from configparser import ConfigParser
from file.file import File

import pymysql
import pdb
import logging

# create logger
db_logger = logging.getLogger(__name__)

class DB(object):
    """
    Class to represent a Reseqtrack db

    Class variables
    ---------------
    settingf : str, Required
               Path to *.ini file with MySQL server connection settings
    conn : Connection object
           Connection to MySQL db
    pwd : srt, Required
          Password used for MySQL server connection
    dbname: str, Required
            Reseqtrack db name
    """

    def __init__(self, settingf, pwd, dbname):

        db_logger.info('Creating DB object')

        # initialise ConfigParser object with connection
        # settings
        parser = ConfigParser()
        parser.read(settingf)
        self.pwd = pwd
        self.dbname = dbname
        self.settings = parser
        self.conn = self.set_conn()

    def set_conn(self):
        """
        Function that will set the conn
        class variable

        Returns
        -------
        Connection object
        """

        db_logger.info('Setting connection...')

        conn = pymysql.connect(host=self.settings.get('mysql_conn', 'host'),
                               user=self.settings.get('mysql_conn', 'user'),
                               password=self.pwd,
                               db=self.dbname,
                               port=self.settings.getint('mysql_conn', 'port'))

        db_logger.info('Connection successful!')

        return conn

    def load_file(self, f, dry=True):
        """
        Function to load a File object
        in self.dbname

        Parameters
        ----------
        f : File object
            File that will be stored in this DB
        dry : Bool, Optional
              If dry=True then it will not try to store the file in the DB. Default True

        Returns
        -------
        Path to the stored file

        Raises
        ------
        pymysql.Error
            If file could not be loaded
        """

        db_logger.info(f"Loading file: {f.path}")
        # construct INSERT INTO sql statement
        sql_insert_attr = f"INSERT INTO file (file_id, name, md5, type, size, host_id, withdrawn, created) " \
                          f"VALUES (NULL, \'{f.path}\', \'{f.md5sum}\', \'{f.type}\', \'{f.size}\', \'{f.host_id}\', " \
                          f"\'{f.withdrawn}\', \'{f.created}\')"

        if dry is False:
            try:
                cursor = self.conn.cursor()
                # Execute the SQL command
                cursor.execute(sql_insert_attr)
                # Commit your changes in the database
                self.conn.commit()
                db_logger.info(f"File loaded: {f.path}")
            except pymysql.Error as e:
                db_logger.error("Exception occurred", exc_info=True)
                # Rollback in case there is any error
                self.conn.rollback()

        elif dry is True:
            db_logger.info(f"Insert sql: {sql_insert_attr}")
            db_logger.info(f"File was not stored in the DB.")
            db_logger.info(f"Use dry=False to effectively store it")

        else:
            raise Exception(f"dry option: {dry} not recognized")

        return f.path

    def delete_file(self, f, dry=True):
        """
        Function to delete a File object
        from self.dbname

        Parameters
        ----------
        f : File object
            File to be deleted from the DB
        dry : Bool, Optional
              If dry=True then it will not delete the file
              from the self.dbname. Default True

        Raises
        ------
        pymysql.Error
        If there was some kind of error
        """

        db_logger.info(f"Deleting file: {f.path}")

        # construct DELETE sql statement
        delete_sql = f"DELETE from file where name='{f.path}'"

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

        elif dry is True:
            db_logger.info(f"Delete sql: {delete_sql}")
            db_logger.info(f"File was not deleted from the DB.")
            db_logger.info(f"Use dry=False to effectively delete it")

        else:
            raise Exception(f"dry option: {dry} not recognized")

    def fetch_file(self, path):
        """
        Function to fetch a file from DB

        Parameters
        ----------
        path : str
               Path of file to be retrieved

        Returns
        -------
        file.file.File object retrieved from DB
        None if no file was retrieved
        """

        db_logger.info(f"Fetching file with path: {path}")

        query = "SELECT * FROM file WHERE name like %s"

        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, ['%' + path])
            result_set = cursor.fetchall()
            if not result_set:
                db_logger.info(f"No file retrieved from DB using using path:{path}")
                return None
            for row in result_set:
                f = File(**row)
                return f
            cursor.close()
            self.db.commit()
        except pymysql.Error as e:
            db_logger.error("Exception occurred", exc_info=True)
            # Rollback in case there is any error
            self.conn.rollback()








