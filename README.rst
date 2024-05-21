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
by triggering a "Build Test and Publish Nightly Packages" workflow dispatch
from the GitHub UI.  You can choose which branch to fire up a build from.


Release
=======

Triggering a "release" workflow dispatch works just like nightly builds
but you're looking for the "Build Test and Publish a Release" workflow.
Choose a branch like "releases/1.0a6".


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
  significantly increases the build time, but results in slightly faster
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


Adding Targets and Modifying Build
==================================

Adding a target for an existing distribution family usually boils down to
running ``mkdir integration/linux/{build,test,testpublished,upload}/<distro>``,
adding ``<distro>`` to ``SUPPORTED_TARGETS`` in the toplevel ``Makefile``,
and running ``make TARGET=<distro> build`` to generate the containers and
test the build.

Adding support for new distributions requires implementing a new target
in `metapkg <https://github.com/edgedb/metapkg/>`_.


How does uploading work?
========================

The upload stage for GitHub Actions is in linux/upload, macos/publish.sh,
and win/publish.sh.  The server-side code is in server/.
