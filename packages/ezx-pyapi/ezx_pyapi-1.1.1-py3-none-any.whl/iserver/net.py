'''
Created on Oct 20, 2021

@author: Sgoldberg
'''
from enum import Enum, auto
import logging
import socket

from iserver import ezx_msg, API_HEADER_SIZE
from iserver.EzxMsg import EzxMsg
from iserver.enums.msgenums import LogonType
from iserver.msgs import LogonRequest
from iserver.msgs import LogonResponse
import iserver
import threading
import time
from iserver.util import StopWatch
from iserver.msgs.HeartBeatMsg import HeartBeatMsg
from iserver.enums import msgenums
from iserver.enums.api import IserverMsgSubType

logger = logging.getLogger(__name__)

def connect(host, port) -> socket.socket :
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    logger.info(f'connected to {host}:{port}')
    return s
    
    
def empty_msg_handler(msg_subtype: int, msg: EzxMsg):
    if msg_subtype == IserverMsgSubType.HEARTBEAT.value:
        # don't log heartbeat message        
        logger.debug(f"received heartbeat message={msg_subtype}, msg={msg}")
    else:
        # log at info level for all other messages
        logger.info(f"received msg={msg}")


class NotLoggedInException(Exception):
    def __init__(self, msg : str = 'Not logged into iServer'):
        super().__init__(msg)
    


class ClientState(Enum):
    INITIAL = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    LOGGED_IN = auto()
    LOGON_FAILURE = auto()
    DISCONNECTED = auto()
    STOPPED = auto()



DEFAULT_CONNECT_RETRY_SECONDS = 5
DEFAULT_HEARTBEAT_SECONDS = 15 

class ConnectionInfo(object):
    '''
    Specifies all settings related to connecting to the iServer.
    '''

    def __init__(self, host : str, port : int, company : str, user : str, password :str, 
                 logon_type : int = LogonType.ALL_FILLS_MSGS_AND_ALL_OPEN_ORDERS.value, 
                 connect_retry_seconds : float = DEFAULT_CONNECT_RETRY_SECONDS, heartbeat_seconds : int = DEFAULT_HEARTBEAT_SECONDS):
        '''
        Constructor
        '''        
        self.host = host
        self.port = port
        self.company = company
        self.user = user
        self.password = password
        self.logon_type = logon_type
        self.connect_retry_seconds = connect_retry_seconds
        heartbeat_seconds = min(DEFAULT_HEARTBEAT_SECONDS, heartbeat_seconds)
        self.heartbeat_seconds = heartbeat_seconds        
        
    def __str__(self):
        return iserver.to_bean_string(self)

