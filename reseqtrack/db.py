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
           Object with connection to MySQL db
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

    def load_file(self):
        """
        Function to load a File object
        in self.dbname
        """




