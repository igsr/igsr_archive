.. igsr_archive documentation master file, created by
   sphinx-quickstart on Wed May 20 15:38:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to igsr_archive's documentation!
========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Installation
============

Usage
=====

Settings file
-------------
All scripts explained below require a ``settings.ini`` file containing basic configuration parameters.
Below is the template of a configuration file::

 [mysql_conn]
 host = mysql-g1kdcc-public.ebi.ac.uk
 user = g1krw
 port = 4197
 [fire]
 root_endpoint = http://hh.fire-test.sdo.ebi.ac.uk/fire
 user = g1k-test-ernesto
 version = v1.1

Where the ``[mysql_conn]`` section contains the parameters for connecting the MYSQL server containing the database
created with the `RESEQTRACK <https://github.com/EMBL-EBI-GCA/reseqtrack/tree/master/sql>`_ schema and the ``[fire]``
section contains the FIRE API connection details. If you still do not have a FIRE user and password you
will need to contact ``fire@ebi.ac.uk`` first to get them as these are needed for connecting the
FIRE API

Load files
----------
This section describes how to load a certain file in the ``RESEQTRACK`` database. For this, we need
to use the script named ``load_files.py`` as follows.

1) Load a single file

For this you need to use the ``-f``/``--file`` option like this::

 load_files.py --settings settings.ini --file /path/to/file.txt --type TEST_F --dbname $DBNAME --pwd $PWD


- ``--type`` will be the type assigned to the file that will be loaded in the database. i.e. ``FASTQ`` or ``CRAM``
- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--pwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the file will not be loaded into the database. You need to run
``load_files.py`` with the option ``--dry False`` to load it.

**Note:** md5sum will be calculated for the provided file and the new entry in the ``file`` table of the database
will contain this md5sum

2) Load a list of files

You can provide the script a list of files (one file per line) to be loaded. For this you need to use the
``-l``/``--list_file`` option







Archive files
-------------
The Python script for interacting with the FIle REplication (FIRE) archive is named ``archive_files.py``.
This script can be used for archiving and moving files in FIRE. Once a certain file is archived using this
script, it will be accessible from our IGSR public FTP

Prerequisites
^^^^^^^^^^^^^


1)




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
