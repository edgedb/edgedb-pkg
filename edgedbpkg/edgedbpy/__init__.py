from metapkg import packages


class EdgeDBPython(packages.BundledPythonPackage):

    title = "Python driver for EdgeDB"
    name = 'edgedb'
    license = 'ASL 2.0'
    group = 'Applications/Databases'
    url = 'https://edgedb.com/'

    sources = (
        "git+https://github.com/edgedb/edgedb-python.git",
    )
