from __future__ import annotations

from metapkg import packages
from metapkg import targets

from edgedbpkg import libgeos
from edgedbpkg import libgdal
from edgedbpkg import libjson_c
from edgedbpkg import libpcre2
from edgedbpkg import libproj
from edgedbpkg import libprotobuf_c
from edgedbpkg import libxml2
from edgedbpkg import protoc_c

from edgedbpkg import pgext


class PostGIS(pgext.PostgresCExtension):
    title = "postgis extension"
    name = packages.canonicalize_name("pgext-postgis")
    description = "Geographic Objects for PostgreSQL"
    license_id = "GPL-3"
    group = "Applications/Databases"

    _server = "https://download.osgeo.org/postgis/source/"

    sources = [
        {
            "url": _server + "postgis-{version}.tar.gz",
        },
    ]

    artifact_requirements = [
        "libgdal (>=2.0.0)",
        "libgeos (>=3.9.0)",
        "libjson-c",
        "libpcre2-dev",
        "libproj (>=6.1.0)",
        "libprotobuf-c (>=1.1.0)",
        "libxml2",
    ]

    artifact_build_requirements = [
        "postgresql-edgedb (>=13)",
        "libgdal-dev (>=2.0.0)",
        "libgeos-dev (>=3.9.0)",
        "libjson-c-dev",
        "libpcre2-dev",
        "libproj-dev (>=6.1.0)",
        "libprotobuf-c-dev (>=1.1.0)",
        "protoc-c (>=1.1.0)",
        "libxml2-dev",
    ]

    bundle_deps = [
        libgdal.LibGDAL("3.9.2"),
        libgeos.LibGEOS("3.13.0"),
        libjson_c.LibJsonC("0.17"),
        libpcre2.LibPCRE2("10.44"),
        libproj.LibProj("9.5.0"),
        libprotobuf_c.LibProtoBufC("1.5.0"),
        protoc_c.ProtoCompilerC("1.5.0"),
        libxml2.LibXML2("2.13.4"),
    ]

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "--without-gui": None,
            "--with-address-standardizer": None,
        }