class ApiClient(object):
    '''
    Network client used to connect, send and receive messages to and from the iServer.
    '''
    def __init__(self, connection_info : ConnectionInfo, msg_handler = empty_msg_handler, state_handler = lambda *args: None, last_seqno : int = 0):
        '''
        Constructor
        '''        
        self.connection_info = connection_info
        self._msg_handler = msg_handler
        self._state = ClientState.INITIAL
        self.on_state_change = state_handler
        self._last_seqno = last_seqno
        self.connection_monitor = ClientMonitor(self)

        
    def start(self):        
        '''
        Start the connection with iServer
        '''        
        if self.is_running():
            return
        
        logger.info("start(): starting client")
        self._set_state(ClientState.INITIAL)
        self.connection_monitor.start()
        

    def _connect(self):
        logger.info("start(): connecting to iServer...")
        try:
            self._socket = connect(self.connection_info.host, self.connection_info.port)
            # if we get here, we're connected
            self._set_state(ClientState.CONNECTED)
            
            logger.info("start(): connected")
            self.__recv_thread = threading.Thread(target=self._recv)
            self.__recv_thread.start()
            
            self._sendLogin()
            
        except Exception as e:
            logger.error('start(): failed to connect! ex=%s', e)            
            #todo: save exception?
            
        
    def stop(self):
        '''
        Disconnect and shut down the ApiClient
        '''
        # set STOPPED state first to prevent reconnect logic
        self._set_state(ClientState.STOPPED)        
        try:
            if self._socket:
                self._socket.close()
                self._socket = None
                
                logger.info("stop(): socket closed.")
            
            if self.connection_monitor:
                self.connection_monitor.stop()
                
               
        except:
            pass
        
    def _heartbeat(self):
        self.send_message(HeartBeatMsg())
    
    def state(self) -> ClientState:
        return self._state
    
    def _set_state(self, state : ClientState):
        logger.debug("ApiClient.state=%s", state)        
        self._state = state
        self.on_state_change(state)    
        
    @property
    def last_seqno(self):
        return self._last_seqno

    @last_seqno.setter
    def last_seqno(self, seqno):
        if not seqno or seqno < self._last_seqno:
            #don't allow setting bad values
            return 

        self._last_seqno = seqno
            
    
    def is_running(self):
        '''
        Indicates that client has been started and is running        
        '''
        return self.connection_monitor.is_running() # if the monitor is running, the client is alive
    
        
    def is_stopped(self):
        '''
        Returns True when Client was stopped programmatically to shut it down.
        '''
        return self._state == ClientState.STOPPED
    
    def is_connected(self):
        return self._state == ClientState.LOGGED_IN or self._state == ClientState.CONNECTED    
    
    def is_loggedin(self):
        return ClientState.LOGGED_IN == self.state()
    
    def _sendLogin(self):
        logger.info("sendLogin(): sending logon message now.")
        self.send_message(_create_login(self.connection_info, self.last_seqno))
        
    def _handle_message(self, msg_type : int, msg_subtype : int, body : bytearray):
        body = body.decode('UTF-8')
        logger.debug(f"_handle_message(): processing subtype={msg_subtype}, msg={body}")
        msg_object = ezx_msg.decode_message(msg_subtype, body)
                
        if msg_object:
            # handle the logon response first.
            if type(msg_object) is LogonResponse:  
                self.handle_logon_response(msg_object)
            
            try:
                # pass message to the user            
                self._msg_handler(msg_subtype, msg_object)
                self.last_seqno = msg_object.get_seqNo()
                
                
            except Exception as e:  #catching Exception here prevents an error in the user code from killing the receive thread.
                logger.error('exception processing msg=%s. ex=%s', msg_object, e)
                
        else:                        
            logger.warn(f"_handle_message(): did not decode subtype={msg_subtype}")         
        
    def handle_logon_response(self, logon_response):
        if logon_response.returnCode == 0:
            self._set_state(ClientState.LOGGED_IN)
        else:
            logger.fatal(f"handle_logon(): logon failed! returnCode={logon_response.returnCode}, failure message={logon_response.returnDesc} ")            
            logger.fatal('handle_logon(): stopping client. Please contact EZX support!')
            self.logon_failure = (logon_response.returnCode, logon_response.returnDesc)
            self._set_state(ClientState.LOGON_FAILURE)
   
            self.stop()
        
    def _recv(self):
        if not self._socket:
            logger.error("_recv(): no socket to receive, exiting")
            return 
        
        # s = self._socket
        with self._socket:
            header = bytearray(API_HEADER_SIZE) 
            header_recv_length = 0
            body_recv_length = 0
            while self._socket:
                try:
                    logger.debug('_recv(): waiting for message...')
                    if header_recv_length < API_HEADER_SIZE:
                        # use memoryview to create a view of the header buffer from last byte read until the end.
                        header_recv_length += self._socket.recv_into(memoryview(header)[header_recv_length:])
                        
                        if header_recv_length <= 0: 
                            # recv_into seems to have a glitch. It normally blocks while waiting for data. However, 
                            # if client gets disconnected from the server, it does not seem to raise a ConnectionAborted error,
                            # and instead returns with 0 bytes read immediately and causes this method to loop indefinitely.
                            logger.warn("_recv(): recv_into return 0 bytes - indicates disconnect?")
                            raise ConnectionAbortedError                                        
                        
                    if header_recv_length < API_HEADER_SIZE:
                        logger.debug('_recv(): received partial header. expected=%d, received=%d', API_HEADER_SIZE, header_recv_length)
                        continue    # wait to receive the rest of the header
                    
                    length, msg_type, msg_subtype = ezx_msg.parse_header(header)
                    
                    #TO-DO: wrap this in if statement
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug('_recv(): got header. reading body of length=%d. (header=%s)', length, header.decode('UTF-8'))
                        
                    if body_recv_length == 0:
                        body = bytearray(length)

                    # use memoryview to create a view of the body buffer from last byte read until the end.                         
                    body_recv_length += self._socket.recv_into(memoryview(body)[body_recv_length: ])
                    if body_recv_length < length:
                        logger.debug('_recv(): received partial message. expected=%d, received=%d - waiting for remainder of the message', length, body_recv_length)
                        continue
                    
                    header_recv_length = 0
                    body_recv_length = 0
                    
                    #TO-DO: wrap this in if statement
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug('_recv(): got msg, processing msg type=%d. msg=%s', msg_type, body.decode('UTF-8'))
                    
                    self._handle_message(msg_type, msg_subtype, body)
                    
                except ConnectionAbortedError:
                    #TODO: figure out whether this was user disconnect or from another source.
                    logger.info("_recv(): socket was disconnected")
                    break
                    
                except Exception as e:
                    logger.exception(f"_recv(): error receiving message! ex={e}")
                    break;

        logger.debug("_recv(): no longer receiving messages.")

        self._socket = None

        if not self.is_stopped():
            self._set_state(ClientState.DISCONNECTED)
         
    def send_message(self, api_msg_object: EzxMsg):
        
        # TODO: do we need thread synchronization around the socket.sendall method?  Also maybe synchronize the state() and _set_state() methods
        # to this same lock?        
        
        if not self.is_loggedin() and not type(api_msg_object) == LogonRequest: # LogonRequest is sent before being in the logged in state
            raise NotLoggedInException()
                        
        try:
            msg = ezx_msg.to_api_bytes(api_msg_object)
            self._socket.sendall(msg)
            logger.debug("send_message(): sent msg=%s", msg)
            
        except Exception as e:
            logger.error('send_message(): error on send - probably a disconnect! ex=%s', e)
    
    
         
    
    def get_logon_failure(self) -> (int, str):
        '''
        Retrieve logon failure code and description if iServer indicates that the Logon failed
        @return: tuple of errcode (int) and message 
        '''
        try:
            return self.logon_failure
        
        except AttributeError: # this might not be set
            pass
            
       
        
