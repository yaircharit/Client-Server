from ctypes import sizeof
from decimal import InvalidContext
import struct

def get_string(data:bytearray)->str:
    """
    Converts a bytes array to a string-> will stop at '\0' or data length
    :data bytearray:    byte array to convert
    :return str:        string of bytes from data
    """
    i = 0
    res = ''
    
    while i < len(data) and data[i] != 0 :
        res += chr(data[i])
        i+=1
    return res

class ClientRequest:
    """
    This class represents a client request during initialization the header is set (client ID, req_version, req_code, payload size)
    After initialization- if needed, the payload can be set through the 'set_payload' function.
    """
    
    _header_format = '<16sbhi'
    _header_size = struct.calcsize(_header_format)
    _payload_formats = {1100: '<255s160s',1102:'<16s',1103:'<16s1si'}
    def __init__(self, data):
        """
        Recieves header data and initializes the object accordingly
        :data bytearray:    header data
        """
        tup = struct.unpack_from(ClientRequest._header_format,data) #Read header
        print("Received message: " , tup)
        self.client_id, self.version, self.code, self.payload_size = tup
        self.payload_format = ClientRequest._payload_formats.get(self.code,'')
        self.payload = 0
        
    def set_payload(self,data):
        """
        Recieves payload data as bytearray and sets it according to the request code
        :data bytearray:    payload data
        """
        
        if self.payload_size > 0:
            self.payload = bytearray(self.payload_size)
            self.payload = struct.unpack_from(self.payload_format,data,0) 
            print("Received payload: " ,data)
            
            if self.code == 1100:
                self.username = get_string(self.payload[0])
                self.public_key = self.payload[1]
                # print(f'\nusername = {self.username}')
            elif self.code == 1102:
                self.client_to_get = self.payload[0]
            elif self.code == 1103:
                self.dest_client_id = self.payload[0]
                self.msg_type = int.from_bytes(self.payload[1],'little')
                self.msg_size = self.payload[2]
                self.msg = bytearray(self.msg_size)
                self.msg = struct.unpack_from(f'{self.msg_size}s',data,struct.calcsize(self.payload_format))[0]

                
        


class ServerResponse:
    """
    This class represents a server response which we send to the client
    This object should be initialized with the relevant payload
    """
    _version = 2
    _header_format = '<1shi'
    _header_size = struct.calcsize(_header_format)
    _payload_formats = {2100: '16s',2101: '16s255s',2102:'16s160s',2103: '<16si',2104: '<16si1si'}
    
    def __init__(self,response_code,payload = tuple()):
        self.version = ServerResponse._version
        self.code = response_code
        self.payload_format = ServerResponse._payload_formats.get(self.code,'')
        self.payload = payload
        
        self.payload_size = struct.calcsize(self.payload_format)
        if self.code == 2101 or self.code == 2104:           
            org_size = self.payload_size 
            self.payload_size *= len(self.payload)
            if self.code == 2104:
                for msg in self.payload:
                    self.payload_size += len(msg[3])
        
        self.reply = bytearray(ServerResponse._header_size + self.payload_size)
        struct.pack_into(ServerResponse._header_format,self.reply,0,ServerResponse._version.to_bytes(1,'little'),self.code,self.payload_size)
        
        if self.payload_size > 0:
            plc = ServerResponse._header_size
            if self.code == 2101:
                for id,name in payload:
                    struct.pack_into(self.payload_format,self.reply,plc,id,bytes(name,'utf-8')) 
                    plc+=org_size
            elif self.code == 2104:
                for msg_id,from_id,typ,cont in payload:
                    # set message header
                    struct.pack_into(self.payload_format,self.reply,plc,from_id,msg_id,typ.to_bytes(1,'little'),len(cont)) 
                    plc += org_size
                    struct.pack_into(f'{len(cont)}s',self.reply,plc,cont) #set content
                    plc += len(cont)   
                    
            else: 
                #ServerReponse #2100 / #2102 / #2103
                struct.pack_into(self.payload_format,self.reply,plc,*self.payload)
