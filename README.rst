================================
EdgeDB Release Packaging Toolkit
================================

Everything specifically related to making EdgeDB packages for all supported
platforms is located in this repo.  The build workflows for packages are
located in the `main EdgeDB repo`_.

.. _main EdgeDB repo: https://github.com/edgedb/edgedb/blob/master/.github/workflows/

SRE bits for packages.edgedb.com is also here.


Nightly Builds
==============

The nightly package builds are performed at 00:00 UTC every day, or on demand
by triggering a "nightly-build" repository dispatch:

.. code-block:: shell

    curl \
        -H "Accept: application/vnd.github.everest-preview+json" \
        -H "Authorization: Bearer <your-github-token>" \
        -H "Content-Type: application/json" \
        --data '{"event_type": "nightly-build"}' \
        https://api.github.com/repos/edgedb/edgedb/dispatches


Building Locally
================

It is possible to execute package build and test stages locally for linux
targets using Docker:

Build Stage
-----------

Build the packages for a given target:

.. code-block:: shell

    make TARGET=<target> build

See the Makefile for the list of supported targets.  The Makefile also
takes the following optional arguments:

* ``SRC_REF``: EdgeDB git ref to build, defaults to ``master``;
* ``PKG_REVISION``: numeric revision of the output package;
* ``PKG_SUBDIST``: name of repository the package is intended for, currently
  the only supported value is ``nightly``;
* ``OUTPUTDIR``: the name of the directory where the build artifacts will
  be stored;
* ``METAPKGDEV``: when set to ``true``, uses metapkg from the current
  virtualenv instead of pulling it from Github, this is useful for debugging
  or making changes to metapkg;
* ``EXTRA_OPTIMIZATIONS``: build with extra optimizations enabled, this
  significantly increases the build time, but results in sligtly faster
  binaries;
* ``GET_SHELL``: when set to ``true``, start the shell instead of running the
  build.

Test Stage
----------

Test the packages built with ``make build``:

.. code-block:: shell

    make TARGET=<target> test

The values of the ``TARGET`` and ``OUTPUTDIR`` variables must be the same
as used for ``make build``.

There is also a test variant that checks systemd integration:

.. code-block:: shell

    make TARGET=<target> test-systemd

Note that this requires the ability to run Docker containers with
``CAP_ADMIN``.
