from ast import Str
from doctest import debug_script
from socket import create_connection
import sqlite3

class Database:
    """
    This class exists only to connect to a SQLITE.db file and execute needed commands.
    """
    def __init__(self, db_file):
        self._db_file = db_file
          
    def execute(self,cmd:str,args=())->list:
        """
        Connects to "_db_file".db and execute the requested command
        :cmd str:   SQLITE command to run
        :args tup:  Arguments required for "cmd"
        """
        
        try:
            conn = sqlite3.connect(self._db_file)
            with conn:
                print(cmd)
                cur = conn.cursor()
                cur.execute(cmd, args)
                conn.commit()
                res = cur.fetchall()
                return res
        except Exception as e:
            print(f'Error! {e}')
  