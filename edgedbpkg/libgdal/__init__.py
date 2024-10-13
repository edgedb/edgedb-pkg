from __future__ import annotations

from metapkg import packages
from metapkg import targets

from edgedbpkg import (
    libexpat,
    libgeos,
    libjson_c,
    libpcre2,
    libxml2,
    libtiff,
    libgeotiff,
    libproj,
    libsqlite3,
    openssl,
    zlib,
)


class LibGDAL(packages.BundledCMakePackage):
    title = "libgdal"
    ident = "libgdal"
    aliases = ["libgdal-dev"]

    _server = "https://download.osgeo.org/gdal/"

    sources = [
        {
            "url": _server + "{version}/gdal-{version}.tar.gz",
        },
    ]

    artifact_requirements = [
        "libexpat",
        "libgeos (>=3.8.0)",
        "libjson-c (>=0.13)",
        "libpcre2",
        "libxml2",
        "libgeotiff (>=1.5.1)",
        "libproj (>=6.3.1)",
        "libsqlite3",
        "libtiff (>=4.1.0)",
        "openssl",
        "zlib",
    ]

    artifact_build_requirements = [
        "libexpat-dev",
        "libgeos-dev (>=3.8.0)",
        "libjson-c-dev (>=0.13)",
        "libpcre2-dev",
        "libxml2-dev",
        "libtiff-dev (>=4.1.0)",
        "libgeotiff-dev (>=1.5.1)",
        "libproj-dev (>=6.3.1)",
        "libsqlite3-dev",
        "openssl-dev",
        "zlib-dev",
    ]

    bundle_deps = [
        libexpat.LibExpat("2.6.3"),
        libgeos.LibGEOS("3.13.0"),
        libjson_c.LibJsonC("0.17"),
        libpcre2.LibPCRE2("10.44"),
        libxml2.LibXML2("2.13.4"),
        libgeotiff.LibGeoTIFF("1.7.3"),
        libproj.LibProj("9.5.0"),
        libsqlite3.LibSQLite3("3.46.1"),
        libtiff.LibTIFF("4.7.0"),
        openssl.OpenSSL("3.3.1"),
        zlib.Zlib("1.3.1"),
    ]

    @classmethod
    def get_dep_pkg_name(cls) -> str:
        """Name used by pkg-config or CMake to refer to this package."""
        return "GDAL"

    def get_dep_pkg_config_script(self) -> str | None:
        return "gdal-config"

    def get_configure_args(
        self,
        build: targets.Build,
        wd: str | None = None,
    ) -> packages.Args:
        return super().get_configure_args(build, wd=wd) | {
            "-DENABLE_IPO": "OFF",
            "-DGDAL_USE_EXTERNAL_LIBS": "ON",
            "-DGDAL_USE_INTERNAL_LIBS": "OFF",
            "-DBUILD_TESTING": "OFF",
            "-DGDAL_USE_ARMADILLO": "OFF",
            "-DGDAL_USE_ARROW": "OFF",
            "-DGDAL_USE_BLOSC": "OFF",
            "-DGDAL_USE_BRUNSLI": "OFF",
            "-DGDAL_USE_CRNLIB": "OFF",
            "-DGDAL_USE_CFITSIO": "OFF",
            "-DGDAL_USE_CURL": "OFF",
            "-DGDAL_USE_CRYPTOPP": "OFF",
            "-DGDAL_USE_DEFLATE": "OFF",
            "-DGDAL_USE_ECW": "OFF",
            "-DGDAL_USE_EXPAT": "ON",
            "-DGDAL_USE_FILEGDB": "OFF",
            "-DGDAL_USE_FREEXL": "OFF",
            "-DGDAL_USE_FYBA": "OFF",
            "-DGDAL_USE_GEOTIFF": "ON",
            "-DGDAL_USE_GEOS": "ON",
            "-DGDAL_USE_GIF": "OFF",
            "-DGDAL_USE_GTA": "OFF",
            "-DGDAL_USE_HEIF": "OFF",
            "-DGDAL_USE_HDF4": "OFF",
            "-DGDAL_USE_HDF5": "OFF",
            "-DGDAL_USE_HDFS": "OFF",
            "-DGDAL_USE_ICONV": "ON",
            "-DGDAL_USE_IDB": "OFF",
            "-DGDAL_USE_JPEG": "OFF",
            "-DGDAL_USE_JPEG12_INTERNAL": "ON",
            "-DGDAL_USE_JSONC": "ON",
            "-DGDAL_USE_JXL": "OFF",
            "-DGDAL_USE_KDU": "OFF",
            "-DGDAL_USE_KEA": "OFF",
            "-DGDAL_USE_LERC": "OFF",
            "-DGDAL_USE_LIBKML": "OFF",
            "-DGDAL_USE_LIBLZMA": "OFF",
            "-DGDAL_USE_LIBXML2": "ON",
            "-DGDAL_USE_LURATECH": "OFF",
            "-DGDAL_USE_LZ4": "OFF",
            "-DGDAL_USE_MONGOCXX": "OFF",
            "-DGDAL_USE_MRSID": "OFF",
            "-DGDAL_USE_MSSQL_NCLI": "OFF",
            "-DGDAL_USE_MSSQL_ODBC": "OFF",
            "-DGDAL_USE_MYSQL": "OFF",
            "-DGDAL_USE_NETCDF": "OFF",
            "-DGDAL_USE_ODBC": "OFF",
            "-DGDAL_USE_ODBCCPP": "OFF",
            "-DGDAL_USE_OGDI": "OFF",
            "-DGDAL_USE_OPENCAD": "OFF",
            "-DGDAL_USE_OPENCL": "OFF",
            "-DGDAL_USE_OPENEXR": "OFF",
            "-DGDAL_USE_OPENJPEG": "OFF",
            "-DGDAL_USE_OPENSSL": "ON",
            "-DGDAL_USE_ORACLE": "OFF",
            "-DGDAL_USE_PARQUET": "OFF",
            "-DGDAL_USE_PCRE2": "ON",
            "-DGDAL_USE_PDFIUM": "OFF",
            "-DGDAL_USE_PNG": "OFF",
            "-DGDAL_USE_PODOFO": "OFF",
            "-DGDAL_USE_POPPLER": "OFF",
            "-DGDAL_USE_POSTGRESQL": "OFF",
            "-DGDAL_USE_QHULL": "OFF",
            "-DGDAL_USE_RASTERLITE2": "OFF",
            "-DGDAL_USE_RDB": "OFF",
            "-DGDAL_USE_SPATIALITE": "OFF",
            "-DGDAL_USE_SQLITE3": "ON",
            "-DGDAL_USE_SFCGAL": "OFF",
            "-DGDAL_USE_TEIGHA": "OFF",
            "-DGDAL_USE_TIFF": "ON",
            "-DGDAL_USE_TILEDB": "OFF",
            "-DGDAL_USE_WEBP": "OFF",
            "-DGDAL_USE_XERCESC": "OFF",
            "-DGDAL_USE_ZLIB": "ON",
            "-DGDAL_USE_ZSTD": "OFF",
            "-DBUILD_PYTHON_BINDINGS": "OFF",
            "-DBUILD_JAVA_BINDINGS": "OFF",
            "-DBUILD_CSHARP_BINDINGS": "OFF",
        }

    def get_shlibs(self, build: targets.Build) -> list[str]:
        return ["gdal"]
