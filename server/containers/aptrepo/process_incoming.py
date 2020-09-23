#!/usr/bin/env python3
from __future__ import annotations
from typing import *

import contextlib
import distutils.version
import hashlib
import json
import os
import pathlib
import re
import subprocess

import boto3
import click

LOCAL_DIR = pathlib.Path("%%REPREPRO_BASE_DIR%%")
PACKAGE_RE = re.compile(
    r"^(?P<basename>\w+(-[a-zA-Z]*)?)"
    r"(?P<slot>-\d+(-(alpha|beta|rc)\d+)?(-dev\d+)?)?"
    r"\w+(?P<version>[^_]*)-(?P<release>[^.]*)"
    r"(?P<ext>.*)?$",
    re.A,
)
CACHE = "Cache-Control:public, no-transform, max-age=315360000"
NO_CACHE = "Cache-Control:no-store, no-cache, private, max-age=0"
REPREPRO_PROCESS = [
    "reprepro",
    "-b",
    str(LOCAL_DIR / "apt"),
    "-v",
    "-v",
    "--waitforlock",
    "100",
    "processincoming",
    "main",
]


if TYPE_CHECKING:
    from mypy_boto3_s3 import service_resource as s3

    class Package(TypedDict):
        basename: str  # edgedb-server
        slot: Optional[str]  # 1-alpha6-dev5069
        name: str  # edgedb-server-1-alpha6-dev5069
        version: str  # 1.0a6.dev5069+g0839d6e8
        revision: str  # 2020091300~nightly
        architecture: str  # x86_64.nightly
        installref: str  # /archive/macos-x86_64.nightly/edgedb-server ... .pkg

    class Packages(TypedDict):
        packages: List[Package]


def gpg_detach_sign(path: pathlib.Path) -> pathlib.Path:
    proc = subprocess.run(["gpg", "--detach-sign", "--armor", str(path)])
    proc.check_returncode()
    asc_path = path.with_suffix(path.suffix + ".asc")
    assert asc_path.exists()
    return asc_path


def sha256(path: pathlib.Path) -> pathlib.Path:
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
    index: Dict[str, List[Tuple[str, str]]] = {}
    for obj in bucket.objects.filter(Prefix=str(prefix)):
        m = PACKAGE_RE.match(obj.key)
        if not m or m.group("ext").endswith((".sha256", ".asc")):
            continue

        if subdist:
            _revision, _, _subdist = m.group("release").rpartition("~")
            if subdist != _subdist:
                continue

        key = f"{m.group('basename')}{m.group('slot')}"
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

        for ver in sorted_versions[keep:]:
            bucket.objects.filter(Prefix=ver[1]).delete()


