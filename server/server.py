from csv import excel_tab
import socket
import struct
import ctypes
import os
import sys
from threading import Thread
from time import sleep
import uuid
from tkinter.tix import TEXT
from Database import Database
from ClientRequest import ClientRequest,ServerResponse
from datetime import datetime


sql_create_clients_table = """ CREATE TABLE IF NOT EXISTS clients(
                                            ID VARCHAR(128) PRIMARY KEY,
                                            UserName VARCHAR(255) NOT NULL,
                                            PublicKey VARCHAR(160) NOT NULL,
                                            LastSeen DATETIME NOT NULL);"""

sql_create_messages_table = """CREATE TABLE IF NOT EXISTS messages(
                                 ID int PRIMARY KEY,
                                 ToClient VARCHAR(16),
                                 FromClient VARCHAR(16),
                                 Type int,
                                 Content Blob);"""


class Server:   
   def __init__(self, threads_limit=100):
      """
      Reads the server details from 'server.info' (IP:PORT)
      Connects to the database object and creates the tables if needed
      Prints "clients" and "messages" tables 
      """
      try:
         
         f = open(os.path.join(sys.path[0], 'server.info'),'r') 
         addr = f.readline().split(':')
         self.HOST, self.PORT = addr[0],int(addr[1])
         self._threads_limit = threads_limit
         self.db = Database(os.path.join(sys.path[0],'server.db'))
         self.db.execute(sql_create_clients_table)
         self.db.execute(sql_create_messages_table)
         self.threads = []
      except Exception as ex:
         print(ex)
         exit(1)
         
   def respond(self,cr:ClientRequest)->ServerResponse:
      """
      Returns a ServerResponse according to "cr"
      :cr ClientRequest:      Client's request
      :return ServerResponse: Response for cr, will return response code 9000 as error
      """
      if cr.code == 1100:
         # Registration
         us = self.db.execute('SELECT ID FROM clients WHERE UserName=?', (cr.username,))
         if len(us) == 0:
            #add user
            userid = uuid.uuid1()
            self.db.execute('INSERT INTO clients (ID,UserName,PublicKey,LastSeen) VALUES(?,?, ?, "{datetime.now()}")', (userid.bytes,cr.username,cr.public_key,))
            return ServerResponse(2100,(userid.bytes,))
         
      else:
         results = self.db.execute('SELECT ID FROM clients WHERE ID=?',(cr.client_id,))
         if len(results) == 1: # Verify client_id
            if cr.code == 1101:
               # Get userlist
               userlist = self.db.execute('SELECT ID,UserName FROM clients WHERE ID<>?',(cr.client_id,)) # WITHOUT CONDITION ITS SIUMULATOR MODE   
               return ServerResponse(2101,userlist)
         
            elif cr.code == 1102:
               # Get specified user's public key
               results = self.db.execute('SELECT ID,PublicKey FROM clients WHERE ID=?',(cr.client_to_get,))
               if len(results) == 1:
                  id, pub_key = results[0]
                  return ServerResponse(2102,(id, pub_key))
               
            elif cr.code == 1103:
               # Save message
               msgid = self.db.execute('SELECT ID FROM messages ORDER BY ID DESC')+[(0,)]
               msgid = msgid[0][0]+1
               self.db.execute('INSERT INTO messages (ID,ToClient,FromClient,Type,Content) VALUES(?, ?, ?, ?,?)', (msgid,cr.dest_client_id,cr.client_id,cr.msg_type,cr.msg))
               return ServerResponse(2103,(cr.dest_client_id,msgid))
               
            elif cr.code == 1104:
               # Get messages
               msgs = self.db.execute('SELECT ID,FromClient,Type,Content FROM messages WHERE ToClient=?', (cr.client_id,))
               self.db.execute('DELETE FROM messages WHERE ToClient=?', (cr.client_id,))
               return ServerResponse(2104,msgs)
            
      # else:
      return ServerResponse(9000)
   
         
   def accept(self,conn,addr)->None:
      """
      After a connection is set, this function accepts and responds the client's request
      :conn:   Socket connection to send/recieve data
      :addr:   connection's address.
      """

      with conn:
         print('Connected by ', addr)
         data = conn.recv(ClientRequest._header_size) #recieve header
         cr = ClientRequest(data)   # proccess header
         if cr.payload_size > 0:
            data = conn.recv(cr.payload_size) #recieve payload
            cr.set_payload(data)    # proccess payload
         resp = self.respond(cr)    # get response
         # print(resp.code,resp.payload)
         conn.sendall(resp.reply)   
         sleep(10)   # Keep connection alive for a few seconds
         print(f'Connection to {addr[0]}:{addr[1]} closed. job done!')
      
   def run(self):
      """
      Starts the server.
      """
      print(self.db.execute('SELECT * FROM clients'))    #print clients list
      print(self.db.execute('SELECT * FROM messages'))   #print messages list
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         s.bind((self.HOST, self.PORT))
         s.listen()
         print(f'\nListening on {self.HOST}:{self.PORT}')
         while len(self.threads) < self._threads_limit:   #Limit of threads to avoid fatal DDOS attacks
            try:    
               conn, addr = s.accept()
               th = Thread(target=self.accept,args=(conn,addr))
               self.threads.append(th)
               th.start()
               
               for t in self.threads:
                  # Cleanup threads list
                  if t.is_alive() == False:
                     t.join()
                     self.threads.remove(t)
               print(f'{len(self.threads)} Threads are operating at the moment out of {self._threads_limit} threads allowed')
                 
            except Exception as ex:
               print("ERROR!",ex)
               # exit()
               
               
if __name__ == '__main__':
   s = Server()
   s.run()