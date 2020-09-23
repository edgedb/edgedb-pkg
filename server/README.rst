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
