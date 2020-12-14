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
PACKAGE_NAME_NO_DEV_RE = re.compile(r"([^-]+)((-[^-]+)*)-dev\d+")
CACHE = "Cache-Control:public, no-transform, max-age=315360000"
NO_CACHE = "Cache-Control:no-store, no-cache, private, max-age=0"
ARCHIVE = pathlib.Path("archive")
DIST = pathlib.Path("dist")


if TYPE_CHECKING:
    from mypy_boto3_s3 import service_resource as s3


class Package(TypedDict):
    basename: str  # edgedb-server
    slot: Optional[str]  # 1-alpha6-dev5069
    name: str  # edgedb-server-1-alpha6-dev5069
    version: str  # 1.0a6.dev5069+g0839d6e8
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
        arch, _, _ = arch_subdist.partition('.')

        basename = m.group("basename")
        slot = m.group("slot") or ""

        index["packages"].append(
            Package(
                basename=basename,
                slot=slot.lstrip("-") if slot else None,
                name=f"{basename}{slot}",
                version=m.group("version"),
                revision=m.group("release"),
                architecture=arch,
                installref=obj.key,
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
    for path_str in uploads:
        path = pathlib.Path(path_str)
        if not path.is_file():
            print("File not found:", path)
            continue

        print("Looking at", path)
        # macos-x86_64/edgedb-1-alpha6-dev5081_1.0a6.dev5081+ga0106974_2020092316~nightly.pkg
        try:
            dist = path.parent  # macos-x86_64
            dist_base = arch = ""
            if "-" in str(dist):
                dist_base, arch = str(dist).split("-", 1)
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

                archive_dir = ARCHIVE / pkg_dir
                put(bucket, staging_dir / leaf, archive_dir, cache=True)
                put(bucket, asc_path, archive_dir, cache=True)
                put(bucket, sha256_path, archive_dir, cache=True)

                target_dir = DIST / pkg_dir
                dist_name = f"{basename}{slot}_latest{subdist}{ext}"
                put(bucket, staging_dir / leaf, target_dir, name=dist_name)
                put(bucket, asc_path, target_dir, name=dist_name + ".asc")
                put(
                    bucket, sha256_path, target_dir, name=dist_name + ".sha256"
                )
        finally:
            os.unlink(path)
        print(path)

    for pkg_dir in pkg_directories:
        remove_old(bucket, ARCHIVE / pkg_dir, keep=3, subdist="nightly")
        make_index(bucket, ARCHIVE, pkg_dir)


if __name__ == "__main__":
    main()
