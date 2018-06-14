from setuptools import setup


setup(
    setup_requires=[
        'setuptools_scm',
    ],
    use_scm_version=True,
    name='edgedb-pkg',
    description='EdgeDB Meta Package',
    author='MagicStack Inc.',
    author_email='hello@magic.io',
    packages=['edgedbpkg'],
    include_package_data=True,
    install_requires=[
        'metapkg'
    ],
    entry_points={
        'edbsre.services': ['pub-packages=edgedbpkg._sre:PubPackagesService']
    }
)
