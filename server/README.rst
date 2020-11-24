==============
Upload Servers
==============

There are three: apt, RPM, and a generic package container with .jsonindexes.

They are Docker containers that accept new files and process the relevant
S3 bucket to serve the updated database.

Generic package is not much more than an FTP server but apt and RPM are
databases with their own package listings, indexes, and encoded file
locations.

To test locally::

    $ docker build -t ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-2.amazonaws.com/genrepo:latest containers/genrepo
    $ docker run -it --env-file=.env --rm -p 2222:22 --name=genrepo ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-2.amazonaws.com/genrepo:latest

To upload a new package::

    $ aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-2.amazonaws.com
    $ docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-2.amazonaws.com/genrepo:latest

To kick the server to upgrade using the new uploaded package::

    $ edbcloud fargate edgedbeng pkg-genrepo --force

(without --force it edbcloud assumes that nothing changed)

Analogic actions for aptrepo and rpmrepo, just replace "genrepo" in the
commands above with the respective repository name.
