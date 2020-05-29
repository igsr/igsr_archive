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

This codebase requires Python (3.6.0 or later) and is used to, among other things, interact programmatically
with the FIle REplication (FIRE) archive implemented in the EMBL-EBI.

1 ) clone this repo::

   git clone https://github.com/igsr/igsr_archive.git

2 ) cd into directory where repo has been cloned::

   cd igsr_archive

3 ) Finally::

   pip install -e .

And you	are ready to go!

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
 [ftp]
 staging_mount=/nfs/1000g-work/G1K/archive_staging/ftp
 ftp_mount=/nfs/1000g-archive

Where the ``[mysql_conn]`` section contains the parameters for connecting the MYSQL server containing the database
created with the `RESEQTRACK <https://github.com/EMBL-EBI-GCA/reseqtrack/tree/master/sql>`_ schema and the ``[fire]``
section contains the FIRE API connection details. If you still do not have a FIRE user and password you
will need to contact ``fire@ebi.ac.uk`` first to get them as these are needed for connecting the
FIRE API. The ``[ftp]`` section contains the staging area directory (see below why this area is important) and also
the directory where the FTP server is mounted.

**Note:** FIRE provides a testing and a production environment. Each will differ in the ``user``, ``root_endpoint`` and ``password``
used for connecting the API. Modify ``settings.ini`` depending on the environment you want to use.

Load files
----------
This section describes how to load a certain file/s in the ``RESEQTRACK`` database. For this, we need
to use the script named ``load_files.py`` as follows.

1) Load a single file

For this, use the ``-f``/``--file`` option like this::

 load_files.py --settings settings.ini --file /path/to/file.txt --type TEST_F --dbname $DBNAME --pwd $PWD


- ``--type`` will be the type assigned to the file that will be loaded in the database. i.e. ``FASTQ`` or ``CRAM``
- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--pwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the file will not be loaded into the database. You need to run
``load_files.py`` with the option ``--dry False`` to load it.

**Note:** md5 checksum will be calculated for the file and the new entry in the ``file`` table of the database
will contain this md5 checksum

2) Load a list of files

You can provide the script a list of files (one file per line) to be loaded. For this use the
``-l``/``--list_file`` option::

 load_files.py --settings settings.ini --list_file file_list.txt --type TEST_F --dbname $DBNAME --pwd $PWD

- ``--type`` will be the type assigned to each of the files that will be loaded in the database. i.e. ``FASTQ`` or ``CRAM``
- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--pwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the files will not be loaded into the database. You need to run
``load_files.py`` with the option ``--dry False`` to load them.

**Note:** md5 checksum will be calculated for each file and these md5 checksums will be loaded in the file
table of the database

3) Load a list of files with precalculated md5 checksums

For this use the ``--md5_file`` option with a file with the following format::

 <md5>\t<path_to_file>


Each of the lines in the file will contain the precalculated md5 checksum and the path of the file to be
loaded. An example command line using this option is::

  load_files.py --settings settings.ini --md5_file file_list.txt --type TEST_F --dbname $DBNAME --pwd $PWD

- ``--type`` will be the type assigned to each of the files that will be loaded in the database. i.e. ``FASTQ`` or ``CRAM``
- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--pwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the files will not be loaded into the database. You need to run
``load_files.py`` with the option ``--dry False`` to load them.

Errors
^^^^^^
1) When you are trying to load a file in the database you can get an error
like the following::

   AssertionError: A file with the name '$FILE' already exists in the DB. You need
    to change name '$FILE' so it is unique.

This error indicates that there is already a file entry in the database with either the same basename or path and this
is why the script can't continue. You can deactivate this check by passing the option ``--unique False``

Delete files
------------
The script for removing an entry in the ``file`` table of the ``RESEQTRACK`` database is ``delete_files.py``.

1) Delete a single file

You can use it as follows::

  delete_files.py --settings settings.ini -f /path/to/file.txt --dbname $DBNAME --pwd $PWD

- ``-f /path/to/file.txt`` is the path of the file to be deleted
- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--pwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the file will not be removed from the database. You need to run
``delete_files.py`` with the option ``--dry False`` to remove it.

2) Remove a list of files

You can provide the script a list of files (one file per line) to be removed. For this use the
``-l``/``--list_file`` option::

 delete_files.py --settings settings.ini --list_file file_list.txt --dbname $DBNAME --pwd $PWD

- ``--list_file file_list.txt`` is the file containing the file paths to be removed
- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--pwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the files will not be removed from the database. You need to run
``delete_files.py`` with the option ``--dry False`` to remove them.

Archive files
-------------
The script for interacting with the FIle REplication (FIRE) archive is named ``archive_files.py``.
This script can be used for archiving files in the public IGSR FTP. Once a certain file is archived using
this script, it will be accessible from our IGSR public FTP at http://ftp.1000genomes.ebi.ac.uk/vol1/

Prerequisites
^^^^^^^^^^^^^
* The file/s to be archived in the FTP need to be tracked in the ``file`` table of the ``RESEQTRACK`` database. For this you need to
  load them first using the ``load_files.py`` script explained in the previous section
* The file/s to be archived in the FTP need to be in the staging area (``/nfs/1000g-work/G1K/archive_staging/ftp``).
  This area can be changed by modifying the ``staging_mount`` parameter of the ``[ftp]`` section in the ``settings.ini`` file

