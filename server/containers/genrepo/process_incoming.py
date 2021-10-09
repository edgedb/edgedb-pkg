#!/usr/bin/env python3
from __future__ import annotations
from typing import *
from typing_extensions import TypedDict

import contextlib
import distutils.version
import hashlib
import json
import os
import mimetypes
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import boto3
import click


INCOMING_DIR = "%%REPO_INCOMING_DIR%%"
LOCAL_DIR = "%%REPO_LOCAL_DIR%%"
# like:
# edgedb-server-1-alpha6-dev5085_1.0a6.dev5085+g115f9591_2020092500~nightly.pkg.sha256
PACKAGE_RE = re.compile(
    r"^(?P<basename>\w+(-[a-zA-Z]+)*)"
    r"(?P<slot>-\d+(-(alpha|beta|rc)\d+)?(-dev\d+)?)?"
    r"_(?P<version>[^_]*)_(?P<release>[^.]*)"
    r"(?P<ext>.*)?$",
    re.A,
)

VERSION_PATTERN = re.compile(
    r"""^
    (?P<release>[0-9]+(?:\.[0-9]+)*)
    (?P<pre>
        [-]?
        (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
        [\.]?
        (?P<pre_n>[0-9]+)?
    )?
    (?P<dev>
        [\.]?
        (?P<dev_l>dev)
        [\.]?
        (?P<dev_n>[0-9]+)?
    )?
    (?:\+(?P<local>[a-z0-9]+(?:[\.][a-z0-9]+)*))?
    $""",
    re.X | re.A,
)

PACKAGE_NAME_NO_DEV_RE = re.compile(r"([^-]+)((-[^-]+)*)-dev\d+")
CACHE = "Cache-Control:public, no-transform, max-age=315360000"
NO_CACHE = "Cache-Control:no-store, no-cache, private, max-age=0"
ARCHIVE = pathlib.Path("archive")
DIST = pathlib.Path("dist")


if TYPE_CHECKING:
    from mypy_boto3_s3 import service_resource as s3


class Version(TypedDict):

    major: int
    minor: int
    patch: int
    prerelease: Tuple[str, ...]
    metadata: Tuple[str, ...]


class Package(TypedDict):
    basename: str  # edgedb-server
    slot: Optional[str]  # 1-alpha6-dev5069
    name: str  # edgedb-server-1-alpha6-dev5069
    version: str  # 1.0a6.dev5069+g0839d6e8
    parsed_version: Version
    version_key: str  # 1.0.0~alpha.6~dev.5069.2020091300~nightly
    revision: str  # 2020091300~nightly
    architecture: str  # x86_64
    installref: str  # /archive/macos-x86_64.nightly/edgedb-server ... .pkg


class Packages(TypedDict):
    packages: List[Package]


def gpg_detach_sign(path: pathlib.Path) -> pathlib.Path:
    print("gpg_detach_sign", path)
    proc = subprocess.run(["gpg", "--detach-sign", "--armor", str(path)])
    proc.check_returncode()
    asc_path = path.with_suffix(path.suffix + ".asc")
    assert asc_path.exists()
    return asc_path


def sha256(path: pathlib.Path) -> pathlib.Path:
    print("sha256", path)
    with open(path, "rb") as bf:
        _hash = hashlib.sha256(bf.read())
    out_path = path.with_suffix(path.suffix + ".sha256")
    with open(out_path, "w") as f:
        f.write(_hash.hexdigest())
        f.write("\n")
    return out_path


def parse_version(ver: str) -> Version:
    v = VERSION_PATTERN.match(ver)
    if v is None:
        raise ValueError(f"cannot parse version: {ver}")
    metadata = []
    prerelease: List[str] = []
    if v.group("pre"):
        pre_l = v.group("pre_l")
        if pre_l in {"a", "alpha"}:
            pre_kind = "alpha"
        elif pre_l in {"b", "beta"}:
            pre_kind = "beta"
        elif pre_l in {"c", "rc"}:
            pre_kind = "rc"
        else:
            raise ValueError(f"cannot determine release stage from {ver}")

        prerelease.append(f"{pre_kind}.{v.group('pre_n')}")
        if v.group("dev"):
            prerelease.append(f'dev.{v.group("dev_n")}')

    elif v.group("dev"):
        prerelease.append("alpha.1")
        prerelease.append(f'dev.{v.group("dev_n")}')

    if v.group("local"):
        metadata.extend(v.group("local").split("."))

    release = [int(r) for r in v.group("release").split(".")]

    return Version(
        major=release[0],
        minor=release[1],
        patch=release[2] if len(release) == 3 else 0,
        prerelease=tuple(prerelease),
        metadata=tuple(metadata),
    )


def format_version_key(ver: Version, revision: str) -> str:
    ver_key = f'{ver["major"]}.{ver["minor"]}.{ver["patch"]}'
    if ver["prerelease"]:
        # Using tilde for "dev" makes it sort _before_ the equivalent
        # version without "dev" when using the GNU version sort (sort -V)
        # or debian version comparison algorithm.
        prerelease = (
            ("~" if pre.startswith("dev.") else ".") + pre
            for pre in ver["prerelease"]
        )
        ver_key += "~" + "".join(prerelease).lstrip(".~")
    if revision:
        ver_key += f".{revision}"
    return ver_key