def make_local_indexes(repository: pathlib.Path) -> None:
    index = Packages(packages=[])

    result = subprocess.run(
        ["reprepro", "-b", str(repository), "dumpreferences"],
        universal_newlines=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    dists: Set[str] = set()

    for line in result.stdout.split("\n"):
        if not line.strip():
            continue

        dist, _, _ = line.partition("|")
        dists.add(dist)

    for dist in dists:
        result = subprocess.run(
            ["reprepro", "-b", str(repository), "list", dist],
            universal_newlines=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        arch = ""
        for line in result.stdout.split("\n"):
            if not line.strip():
                continue

            dist_info, _, pkg = line.partition(":")
            if not dist_info or not pkg:
                continue

            _distname, _component, arch = dist_info.strip().split("|")

        m = PACKAGE_RE.match(pkg)
        if not m:
            continue

        basename = m.group("basename")
        slot = m.group("slot") or ""
        if arch == "amd64":
            arch = "x86_64"

        _name = f"{basename}{slot}"
        _ver = m.group("version")
        _rev = m.group("release")
        index["packages"].append(
            Package(
                basename=basename,
                slot=slot.lstrip("-") if slot else None,
                name=_name,
                version=_ver,
                revision=_rev,
                architecture=arch,
                installref=f"{_name}={_ver}-{_rev}",
            )
        )

        out = repository / ".jsonindexes" / dist
        with out.open("w") as f:
            json.dump(index, f)


def get(
    bucket: s3.Bucket,
    source: pathlib.Path,  # bucket key
    target: pathlib.Path,  # file
    *,
    last_modified: int = 0,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    bucket.download_file(Key=str(source), Filename=str(target))
    if last_modified:
        os.utime(target, times=(last_modified, last_modified))
    print("GET", source)


def delete(bucket: s3.Bucket, key: pathlib.Path) -> None:  # bucket key
    bucket.delete_objects(Delete={"Objects": [{"Key": str(key)}]})
    print("DELETE", key)


def put(
    bucket: s3.Bucket,
    source: Union[pathlib.Path, bytes],  # file or data
    target: pathlib.Path,  # bucket key
    *,
    cache: bool = False,
) -> s3.Object:
    ctx: ContextManager

    if isinstance(source, pathlib.Path):
        ctx = open(source, "rb")
    else:
        ctx = contextlib.nullcontext(source)

    with ctx as body:
        result = bucket.put_object(
            Key=str(target),
            Body=body,
            CacheControl=CACHE if cache else NO_CACHE,
            ACL="public-read",
        )
    print("PUT", result)
    return result


def sync_from_remote(local_root: pathlib.Path, bucket: s3.Bucket) -> None:
    """Copy files from S3 to local.

    If a file only exists locally, it's deleted.
    """
    s3_last_modified: Dict[str, int] = {}  # expressed in Unixtime seconds
    s3_size: Dict[str, int] = {}  # expressed in bytes
    for item in bucket.objects.filter(Prefix="apt/"):
        s3_last_modified[item.key] = int(item.last_modified.timestamp())
        s3_size[item.key] = item.size
    local_only: Set[str] = set()

    # Everything left in s3_size after this loop is supposed to be downloaded
    # from S3.
    for entry in recursive_scandir(local_root):
        if not entry.is_file():
            continue

        n = str(pathlib.Path(entry.path).relative_to(local_root))
        if n not in s3_size:
            local_only.add(n)
            continue

        stat = entry.stat()
        if s3_size[n] == stat.st_size and s3_last_modified[n] == stat.st_mtime:
            del s3_size[n]
            del s3_last_modified[n]

    for name, last_modified in sorted(s3_last_modified.items()):
        get(
            bucket,
            pathlib.Path(name),
            local_root / name,
            last_modified=last_modified,
        )

    for name in local_only:
        p = pathlib.Path(name)
        print("RM", p)
        p.unlink()
        with contextlib.suppress(OSError):
            p.parent.rmdir()
            print("RMDIR", p.parent)


def sync_from_local(local_root: pathlib.Path, bucket: s3.Bucket) -> None:
    """Copy files from local to S3.

    If a file only exists on S3, it's deleted.
    """
    s3_last_modified: Dict[str, int] = {}  # expressed in Unixtime seconds
    s3_size: Dict[str, int] = {}  # expressed in bytes
    for item in bucket.objects.filter(Prefix="apt/"):
        s3_last_modified[item.key] = int(item.last_modified.timestamp())
        s3_size[item.key] = item.size
    upload_from_local: Set[str] = set()

    # Everything left in s3_size after this loop is only present on S3 and
    # should be deleted.
    for entry in recursive_scandir(local_root):
        if not entry.is_file():
            continue

        n = str(pathlib.Path(entry.path).relative_to(local_root))
        if n not in s3_size:
            upload_from_local.add(n)
            continue

        stat = entry.stat()
        if s3_size[n] != stat.st_size or s3_last_modified[n] != stat.st_mtime:
            upload_from_local.add(n)

        del s3_size[n]
        del s3_last_modified[n]

    for name in upload_from_local:
        cache = name.startswith("apt/pool/")
        put(
            bucket, local_root / name, pathlib.Path(name), cache=cache,
        )

    for name in sorted(s3_size):
        delete(bucket, pathlib.Path(name))


def recursive_scandir(path: Union[str, pathlib.Path]) -> Iterator[os.DirEntry]:
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from recursive_scandir(entry.path)
        else:
            yield entry


def run_reprepro(listing: pathlib.Path) -> None:
    subprocess.run(REPREPRO_PROCESS + [str(listing)], check=True)


@click.command()
@click.argument("upload_listing")  # a single file with a listing of many files
def main(upload_listing: str) -> None:
    region = os.environ.get("AWS_REGION", "us-east-2")
    session = boto3.session.Session(region_name=region)
    s3 = session.resource("s3")
    bucket = s3.Bucket("edgedb-packages")
    # Note: we're not using a temporary directory because the sync is too big.
    sync_from_remote(LOCAL_DIR, bucket)
    run_reprepro(pathlib.Path(upload_listing))
    make_local_indexes(LOCAL_DIR / "apt")
    sync_from_local(LOCAL_DIR, bucket)


if __name__ == "__main__":
    main()
