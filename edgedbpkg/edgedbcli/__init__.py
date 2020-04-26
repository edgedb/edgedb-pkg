from metapkg import packages


class EdgeDBCLI(packages.BundledRustPackage):

    title = "EdgeDBCLI"
    name = 'edgedb-cli'
    description = 'EdgeDB Command Line Tools'
    license = 'ASL 2.0'
    group = 'Applications/Databases'
    identifier = 'com.edgedb.edgedb-cli'
    url = 'https://edgedb.com/'

    sources = (
        {
            "url": "git+https://github.com/edgedb/edgedb-cli.git",
        },
    )

    def get_package_layout(self, build) -> packages.PackageFileLayout:
        return packages.PackageFileLayout.FLAT
