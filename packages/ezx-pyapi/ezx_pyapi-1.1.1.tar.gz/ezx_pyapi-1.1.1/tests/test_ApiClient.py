'''
Created on 10 Mar 2022

@author: shalomshachne
'''

import logging
import socket
from socketserver import BaseRequestHandler, TCPServer
from threading import Condition
import threading

import unittest
from unittest.mock import Mock

from iserver import ezx_msg
from iserver.enums.api import IserverMsgSubType, IserverMsgType
from iserver.enums.msgenums import ReturnCode
from iserver.msgs.LogonRequest import LogonRequest
from iserver.msgs.LogonResponse import LogonResponse
from iserver.net import ConnectionInfo, ApiClient, ClientState, \
    NotLoggedInException
from iserver.util import next_id
from tests import check_logging, wait_for_condition, test_util, fill_array
from tests.data import test_data_factory
from iserver.EzxMsg import EzxMsg


logger = logging.getLogger(__name__)


class TestApiClient(unittest.TestCase):

    DEFAULT_PORT = 15002
        
    @classmethod
    def setUpClass(cls):
        # super(TestApiClient, cls).setUpClass()
        # sh = logging.StreamHandler(sys.stdout)
        # logging.root.addHandler(sh)
        check_logging()

    def start_server(self):
        self.server = MockIserver(TestApiClient.DEFAULT_PORT, self.handle)
        self.server.start()

    def setUp(self):
        self.connectInfo = ConnectionInfo(host='localhost', port=TestApiClient.DEFAULT_PORT, company='EZX', user='gnadan', password='gnadan', connect_retry_seconds=.1)        
        self.client = ApiClient(self.connectInfo)
        self.start_server()
        
        self.clientTest = lambda *args: None
        self.last_message = None  # message received by server from the ApiClient
        self.wait_condition = Condition()
        
        self.connect_wait_secs = 3
        
        self.incoming_messages = []
        
        
        
    def tearDown(self):
        self.client.stop()
        self.server.stop()        
    
    def on_state_change(self, state):
        self.last_state_change = state
        
    def handle(self, header, body):
        logger.info(f'got a message. header={header}, body={body}')
        self.wait_condition.acquire()
        self.last_message = (header, body)
        self.wait_condition.notify_all()
        self.wait_condition.release()
            
    def client_message_handler(self, subtype : int, msg : EzxMsg):
        self.incoming_messages.append(msg)
        
    def decode_last_message(self):
        if self.last_message:
            header, body = self.last_message
            _, _, subtype = ezx_msg.parse_header(header)
            body = body.decode('UTF-8')
            return ezx_msg.decode_message(subtype, body)
    

    def testNotifiesStateChange(self):
        received = 'untouched'
        
        def printState(state): 
            nonlocal received        
            received = state
            logger.debug('got state change=%s', received)
        
        handler = printState
                   
        self.client.on_state_change = handler
         
        self.client._set_state(ClientState.CONNECTED)
        
        self.assertEqual(ClientState.CONNECTED, received, "called back on state change")
    
    def test_state_functions(self):
        self.assertFalse(self.client.is_connected(), 'valid initial state')
        
        self.client._set_state(ClientState.CONNECTED)
        self.assertTrue(self.client.is_connected())
        
        self.client._set_state(ClientState.LOGGED_IN)
        self.assertTrue(self.client.is_connected())

    def assert_logon_received(self):
        message = self.last_message
        self.assertIsNotNone(message, 'got a message')
        header, body = message
        sub_type = int(header[8:11].decode('UTF-8'))
        self.assertEqual(IserverMsgSubType.LOGON.value, sub_type, 'received logonRequest')
        logon = ezx_msg.decode_message(sub_type, body.decode('UTF-8'))
        self.assertEqual(0, logon.seqNo, 'default logon seqNo = 0')

    def test_start_sends_logon(self):
        self.wait_condition.acquire()
        self.client.start()
        self.wait_condition.wait(self.connect_wait_secs)  # 3 seconds max wait.

        self.assert_logon_received()
        
    def test_can_restart_after_stop(self):
        self.test_start_sends_logon()
        self.client.stop()
        self.assertEqual(ClientState.STOPPED, self.client.state(), 'valid initial state')
        self.last_message = None

        wait_for_condition(lambda: self.client.connection_monitor.monitor_thread == None, 2)
        self.assertIsNone(self.client.connection_monitor.monitor_thread, 'valid test state - monitor is fully shut down')

        print('===>>>> restarting client here....')                
        self.test_start_sends_logon()  # restart and show it can be reused
        self.assertTrue(self.client.is_running(), 'started...')
        self.assertEqual(ClientState.CONNECTED, self.client.state())
        
    
    def test_can_set_logon_seqno(self):
        self.client.last_seqno = 10
        self.wait_condition.acquire()
        self.client.start()
        self.wait_condition.wait(self.connect_wait_secs)  # 3 seconds max wait.

        logon = self.decode_last_message()
        self.assertEqual(10, logon.seqNo, 'used last seqNo set on the client')
        
    def test_notifies_logon_response(self):
        self.client.on_state_change = self.on_state_change
                
        response = LogonResponse(returnCode=ReturnCode.OK.value)
        api_bytes = ezx_msg.to_api_bytes(response, test_data_factory.random_quantity())
        self.client._handle_message(response.msg_type, response.msg_subtype, api_bytes[15:])
        
        self.assertEqual(ClientState.LOGGED_IN, self.client.state(), 'handled logonresponse correctly = ok')
        self.assertEqual(ClientState.LOGGED_IN, self.last_state_change, 'got notified on logon')
        
    def test_logon_failure_shuts_down_client(self):
        counter = 0

        def check_logon_failure_notification(state):
            nonlocal counter
            counter = counter + 1
            if counter == 1:
                self.assertEqual(ClientState.LOGON_FAILURE, state, 'notified of logon failure')
                self.got_state_change = True

        self.client.on_state_change = check_logon_failure_notification
        failure = 'wrong user name!'
        response = LogonResponse(returnCode=ReturnCode.INVALID_USER.value, returnDesc=failure)
        api_bytes = ezx_msg.to_api_bytes(response, test_data_factory.random_quantity())

        self.client._handle_message(response.msg_type, response.msg_subtype, api_bytes[15:])
        
        self.assertEqual(ClientState.STOPPED, self.client.state(), 'handled logonresponse correctly = failure')
        self.assertTrue(self.client.is_stopped(), 'shut down on logon failure')
        self.assertTrue(self.got_state_change)
        
        errcode, desc = self.client.get_logon_failure()
        self.assertEqual(ReturnCode.INVALID_USER.value, errcode)
        self.assertEqual(failure, desc)
                        
    def test_client_retries_connection(self):
        self.test_start_sends_logon()
        logger.info('stopping server to cause ApiClient disconnect')
        self.server.stop()
        self.last_message = None
        self.connect_wait_secs = 10  # not sure how long to wait.
        self.wait_condition.acquire()
        logger.info('restarting server...')        
        self.start_server()
        logger.info('waiting for login...')        
        self.wait_condition.wait(self.connect_wait_secs) 
        
        # should reconnect shortly
        # message = self.last_message
        # self.assertIsNotNone(message, 'reconnected and logged in')
        self.assert_logon_received()          
    
    def test_client_can_start_before_server(self):
        self.server.stop()
        
        wait_for_condition(lambda: not self.server.is_running())
        self.assertFalse(self.server.is_running(), 'valid test state, server is shut down')                
        self.client.start()

        self.wait_condition.acquire()        
        self.start_server()
        self.wait_condition.wait(self.connect_wait_secs)         
        self.assert_logon_received()
 
    def test_write_not_connected(self):
        response = test_data_factory.create_order_response()
        with self.assertRaises(NotLoggedInException):
            self.client.send_message(response)
            
    def test_write_connected_can_send_logon(self):
        self.client._set_state(ClientState.CONNECTED)
        mock_socket = Mock()
        mock_socket.sendall(bytearray())
        self.client._socket = mock_socket
        
        mock_socket.sendall.assert_called_once()
        logon = LogonRequest()
        self.client.send_message(logon)
    
    def test_calling_start_twice_does_nothing(self):
        mock_monitor = Mock()
        self.client.connection_monitor = mock_monitor
        mock_monitor.start()
        
        self.client.start()
        mock_monitor.start.assert_called_once()
 



    def test_catches_handler_exception(self):

        # if user code throws an Exception, client should keep processing.
        def exception_thrower(subtype, msg):
            raise Exception('something bad happened (unit test)')
        
        self.client._msg_handler = exception_thrower
        msg = test_data_factory.create_order_response()
        
        self.push_message_to_client(msg) 
        
    def test_updates_seqno(self):
        response = test_data_factory.create_order_response()
        
        response.seqNo = test_data_factory.next_int_id()
        self.push_message_to_client(response)        
        self.assertEqual(response.seqNo, self.client.last_seqno, 'updated seqno')
        
        response.seqNo = response.seqNo + 1
        self.push_message_to_client(response)
        self.assertEqual(response.seqNo, self.client.last_seqno, 'updated seqno')
        
    
    def test_cannot_set_seqno_to_bad_values(self):
        seqNo = test_data_factory.next_int_id()
        self.client.last_seqno = seqNo
        self.client.last_seqno = None
        
        self.assertEqual(seqNo, self.client.last_seqno, 'cannot set to None')
        
        self.client.last_seqno = seqNo - 1
        self.assertEqual(seqNo, self.client.last_seqno, 'cannot decrement seqNo')
        
    def test_send_heartbeat(self):
        s = MockSocket()
        self.client._socket = s
        self.client._set_state(ClientState.LOGGED_IN)
        self.client._heartbeat()
    
    
        sent_msgs = s.received
        self.assertEqual(1, len(sent_msgs), 'sent a message')
        msg_bytes = sent_msgs[0]
        self.assertEqual(16, len(msg_bytes), 'header + etx')
        self.assertEqual(3, msg_bytes[15])
        
        length, mtype, subtype = ezx_msg.parse_header(msg_bytes)
        self.assertEqual(IserverMsgType.APPLICATION.value, mtype)
        self.assertEqual(IserverMsgSubType.HEARTBEAT.value, subtype, 'expected msubtype') 
        self.assertEqual(1, length, 'heartbeat has no msg contents except ETX character')
        
          
        
    
    
    def test_mock_socket(self):
        s = MockSocket()
        msg_bytes = bytearray()
        s.sendall(msg_bytes)
        
        self.assertEqual(1, len(s.received))
        self.assertEqual(msg_bytes, s.received[0])
        
    def test_socket_receive_partial_body_reads_continues_to_read(self):
        header_string = '00035702150028'
        body_string = 'MYID=Ord-637878923112570755-22ROID=78UIDN=7UNAM=igorSIDE=2PX=0.02OQTY=500MINQ=100FV=0DISOFF=0XSYM=UNYSYM=ULXMDSYM=UNYMDSYM=ULXTXT=+B.1.a.4YTXT=+B.1.a.4DEST=SIMUACCT=5EW6PK15LREQD=GOLDMANHGALL=100MVALL=0SLIP=0.01ISCAN=10HSCAN=15REPMS=0MAXDIST=40DELAYMS=0FQTY=0HQTY=0XFQTY=0YFQTY=0PRSTATE=CanceledSTATE=CANDOID=pairs-server\x003'
        self.assertEqual(int(header_string[0:6]),len(body_string), 'valid setup')
        
        self.client._msg_handler = self.client_message_handler 
        
        
        header_bytes = header_string.encode('UTF8')
        body_bytes = body_string.encode('UTF-8')
        partial_recv_length = 213
        
        counter = -1
        values = [15, partial_recv_length, 0, len(body_bytes) - partial_recv_length]
        def recv_into(b):
            import tests
            nonlocal counter            
            counter += 1
            if counter == 0:
                b[:] = header_bytes
            elif counter == 1:
                tests.fill_array(b, body_bytes[0 : partial_recv_length])
            elif counter == 2:
                pass
            elif counter == 3:
                tests.fill_array(b, body_bytes[partial_recv_length:])
            else:
                raise ConnectionAbortedError #stop processing
            return values[counter]
        
        s = Mock()
        s.recv_into = recv_into
        enter_s = Mock(return_value=s)
        s.__enter__ = enter_s
        s.__exit__ = enter_s
        self.client._socket = s
        self.client._recv()
        
        expected = 1
        actual = len(self.incoming_messages)
        self.assertEqual(expected, actual, 'got correct number of messages')
        
    def test_socket_receive_partial_header(self):
        header_string = '00035702150028'
        body_string = 'MYID=Ord-637878923112570755-22ROID=78UIDN=7UNAM=igorSIDE=2PX=0.02OQTY=500MINQ=100FV=0DISOFF=0XSYM=UNYSYM=ULXMDSYM=UNYMDSYM=ULXTXT=+B.1.a.4YTXT=+B.1.a.4DEST=SIMUACCT=5EW6PK15LREQD=GOLDMANHGALL=100MVALL=0SLIP=0.01ISCAN=10HSCAN=15REPMS=0MAXDIST=40DELAYMS=0FQTY=0HQTY=0XFQTY=0YFQTY=0PRSTATE=CanceledSTATE=CANDOID=pairs-server\x003'
        
        self.client._msg_handler = self.client_message_handler 
        header_bytes = header_string.encode('UTF8')
        body_bytes = body_string.encode('UTF-8')

        partial_header = 2
        s = MockSocket()
        s.to_send.append(header_bytes[0:partial_header]) #send only first part of the header
        s.to_send.append(header_bytes[partial_header:])  #send the rest
        s.to_send.append(body_bytes) #body 
                
        self.client._socket = s
        self.client._recv()
        
        expected = 1
        actual = len(self.incoming_messages)
        self.assertEqual(expected, actual, 'got correct number of messages')

    def test_socket_receives_multiple_messages(self):
        self.client._msg_handler = self.client_message_handler
        msgs = []
        msgs.append(ezx_msg.to_api_bytes(test_data_factory.create_order_response()))
        msgs.append(ezx_msg.to_api_bytes(test_data_factory.create_new_order_request()))
        msgs.append(ezx_msg.to_api_bytes(test_data_factory.create_logon_response()))
        
        s = MockSocket(to_send=msgs)        
        
        self.client._socket = s
        self.client._recv()
        expected = len(msgs)
        actual = len(self.incoming_messages)
        message = "client received all the messages"
        self.assertEqual(expected, actual, message)
        
        
        
        
        







        
    def push_message_to_client(self, msg):
        body = ezx_msg.encode(msg).encode(encoding='UTF-8')
        self.client._handle_message(IserverMsgType.APPLICATION.value, IserverMsgSubType.ORDERRESPONSE.value, body)


        
    