def remove_old(
    bucket: s3.Bucket, prefix: pathlib.Path, keep: int, subdist: str = ""
) -> None:
    print("remove_old", bucket, prefix, keep, subdist)
    index: Dict[str, List[Tuple[str, str]]] = {}
    prefix_str = str(prefix) + "/"
    for obj in bucket.objects.filter(Prefix=prefix_str):
        obj_key_no_prefix = pathlib.Path(obj.key).name
        m = PACKAGE_RE.match(obj_key_no_prefix)
        if not m:
            print(obj_key_no_prefix, "doesn't match PACKAGE_RE")
            continue

        if m.group("ext").endswith((".sha256", ".asc")):
            print(obj.key, "is a hash")
            continue

        if subdist:
            _revision, _, _subdist = m.group("release").rpartition("~")
            if subdist != _subdist:
                continue

        key_with_dev = f"{m.group('basename')}{m.group('slot') or ''}"
        key = PACKAGE_NAME_NO_DEV_RE.sub(r"\1\2", key_with_dev)

        version = f"{m.group('version')}_{m.group('release')}"
        index.setdefault(key, []).append((version, obj.key))

    for _, versions in index.items():
        sorted_versions = list(
            sorted(
                versions,
                key=lambda v: distutils.version.LooseVersion(v[0]),
                reverse=True,
            )
        )

        for _ver, obj_key in sorted_versions[keep:]:
            print("Deleting outdated", obj_key)
            bucket.objects.filter(Prefix=obj_key).delete()


def make_index(bucket: s3.Bucket, prefix: pathlib.Path, pkg_dir: str) -> None:
    print("make_index", bucket, prefix, pkg_dir)
    index = Packages(packages=[])
    for obj in bucket.objects.filter(Prefix=str(prefix / pkg_dir)):
        path = pathlib.Path(obj.key)
        leaf = path.name

        if path.parent.name != pkg_dir:
            print(leaf, "wrong dist")
            continue

        m = PACKAGE_RE.match(leaf)
        if not m:
            print(leaf, "doesn't match PACKAGE_RE")
            continue

        if m.group("ext").endswith((".sha256", ".asc")):
            print(leaf, "is a hash")
            continue

        if "-" not in path.parent.name:
            print(f"cannot parse: {obj.key}", file=sys.stderr)
            return

        dist, _, arch_subdist = path.parent.name.rpartition("-")
        arch, _, _ = arch_subdist.partition(".")

        basename = m.group("basename")
        slot = m.group("slot") or ""
        installref = obj.key
        if not installref.startswith("/"):
            installref = f"/{installref}"

        parsed_ver = parse_version(m.group("version"))

        index["packages"].append(
            Package(
                basename=basename,
                slot=slot.lstrip("-") if slot else None,
                name=f"{basename}{slot}",
                version=m.group("version"),
                parsed_version=parsed_ver,
                version_key=format_version_key(parsed_ver, m.group("release")),
                revision=m.group("release"),
                architecture=arch,
                installref=installref,
            )
        )

    source_bytes = json.dumps(index).encode("utf8")
    target_dir = prefix / ".jsonindexes"
    index_name = pkg_dir + ".json"
    put(bucket, source_bytes, target_dir, name=index_name)


def put(
    bucket: s3.Bucket,
    source: Union[pathlib.Path, bytes],
    target: pathlib.Path,  # directory
    *,
    name: str = "",
    cache: bool = False,
    content_type: str = "",
) -> s3.Object:
    ctx: ContextManager

    if isinstance(source, pathlib.Path):
        ctx = open(source, "rb")
        name = name or source.name
    elif not name:
        raise ValueError(f"Name not given for target {target}")
    else:
        ctx = contextlib.nullcontext(source)

    if not content_type:
        ct, enc = mimetypes.guess_type(name)
        if ct is not None and "/" in ct:
            content_type = ct
    print("put", name, bucket, target)
    with ctx as body:
        result = bucket.put_object(
            Key=str(target / name),
            Body=body,
            CacheControl=CACHE if cache else NO_CACHE,
            ContentType=content_type,
            ACL="public-read",
        )
    print(result)
    return result


