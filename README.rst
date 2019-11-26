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