class ClientMonitor(object):
    
    
    def __init__(self, client, wait_seconds = DEFAULT_CONNECT_RETRY_SECONDS, heartbeat_seconds = DEFAULT_HEARTBEAT_SECONDS):
        self.client = client
        self.monitor_thread = None
        self.heartbeat_timer = StopWatch()

    def retry_seconds(self) -> float: 
        return self.client.connection_info.connect_retry_seconds
    
    def heartbeat_seconds(self) -> float:
        return self.client.connection_info.heartbeat_seconds    
    
    def start(self):
        if self.monitor_thread:
            logger.warn('started called when ClientMonitor is already running.')
            return 

        logger.info("ClientMonitor.start(): starting monitor thread")
        self.run = True        
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.monitor_thread.daemon = True                        
        self.monitor_thread.start()
    
        
    def stop(self):
        logger.info("ClientMonitor.stop(): shutting down monitor")
        self.run = False
                        
        
    def monitor(self):
        logger.info("ClientMonitor.monitor(): starting connection monitor")        
        # 1. if not connected, connect
        # 2. if logged in, send heartbeat
        while self.run:
            if self.connect_required():
                self.client._connect()
                time.sleep(self.retry_seconds())
                self.heartbeat_timer.start()            
                
            elif ClientState.LOGGED_IN == self.client.state() and self.heartbeat_timer.elapsed_seconds() >= self.heartbeat_seconds():
                self.client._heartbeat()
                self.heartbeat_timer.start()                
                                
        logger.info('ClientMonitor.monitor(): exiting')
        self.monitor_thread = None
    
    def connect_required(self):
        return self.client.state() == ClientState.INITIAL or self.client.state() == ClientState.DISCONNECTED
    
    def is_running(self):
        if self.monitor_thread:
            return self.monitor_thread.is_alive()



def _create_login(info : ConnectionInfo, seqno : int = 0):
    l = LogonRequest()
    l.companyName = info.company
    l.userName = info.user
    l.password = info.password
    l.logonType = info.logon_type
    # to-do handle setting seqno
    l.seqNo = seqno
    return l