@click.command()
@click.argument("upload_listing")  # a single file with a listing of many files
def main(upload_listing: str) -> None:
    os.chdir(INCOMING_DIR)
    with open(upload_listing) as upload_listing_file:
        uploads = upload_listing_file.read().splitlines()
    os.unlink(upload_listing)
    region = os.environ.get("AWS_REGION", "us-east-2")
    session = boto3.session.Session(region_name=region)
    s3 = session.resource("s3")
    bucket = s3.Bucket("edgedb-packages")
    pkg_directories = set()
    rrules = {}
    for path_str in uploads:
        path = pathlib.Path(path_str)
        if not path.is_file():
            print("File not found:", path)
            continue
        if path.name == "package-version.json":
            print("Skipping package-version.json")
            continue

        print("Looking at", path)
        # macos-x86_64/edgedb-1-alpha6-dev5081_1.0a6.dev5081+ga0106974_2020092316~nightly.pkg
        try:
            dist = path.parent  # macos-x86_64
            leaf = path.name
            m = PACKAGE_RE.match(leaf)
            if not m:
                raise click.ClickException(
                    f"Cannot parse artifact filename: {path_str}"
                )
            basename = m.group("basename")
            slot = m.group("slot") or ""
            subdist = m.group("release")
            subdist = re.sub(r"[0-9]+", "", subdist)
            subdist = subdist.replace("~", "_")
            pkg_dir = str(dist) + subdist.replace("_", ".")
            pkg_directories.add(pkg_dir)
            ext = m.group("ext")
            print(f"dist={dist} leaf={leaf}")
            print(f"basename={basename} slot={slot}")
            print(f"subdist={subdist} pkg_dir={pkg_dir}")
            print(f"ext={ext}")
            with tempfile.TemporaryDirectory(
                prefix="genrepo", dir=LOCAL_DIR
            ) as temp_dir:
                staging_dir = pathlib.Path(temp_dir) / pkg_dir
                os.makedirs(staging_dir)
                shutil.copy(path_str, staging_dir)
                asc_path = gpg_detach_sign(staging_dir / leaf)
                sha256_path = sha256(staging_dir / leaf)

                # Store the fully-qualified artifact to archive/
                archive_dir = ARCHIVE / pkg_dir
                put(bucket, staging_dir / leaf, archive_dir, cache=True)
                put(bucket, asc_path, archive_dir, cache=True)
                put(bucket, sha256_path, archive_dir, cache=True)

                # And record a copy of it in the dist/ directory
                # as an unversioned "*_latest" key for ease of reference
                # in download scripts.  Note: the archive/ entry is cached,
                # but the dist/ entry MUST NOT be cached for obvious reasons.
                # However, we still want the benefit of CDN for it, so we
                # generate a bucket-wide redirect policy for the dist/ object
                # to point to the archive/ object.  See below for details.
                target_dir = DIST / pkg_dir
                dist_name = f"{basename}{slot}_latest{subdist}{ext}"
                put(bucket, staging_dir / leaf, target_dir, name=dist_name)

                asc_name = f"{dist_name}.asc"
                put(bucket, asc_path, target_dir, name=asc_name)

                sha_name = f"{dist_name}.sha256"
                put(bucket, sha256_path, target_dir, name=sha_name)

                rrules[target_dir / dist_name] = archive_dir / leaf
        finally:
            os.unlink(path)
        print(path)

    for pkg_dir in pkg_directories:
        remove_old(bucket, ARCHIVE / pkg_dir, keep=3, subdist="nightly")
        make_index(bucket, ARCHIVE, pkg_dir)

    if rrules:
        # We can't use per-object redirects, because in that case S3
        # generates the `301 Moved Permanently` response, and, adding
        # insult to injury, forgets to send the `Cache-Control` header,
        # which makes the response cacheable and useless for the purpose.
        # Luckily the "website" functionality of the bucket allows setting
        # redirection rules centrally, so that's what we do.
        #
        # The redirection rules are key prefix-based, and so we can use just
        # one redirect rule to handle both the main artifact and its
        # accompanying signature and checksum files.
        #
        # NOTE: Amazon S3 has a limitation of 50 routing rules per
        #       website configuration.
        website = s3.BucketWebsite("edgedb-packages")
        existing_rrules = list(website.routing_rules)
        for src, tgt in rrules.items():
            src_key = str(src)
            tgt_key = str(tgt)
            for rule in existing_rrules:
                condition = rule.get("Condition")
                if not condition:
                    continue
                if condition.get("KeyPrefixEquals") == src_key:
                    try:
                        redirect = rule["Redirect"]
                    except KeyError:
                        redirect = rule["Redirect"] = {}

                    redirect["ReplaceKeyPrefixWith"] = tgt_key
                    redirect["HttpRedirectCode"] = "307"
                    break
            else:
                existing_rrules.append(
                    {
                        "Condition": {
                            "KeyPrefixEquals": src_key,
                        },
                        "Redirect": {
                            "HttpRedirectCode": "307",
                            "Protocol": "https",
                            "HostName": "packages.edgedb.com",
                            "ReplaceKeyPrefixWith": tgt_key,
                        },
                    }
                )

        website_config = {
            "RoutingRules": existing_rrules,
        }

        if website.error_document is not None:
            website_config["ErrorDocument"] = website.error_document

        if website.index_document is not None:
            website_config["IndexDocument"] = website.index_document

        if website.redirect_all_requests_to is not None:
            website_config[
                "RedirectAllRequestsTo"
            ] = website.redirect_all_requests_to

        print("updating bucket website config:", website_config)
        website.put(WebsiteConfiguration=website_config)


if __name__ == "__main__":
    main()
