import pathlib

from metapkg import packages
from metapkg import targets


source = pathlib.Path(__file__).parent.resolve() / "rust"


class PyEntryPoint(packages.BundledRustPackage):
    title = "pyentrypoint"
    name = "pyentrypoint"
    sources = [
        {
            "url": f"file://{source}",
        },
    ]

    def get_package_layout(
        self, build: targets.Build
    ) -> packages.PackageFileLayout:
        return packages.PackageFileLayout.SINGLE_BINARY