class MockIserver(object):

    def __init__(self, port, handler):
        
        class ApiClientTestHandler(BaseRequestHandler):

            def __init__(self, *args):
                self.handler = handler  # function(header,body)
                super().__init__(*args)
                logger.debug('ApiClientTestHandler..__init__(): initialized handler')
                
            def handle(self):
                # parse header
                header = self.request.recv(15)
                if not header:
                    logger.error('error: did not receive enough bytes for an API header!')
                    return 
                length, msg_type, msg_subtype = ezx_msg.parse_header(header)
                logger.info(f'msg length={length}, msg_subtype={msg_subtype}')
                body = self.request.recv(length)
                self.handler(header, body)
                 
        self.port = port
        self.server = TCPServer(('localhost', port), ApiClientTestHandler, False)
        # enable immediate reuse
        self.server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.server_bind()
        self.server.server_activate()
        logger.info(f'Server listening on: {self.server.server_address}')
        
    def start(self):
        logger.info(f'starting server on port={self.port}')
        t = threading.Thread(target=self.server.serve_forever)
        t.daemon = True
        t.start()
        self.server_thread = t
        logger.info(f'Server started.')
        # self.server.serve_forever()
        
    def is_running(self):
        try:
            return self.server_thread.is_alive()
        except AttributeError:
            pass
        
    def stop(self):
        logger.info('stopping server')
        self.server.shutdown()
        self.server.server_close()
        logger.info('server stopped')
        

class MockSocket(socket.socket):
    def __init__(self, to_send : list = list()):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.received = []
        self.to_send : list(bytearray) = to_send
        self.message_send_index = 0
        self.within_message_index = 0
        
    def sendall(self, *args, **kwargs):
        msg_bytes = args[0]
        self.received.append(msg_bytes)        
        return len(msg_bytes)
    
    def recv_into(self, buffer, nbytes=0, flags=None) -> int:
        if self.message_send_index < len(self.to_send):
            source = self.to_send[self.message_send_index][self.within_message_index:]
            sent = fill_array(buffer, source)
            if sent == len(source): # fully sent
                self.message_send_index += 1
                self.within_message_index = 0
            else:   # partial message sent
                self.within_message_index = sent
                
            return sent
        
        raise ConnectionAbortedError # when no more messages

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
