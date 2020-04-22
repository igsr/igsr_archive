from configparser import ConfigParser

import pymysql
import pdb

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
        conn = pymysql.connect(host=self.settings.get('mysql_conn', 'host'),
                               user=self.settings.get('mysql_conn', 'user'),
                               password=self.pwd,
                               db=self.dbname,
                               port=self.settings.getint('mysql_conn', 'port'))
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
              If dry=True then it will not store the file in the DB. Default True

        Returns
        -------
        Path to the stored file
        """

        pdb.set_trace()
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
            except pymysql.Error as e:
                print(e[0], e[1])
                # Rollback in case there is any error
                self.conn.rollback()
        #    warnings.warn("File was stored in the DB")
        #elif dry is True:
         #   warnings.warn("Insert statement was: {0}".format(sql_insert_attr))
         #   warnings.warn("The file was not stored in the DB."
         #                 "Use dry=False to effectively store it")

        return self.path
        print("h\n")








