from igsr_archive.file import File

import pymysql
import logging
import datetime
import os
import sys
import pdb

from igsr_archive.config import CONFIG

# create logger
db_logger = logging.getLogger(__name__)

class DB(object):
    """
    Class to represent a Reseqtrack db

    Attributes
    ----------
    conn : Connection object
           Connection to MySQL db.
    pwd : str
          Password used for MySQL server connection.
    dbname : str
            Reseqtrack db name.
    """

    def __init__(self, pwd, dbname):
        """
        Constructor

        Parameters
        ----------
        pwd : str
              Password for API.
        dbname: str
                Reseqtrack db name.
        """

        db_logger.debug('Creating DB object')

        self.pwd = pwd
        self.dbname = dbname
        self.conn = self.set_conn()

    def set_conn(self):
        """
        Function that will set the conn
        class variable

        Returns
        -------
        conn: Connection object
        """

        db_logger.debug('Setting connection...')

        # initialise ConfigParser object with connection
        # settings

        conn = pymysql.connect(host=CONFIG.get('mysql_conn', 'host'),
                               user=CONFIG.get('mysql_conn', 'user'),
                               password=self.pwd,
                               db=self.dbname,
                               port=CONFIG.getint('mysql_conn', 'port'))

        db_logger.debug('Connection successful!')

        return conn

    def load_file(self, f, dry=True):
        """
        Function to load an entry in the
        table 'file' of self.dbname

        Parameters
        ----------
        f : File object
            File that will be stored in this DB.
        dry : bool, default=True
              If True then it will not try to store the file in the DB.

        Returns
        -------
        int
            Return code
                0 : Success
                1 : Error

        Raises
        ------
        pymysql.Error
            If file could not be loaded
        """

        db_logger.info(f"Loading file: {f.name}")
        # construct INSERT INTO sql statement
        sql_insert_attr = f"INSERT INTO file (file_id, name, md5, type, size, host_id, withdrawn, created) " \
                          f"VALUES (NULL, \'{f.name}\', \'{f.md5}\', \'{f.type}\', \'{f.size}\', \'{f.host_id}\', " \
                          f"\'{f.withdrawn}\', \'{f.created}\')"

        if dry is False:
            try:
                cursor = self.conn.cursor()
                # Execute the SQL command
                cursor.execute(sql_insert_attr)
                # Commit your changes in the database
                self.conn.commit()
                db_logger.info(f"File loaded: {f.name}")
                return 0
            except pymysql.Error as e:
                db_logger.error("Exception occurred", exc_info=True)
                # Rollback in case there is any error
                self.conn.rollback()
                return 1
        elif dry is True:
            db_logger.info(f"INSERT sql: {sql_insert_attr}")
            db_logger.info(f"File was not stored in the DB.")
            db_logger.info(f"Use --dry False to effectively store it")
            return 0
        else:
            raise Exception(f"dry option: {dry} not recognized")

    def delete_file(self, f, dry=True):
        """
        Function to delete a certain entry
        from the 'file' table in self.dbname

        Parameters
        ----------
        f : File object
            File to be deleted from the DB.
        dry : bool, default=True
              If dry=True then it will not delete the file
              from the self.dbname.
        
        Returns
        -------
        None

        Raises
        ------
        pymysql.Error
            If there was some kind of error
        """

        db_logger.info(f"Deleting file: {f.name}")

        # construct DELETE sql statement
        delete_sql = f"DELETE from file where name='{f.name}'"

        if dry is False:
            try:
                cursor = self.conn.cursor()
                # Execute the SQL command
                cursor.execute(delete_sql)
                # Commit your changes in the database
                self.conn.commit()
                db_logger.info(f"File deleted")
            except pymysql.Error as e:
                db_logger.error("Exception occurred", exc_info=True)
                # Rollback in case there is any error
                self.conn.rollback()
                sys.exit(1)

        elif dry is True:
            db_logger.info(f"DELETE sql: {delete_sql}")
            db_logger.info(f"File was not deleted from the DB.")
            db_logger.info(f"Use --dry False to effectively delete it")

        else:
            raise Exception(f"dry option: {dry} not recognized")

    def fetch_file(self, path=None, basename=None):
        """
        Function to fetch a certain entry from the table 'file' in
        self.dbname

        Parameters
        ----------
        path : str, optional
               Path of file to be retrieved.
        basename : str, optional
                   Basename of file to be retrieved.

        Returns
        -------
        f : file.file.File or None
            object retrieved from DB
            None if no file was retrieved.
        
        Raises
        ------
        pymysql.Error
        """
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        if path is not None:
            db_logger.debug(f"Fetching file with path: {path}")
            abs_path = os.path.abspath(path)
            query = "SELECT * FROM file WHERE name = %s"
            cursor.execute(query, [abs_path])
        elif basename is not None:
            db_logger.debug(f"Fetching file with basename: {basename}")
            query = "SELECT * FROM file WHERE name like %s"
            cursor.execute(query, ['%' + basename])
        try:
            result_set = cursor.fetchall()
            if not result_set:
                db_logger.debug(f"No file retrieved from DB using using path:{path}")
                return None
            for row in result_set:
                f = File(**row)
                return f
            cursor.close()
            self.conn.commit()
        except pymysql.Error as e:
            db_logger.error("Exception occurred", exc_info=True)
            # Rollback in case there is any error
            self.conn.rollback()

    def fetch_files_by_pattern(self, pattern):
        """
        Function to fetch all files using a certain pattern
        of the 'name' field: i.e. SELECT * FROM file WHERE name like '%PATTERN';

        Parameters
        ----------
        pattern : str
                  Pattern used to find files

        Returns
        -------
        file_list : list of str
                    List with all paths returned by the query
        
        Raises
        ------
        pymysql.Error
        """

        db_logger.debug(f"Fetching all files for pattern: {pattern}")
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        query = "SELECT * FROM file WHERE name like %s"
        cursor.execute(query, [pattern+'%'])
        file_list = []
        try:
            result_set = cursor.fetchall()
            if not result_set:
                db_logger.debug(f"No file retrieved from DB using using pattern:{pattern}")
                return None
            for row in result_set:
                file_list.append(row["name"])
            cursor.close()
            self.conn.commit()
        except pymysql.Error as e:
            db_logger.error("Exception occurred", exc_info=True)
            # Rollback in case there is any error
            self.conn.rollback()

        return file_list

    def get_ctree(self, fields, outfile, limit=None):
        """
        Function to dump DB file records and generate
        a current tree file pointed by outfile.
        This function will also parse each of the records
        in the 'file' table and creates a dict with the following information:
        { 'path' : md5 }

        Parameter
        --------
        fields: list of str
                List with the fields from the 'file' table to
                be dumped. The order of the fields in the dumped
                file will be preserved.
        outfile: str
                 File path for the current.same.tree output.
        limit: int, default = None
               Limit current.same.tree file to this int number of records
               If None then (all records will be dumped).

        Return
        ------
        outfile : str
                  path with current.tree.
        data_dict : dict
                    Dict with md5s
                    { 'path' : md5 }
        """
        assert isinstance(fields, list)

        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        fields_str = ",".join(fields)
        if limit is None:
            query = f"SELECT {fields_str} FROM file"
        else:
            query = f"SELECT {fields_str} FROM file limit {limit}"

        fields.insert(1, "type")

        f = open(outfile, 'w')

        data_dict = {} # dict {'path' : 'md5' }
        cursor.execute(query)
        try:
            result_set = cursor.fetchall()
            if not result_set:
                db_logger.debug(f"No file retrieved from DB using using query:{query}")
                return None
            for row in result_set:
                row["name"] = row["name"].replace(CONFIG.get("ftp","ftp_mount")+"/","")
                if CONFIG.get("ftp","staging_mount") in row["name"]:
                    continue
                # skip files that are in any dir that is not the ftp/ dir,
                # as these files are not included in the current.tree file
                bits = row["name"].split("/")
                if bits[0] != "ftp":
                    continue
                row["type"] = "file"
                data_dict[row["name"]] = row["md5"]
                for k in fields:
                    f.write(f"{row[k]}\t")
                f.write("\n")
            cursor.close()
            self.conn.commit()
        except pymysql.Error as e:
            db_logger.error("Exception occurred", exc_info=True)
            # Rollback in case there is any error
            self.conn.rollback()
        f.close

        return outfile, data_dict

    def update_file(self, attr_name, value, name, dry=True):
        """
        Update a certain attribute in an entry from the 'file' table in
        self.dbname

        Parameters
        ----------
        attr_name : str
                    Attribute name to modify.
        value : str
                New value for `attr_name`.
        name : str
               'name' (path) of entry that
               will be updated.
        dry : bool, default=True
              If dry=True then it will not delete the file
              from the self.dbname.

        Returns
        -------
        int: Return code
             0 : Success
             1 : False
        """
        db_logger.info(f"Updating file entry with name: {name}")

        now = datetime.datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')

        # construct query
        update_sql = f"UPDATE file SET {attr_name}='{value}', updated='{now_str}' WHERE name='{name}'"

        if dry is False:
            try:
                db_logger.info(f"UPDATE sql: {update_sql}")
                cursor = self.conn.cursor(pymysql.cursors.DictCursor)
                # if the connection was lost, then it reconnects
                self.conn.ping(reconnect=True)

                # Execute the SQL command
                cursor.execute(update_sql)
                cursor.close()
                # Commit your changes in the database
                self.conn.commit()
                return 0
            except pymysql.Error as exc:
                db_logger.error("Exception occurred", exc_info=True)
                # Rollback in case there is any error
                self.conn.rollback()
                return 1
        elif dry is True:
            db_logger.info(f"UPDATE sql: {update_sql}")
            db_logger.info(f"DB Entry was not updated")
            db_logger.info(f"Use --dry False to update it")
            return 0
        else:
            raise Exception(f"dry option: {dry} not recognized")






