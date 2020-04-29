#!/bin/sh

sshkey="-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCHoXKafAduDxGw6zUf/FTfLttUHZjtvhux3KJUX6oyVAAAAKA0Nnd6NDZ3
egAAAAtzc2gtZWQyNTUxOQAAACCHoXKafAduDxGw6zUf/FTfLttUHZjtvhux3KJUX6oyVA
AAAEDbnd9kFanb1YaEj8PF8nCxOXsm1xlaECDbQHWsTZKIAYehcpp8B24PEbDrNR/8VN8u
21QdmO2+G7HcolRfqjJUAAAAG2VsdmlzQGhhbW1lci5tYWdpY3N0YWNrLm5ldAEC
-----END OPENSSH PRIVATE KEY-----"

docker run -it --rm -v $(pwd)/artifacts:/artifacts -v ~/dev/magic/metapkg/metapkg:/usr/local/lib/python3.7/site-packages/metapkg2 -v ~/dev/edgedb/edgedb-pkg/edgedbpkg:/usr/local/lib/python3.7/site-packages/edgedbpkg -e PKG_REVISION=20191014 -e PKG_PLATFORM=debian -e PKG_PLATFORM_VERSION=stretch -e PKG_SUBDIST=nightly -e PACKAGE_UPLOAD_SSH_KEY="${sshkey}" containers.magicstack.net/magicstack/edgedb-pkg/upload:debian