**Note:** The path of the file to be archived within the staging area will be duplicated in the FTP. So for example, if
we want to archive ``test.txt`` so it can accessed from ``http://ftp.1000genomes.ebi.ac.uk/vol1/test_dir/subtest_dir/test.txt``
we need to put ``test.txt`` in ``/nfs/1000g-work/G1K/archive_staging/ftp/test_dir/subtest_dir/``

1) Archive a single file

For this, use the ``-f``/``--file`` option like this::

 archive_files.py --settings settings.ini -f /nfs/1000g-work/G1K/archive_staging/ftp/file.txt --dbname $DBNAME
 --firepwd $FIREPWD --dbpwd $DBPWD

- ``-f/--file`` is the path to the file that will be archived. It needs to exist in the ``file`` table of the ``RESEQTRACK`` database
- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--firepwd`` is the password for connecting the FIRE API
- ``--dbpwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the file will not be archived in the FTP. You need to run
``archive_files.py`` with the option ``--dry False`` to archive them.

**Note:** Use the ``--type`` option if you want to update the ``type`` column from the ``file`` table of the ``RESEQTRACK``
database for the archived file. If you do not specify a type then it will preserve the type that was present previously.

2) Archive a list of files

You can provide the script a list of files (one file per line) to be archived. This list needs to have the format::

  archive_files.py --settings settings.ini --list_file file_list.txt --dbname $DBNAME --firepwd $FIREPWD --dbpwd $DBPWD

- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--firepwd`` is the password for connecting the FIRE API
- ``--dbpwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the files will not be archived in the FTP. You need to run
``archive_files.py`` with the option ``--dry False`` to archive them.

**Note:** Use the ``--type`` option if you want to update the ``type`` column from the ``file`` table of the ``RESEQTRACK``
database for the archived files. If you do not specify a type then it will preserve the type that was present
previously.

Errors
^^^^^^
1) When you are trying to archive a ``/path/to/test.txt`` file in FIRE you can get
the following::

 AssertionError: File entry with path /path/to/test.txt does not exist in the DB. You need to load it first in order
  to proceed

This means that the file is not tracked in the RESEQTRACK database, you need to load it first using the ``load_files.py``
script

Dearchive files
---------------
The script for dearchiving (i.e. removing) a file or a list of files from our public FTP is called ``dearchive_files.py``.
This script will download the file to be dearchived to a desired location before dearchiving from FIRE and will also
delete the entry in the ``file`` table from the ``RESEQTRACK`` database.

1) Dearchive a single file

Enter the following command::

 dearchive_files.py --settings settings.ini --file /nfs/1000g-archive/path/file --directory /dir/to/put/file --dbname $DBNAME \
 --firepwd $FIREPWD --dbpwd $DBPWD

- ``--file`` is the path to the file to be dearchived. ``/nfs/1000g-archive`` is the directory containing the IGSR FTP in our filesystem.
  This directory can be changed by modifying the ``ftp_mount`` parameter of the ``ftp`` section in the ``settings.ini`` file
- ``--directory`` is the directory used to store the file to be dearchived
- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--firepwd`` is the password for connecting the FIRE API
- ``--dbpwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the file will not be dearchived from the FTP. You need to run
``dearchive_files.py`` with the option ``--dry False`` to dearchive it.

2) Dearchive a list of files

You can provide the script a list of files (one file per line) to be dearchived. For this use the
``-l``/``--list_file`` option::

 dearchive_files.py --settings settings.ini --list_file file_list.txt --directory /dir/to/put/file --dbname $DBNAME \
 --firepwd $FIREPWD --dbpwd $DBPWD

- ``--list_file`` is the list of files to be dearchived
- ``--directory`` is the directory used to store the files to be dearchived
- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--firepwd`` is the password for connecting the FIRE API
- ``--dbpwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the files will not be dearchived from the FTP. You need to run
``dearchive_files.py`` with the option ``--dry False`` to dearchive them.

Move files
----------
The script for moving a file/s from one directory in the IGSR public FTP to a different directory is ``move_files.py``.
Also, this script will update the path metadata in the ``RESEQTRACK`` database for the file that wants to be moved.

1) Move a single file

For this, use the ``--origin`` and ``--dest`` options like this::

 move_files.py --settings settings.ini --origin /nfs/1000g-archive/dir1/test.txt --dest /nfs/1000g-archive/dir2/test.txt \
  --dbname $DBNAME --firepwd $FIREPWD --dbpwd $DBPWD

- ``--origin`` is the current path in the FTP filesystem that has the file you want to move
- ``--dest`` is the desired path to which the file will be moved
- ``--dbname`` is the name of the MYSQL ``RESEQTRACK`` database
- ``--firepwd`` is the password for connecting the FIRE API
- ``--dbpwd`` is the password for connecting the MYSQL server

By default, the script will perform a dry run and the file will not be moved. You need to run
``move_files.py`` with the option ``--dry False`` to move it.

2) Move a list of files

You can provide the script a list of the files to be moved. This can be done by creating a 2-columns file::

 <origin>\t<dest>

Where, for each line, the first column will contain the current path in the FTP filesystem that has the file you want to move
and the second column is the desired path to which the file will be moved.

The script will be run by doing::

 move_files.py --settings settings.ini --list_file file_list.txt --dbname $DBNAME --firepwd $FIREPWD --dbpwd $DBPWD

By default, the script will perform a dry run and the files will not be moved. You need to run
``move_files.py`` with the option ``--dry False`` to move them.

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
