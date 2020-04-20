from configparser import ConfigParser

import pymysql

class DB(object):
    """
    Class to represent a Reseqtrack db

    Class variables
    ---------------
    settingf : str, Required
               Path to *.ini file with MySQL server connection settings
    """

    def __init__(self, settingf):

        # initialise ConfigParser object with connection
        # settings
        parser = ConfigParser()
        parser.read(settingf)
        self.settings = parser

    def mysql_connect(self, pwd, dbname):
        """
        Function that will handle the connection
        with the MySQL Reseqtrack db

        Parameters
        ----------
        pwd : srt, Required
              Password used for MySQL server connection
        dbname: str, Required
                Reseqtrack db name

        Returns
        -------
        Connection object

        Raises
        ------
        NotImplementedError
            If no sound is set for the animal or passed in as a
            parameter.
        """
        try:
            connection = pymysql.connect(host=self.settings.get('mysql_conn', 'host'),
                                         user=self.settings.get('mysql_conn', 'user'),
                                         password=pwd,
                                         db=dbname,
                                         port=self.settings.get('mysql_conn', 'user'))

        except pymysql.err.OperationalError:
            print('Unable to make a connection to the mysql database. Please check your credentials')

    def load_file(self):
        """
        Function to load a File object
        in self.dbname
        """




