'''
Created on Sep 29, 2021

@author: Sgoldberg
'''
import unittest

from iserver import ezx_msg, msg_factory
import iserver
from iserver.enums import api
from iserver.enums.api import IserverMsgSubType
from iserver.msgs import LogonRequest, msgtags, LogonResponse, OrderResponse, \
    ExecutionStatus
import tests


class Test(unittest.TestCase):

    def test_to_string_does_not_show_extra_decimals(self):
        value = 123.45
        expected = "123.45"
        actual = ezx_msg.to_string(value)
        self.assertEqual(expected, actual, "simple case")
                
        value = value + .01
        expected = "123.46"
        actual = ezx_msg.to_string(value)
        self.assertEqual(expected, actual, "rounds float")
        
    def test_to_string_works_for_strings(self):
        value = "Hello World"
        self.assertEqual(value, ezx_msg.to_string(value))

    def test_to_string_works_for_int(self):
        value = 987654321
        self.assertEqual(str(f'{value}'), ezx_msg.to_string(value))

    def test_msg_to_map(self):
        msg = "00010402100000\001CONAM=FEIS\001DTGMT=<TODAY>\001TYPE=3\001PWD=igor\001SEQ=0\001UNAM=igor\001SNDDESTSTRAT=1\001SNDSETS=1\001DSTAT=1\001OMSVER=4.0.1\001\003"
        m = ezx_msg.msg_to_map(msg)
        self.assertIsNotNone(m)
        field = "CONAM"
        expected = "FEIS"
        actual = m[field]
        self.assertEqual(expected, actual, field)
        
        field = "DTGMT"
        expected = "<TODAY>"
        actual = m[field]
        self.assertEqual(expected, actual, field)

    def create_logon_request(self):
        logon = LogonRequest()
        logon.companyName = 'FEIS'
        logon.userName = 'igor'
        logon.password = 'igor'
        logon.dateGMT = '<TODAY>'
        logon.logonType = 3
        logon.sendDestStrategies = 1
        logon.sendSettings = 1
        logon.sendDestinationState = 1
        logon.omsVersion = "4.0.1"
        logon.seqNo = 111
        
        return logon

    def test_encode_logon_request(self):
        logon = self.create_logon_request()
        
        msg = "CONAM=FEIS\001DTGMT=<TODAY>\001TYPE=3\001PWD=igor\001SEQ=111\001UNAM=igor\001SNDDESTSTRAT=1\001SNDSETS=1\001DSTAT=1\001OMSVER=4.0.1\001"
        
        encoded = ezx_msg.encode(logon)
        print(f'original={msg}')
        print(f'encoded={encoded}')
        self.assertEqual(ezx_msg.msg_to_map(msg), ezx_msg.msg_to_map(encoded))
        
    def test_to_api_msg_adds_header_and_terminator(self):
        msg = "00010602100000\001CONAM=FEIS\001DTGMT=<TODAY>\001TYPE=3\001PWD=igor\001SEQ=111\001UNAM=igor\001SNDDESTSTRAT=1\001SNDSETS=1\001DSTAT=1\001OMSVER=4.0.1\001\003"
        print(f'original message={msg}')
        logon = self.create_logon_request()
        api = ezx_msg.to_api_msg(logon)
        expected = msg[0:15]
        actual = api[0:15]
        self.assertEqual(expected, actual, "added API header")
        
    def test_to_api_msg_ends_with_tx(self):
        msg = "00010502100000\001CONAM=FEIS\001DTGMT=<TODAY>\001TYPE=3\001PWD=igor\001SEQ=111\001UNAM=igor\001SNDDESTSTRAT=1\001SNDSETS=1\001DSTAT=1\001OMSVER=4.0.1\001\003"
        print(f'original message={msg}')
        logon = self.create_logon_request()
        api = ezx_msg.to_api_msg(logon)
        expected = '\x03'
        actual = api[-1]
        self.assertEqual(expected, actual, "added tx")
        
    def test_to_api_msg_length_correct(self):
#         msg = "00010402100000\001CONAM=FEIS\001DTGMT=<TODAY>\001TYPE=3\001PWD=igor\001SEQ=111\001UNAM=igor\001SNDDESTSTRAT=1\001SNDSETS=1\001DSTAT=1\001OMSVER=4.0.1\001\003"
        logon = self.create_logon_request()
        api = ezx_msg.to_api_msg(logon)
        print(f'api={api}')
        header = api[0:15]
        print(f'api={api} (after getting header)')        
        length = int(header[0:6])
        api = api[15:]
        self.assertEqual(length, len(api), f"header shows msg length=API message line (+ ETX char). header={header}, msg={api}")
        
    def test_decodes_msg(self):
# C++ library handles it this way:
#       int msg_subtype = reader_->msg_subtype();
#       ezx::iserver::EZXMsgPtr msg(ezx::iserver::decode_message(msg_subtype, reader_->read_buffer_));    
        logon = self.create_logon_request()
        api = ezx_msg.to_api_msg(logon)
        logon2 = ezx_msg.decode_message(logon.msg_subtype, api)
        self.assertEqual(type(logon), type(logon2), "got correct message type")
        tests.assert_fields_match(logon, logon2, self)
        
        self.assertEqual(logon, logon2, "decoded logon correctly")
        
    def test_decode_no_message_found_returns_none(self):
        msg_subtype = 100000
        msg = tests.random_string()
        decoded = ezx_msg.decode_message(msg_subtype, msg)
        self.assertIsNone(decoded)

    def test_get_message(self):
        m = msg_factory.get_message(api.IserverMsgSubType.LOGON.value)
        self.assertIsNotNone(m)
        self.assertEqual(LogonRequest, type(m))
        
        m = msg_factory.get_message(api.IserverMsgSubType.LOGONRESPONSE.value)
        self.assertIsNotNone(m)        
        self.assertEqual(LogonResponse, type(m))
        
        m = msg_factory.get_message(-1)
        self.assertIsNone(m)

    def test_msg_equals(self):
        logon = self.create_logon_request()
        f = iserver.msg_equals
        self.assertTrue(f(logon, logon))
        
        logon2 = self.create_logon_request()
        self.assertTrue(f(logon, logon2))
        
        self.assertEqual(logon, logon2, "implemented equals function")
        
        logon2.userName = "different name"
        self.assertFalse(f(logon, logon2))
        
        s = "hello world"
        self.assertFalse(f(logon, s), "different object is not equal")
      
    def testParseHeader(self):
        header = '00050502112000'        
        self.assertEqual(iserver.API_HEADER_SIZE, len(header))
        header = header.encode('UTF-8')
        size, msgtype, subtype = ezx_msg.parse_header(header) 
        self.assertEqual(505, size, "correct msg length")
        self.assertEqual(2, msgtype, "correct msg type")
        self.assertEqual(112, subtype, "correct msg subtype")
        
    def testDecodeWithVector(self):
        msg = 'DEST=SIMUDEST=BLOOMBERG_UATDEST=TRADETECH_UATDEST=TRADETECH_UAT-CMEDEST=TO_FIX2APIDEST=TO_FIX2API1DEST=MERRILL-SIMUDEST=LOADBALANCE_TESTDEST=TO_INBOUND1DEST=ALLWEEKDEST=BlazeDEST=CURRENEXDEST=TRADETECH_CERTDEST=RAPTOR_TDUATRETC=0HBSECS=1800'
        subtype = api.IserverMsgSubType.LOGONRESPONSE.value
        response = ezx_msg.decode_message(subtype, msg)
        
        destinations = response.destinations
        self.assertIsInstance(destinations, list, "created a list for destinations")
        
        expected = msg.count("DEST=")
        actual = len(response.destinations)
        message = "decoded all the destinations"
        self.assertEqual(expected, actual, message)
        
        
    def testEncodeWithVector(self):
        msg = 'DEST=SIMUDEST=BLOOMBERG_UATDEST=TRADETECH_UATDEST=TRADETECH_UAT-CMEDEST=TO_FIX2APIDEST=TO_FIX2API1DEST=MERRILL-SIMUDEST=LOADBALANCE_TESTDEST=TO_INBOUND1DEST=ALLWEEKDEST=BlazeDEST=CURRENEXDEST=TRADETECH_CERTDEST=RAPTOR_TDUATRETC=0HBSECS=1800'
        subtype = api.IserverMsgSubType.LOGONRESPONSE.value
        response = ezx_msg.decode_message(subtype, msg)
        
        expected = msg.count('DEST=')
        actual = len(response.destinations)
        message = 'valid test state - decoded destinations list'
        self.assertEqual(expected, actual, message)
        
        encoded = ezx_msg.encode(response)
        expected = 'RETC=0'
        actual = encoded
        message = 'encoded returnCode'
        self.assertTrue(expected in actual, message)
        
        expected = len(response.destinations)
        actual = encoded.count('DEST=')
        message = 'wrote the destinations list. encoded=' + encoded
        self.assertEqual(expected, actual, message)
        
    def testEncodeGroup(self):
        msg= 'RECVMTHD=M|ORDERID=1|SEQ=49|VER=1|SIDE=1|OQTY=100|PX=20|OTYP=2|ACCT=XYZ|DEST=SIMU|SOLICIT=0|SYM=ABC|CUMQ=0|EVT=ORDR|LVS=100|PENDREQ=NEW|STATE=NEW|TS=2021-10-28 21:49:24|TOTEX=0|UNAM=gnadan|TRTIME=2021-10-28 21:49:24|OETIME=2021-10-28 21:49:24|CORDERTYP=2|TCUMQ=0|TTOTEX=0|UNRTDQTY=100|TENB=-1|UID=466|COID=240|B=EB|EVT=EXEC|EXTRANS=0|EXTYP=2|OQTY=100|OTYP=2|ETIME=2021-10-25 13:09:23|VER=1|LPX=10|LSHRS=5|EID=96|TTIME=20211025-13:09:27.215|IGEN=0|CLID=EZ-20211025-3|BOID=20211025-2-O|E=EB|\003'        
        msg = msg.replace('|', '\001')
        subtype = IserverMsgSubType.CLIENT_ORDER_RESPONSE.value
        cor = ezx_msg.decode_message(subtype, msg)
        
        expected = 'SIMU'
        actual = cor.destination
        message = "destination decoded"
        self.assertEqual(expected, actual, message)
        
        execStatus = cor.execStatus
        self.assertIsNotNone(execStatus, 'decoded execStatus group')
        
        expected = 5
        actual = execStatus.lastShares
        message = "valid test state"
        self.assertEqual(expected, actual, message)
        
        encoded = ezx_msg.encode(cor)
        
        expected = 'SYM=ABC'
        actual = encoded
        message = "encoded symbol"
        self.assertTrue(expected in actual, message)
        
        expected = 'DEST=SIMU'
        actual = encoded
        message = "encoded dest"
        self.assertTrue(expected in actual, message)
        
        expected = 'B=EB'
        actual = encoded
        message = "encoded execution Start block"
        self.assertTrue(expected in actual, message)

        expected = 'E=EB'
        actual = encoded
        message = "encoded execution End block"
        self.assertTrue(expected in actual, message)
        
        cor2 = ezx_msg.decode_message(subtype, encoded)
        self.assertEqual(cor, cor2, f'messages are equal. expected={cor}, was={cor2}')
        
        
        
 
        
    def testDecodeBlockExecutionStatus(self):
        msg = 'HDLI=2|ROID=3|SEQ=19|VER=1|SIDE=2|TIF=0|OQTY=100|PX=10|OTYP=2|ACCT=5CG05400|CLID=EZ-20211025-3|COMM=0|DEST=SIMU|SYM=ABC|TXT=+B.1.a.4|CUMQ=10|EVT=EXEC|LVS=90|PENDREQ=NOPEND|STATE=PAFI|TS=2021-10-25 13:09:27|TOTEX=100|UNAM=gnadan|EZXCLID=2|EZXCLIDVERSION=1|MSGORIGIN=1|CLIENTNAMEID=125|BOID=20211025-2-O|TCUMQ=10|TTOTEX=100|B=EB|EVT=EXEC|EXTRANS=0|EXTYP=2|OQTY=100|OTYP=2|ETIME=2021-10-25 13:09:23|VER=1|LPX=10|LSHRS=5|EID=96|TTIME=20211025-13:09:27.215|IGEN=0|CLID=EZ-20211025-3|BOID=20211025-2-O|E=EB|B=ORSB|VER=1|REQSTATE=ACCEPTED|CLID=EZ-20211025-3|EZXCLID=2|EZXCLIDVERSION=1|E=ORSB|UID=466|SSID=2|\003'
        msg = msg.replace('|', '\001')
        index = msg.find("B=EB") + 5
        r = OrderResponse()
        final_index, exec_status = ezx_msg.parse_block(index, msg, r, 'EB')
        self.assertIsInstance(exec_status, ExecutionStatus, "created the message")
        end_of_block = 'E=EB\001'  
        self.assertEqual(msg.find(end_of_block) + len(end_of_block), final_index, 'returned correct index - consumed up to the TagValuePair delimiter')
        
        self.assertEqual(5, exec_status.lastShares, 'got correct last shares')
    
    def testDecodeOrderResponseWithExecutionBlock(self):
        msg = 'HDLI=2|ROID=3|SEQ=19|VER=1|SIDE=2|TIF=0|OQTY=100|PX=10|OTYP=2|ACCT=5CG05400|CLID=EZ-20211025-3|COMM=0|DEST=SIMU|SYM=ABC|TXT=+B.1.a.4|CUMQ=10|EVT=EXEC|LVS=90|PENDREQ=NOPEND|STATE=PAFI|TS=2021-10-25 13:09:27|TOTEX=100|UNAM=gnadan|EZXCLID=2|EZXCLIDVERSION=1|MSGORIGIN=1|CLIENTNAMEID=125|BOID=20211025-2-O|TCUMQ=10|TTOTEX=100|B=EB|EVT=EXEC|EXTRANS=0|EXTYP=2|OQTY=100|OTYP=2|ETIME=2021-10-25 13:09:23|VER=1|LPX=10|LSHRS=5|EID=96|TTIME=20211025-13:09:27.215|IGEN=0|CLID=EZ-20211025-3|BOID=20211025-2-O|E=EB|B=ORSB|VER=1|REQSTATE=ACCEPTED|CLID=EZ-20211025-3|EZXCLID=2|EZXCLIDVERSION=1|E=ORSB|UID=466|SSID=2|\003'
        msg = msg.replace('|', '\001')
        subtype = api.IserverMsgSubType.ORDERRESPONSE.value
        response = ezx_msg.decode_message(subtype, msg)
        self.assertIsInstance(response, OrderResponse)
        
        expected = 'ABC'
        actual = response.symbol
        message = "symbol"
        self.assertEqual(expected, actual, message)
        
        expected = 2
        actual = response.side
        message = 'side'
        self.assertEqual(expected, actual, message)
        
        executions = response.executions
        self.assertIsNotNone(executions, 'got the executions list')
        
    def testDecodeOrderResponseWithMultipleExecutionsBlock(self):
        msg = 'HDLI=2|ROID=3|SEQ=19|VER=1|SIDE=2|TIF=0|OQTY=100|PX=10|OTYP=2|ACCT=5CG05400|CLID=EZ-20211025-3|COMM=0|DEST=SIMU|SYM=ABC|TXT=+B.1.a.4|CUMQ=10|EVT=EXEC|LVS=90|PENDREQ=NOPEND|STATE=PAFI|TS=2021-10-25 13:09:27|TOTEX=100|UNAM=gnadan|EZXCLID=2|EZXCLIDVERSION=1|MSGORIGIN=1|CLIENTNAMEID=125|BOID=20211025-2-O|TCUMQ=10|TTOTEX=100|B=EB|EVT=EXEC|EXTRANS=0|EXTYP=2|OQTY=100|OTYP=2|ETIME=2021-10-25 13:09:23|VER=1|LPX=10|LSHRS=5|EID=96|TTIME=20211025-13:09:27.215|IGEN=0|CLID=EZ-20211025-3|BOID=20211025-2-O|E=EB|B=EB|EVT=EXEC|EXTRANS=0|EXTYP=2|OQTY=100|OTYP=2|ETIME=2021-10-25 13:09:23|VER=1|LPX=10|LSHRS=10|EID=97|TTIME=20211025-13:09:27.500|IGEN=0|CLID=EZ-20211025-3|BOID=20211025-2-O|E=EB|B=ORSB|VER=1|REQSTATE=ACCEPTED|CLID=EZ-20211025-3|EZXCLID=2|EZXCLIDVERSION=1|E=ORSB|UID=466|SSID=2|\003'
        msg = msg.replace('|', '\001')
        subtype = api.IserverMsgSubType.ORDERRESPONSE.value
        response = ezx_msg.decode_message(subtype, msg)
  
        executions = response.executions
        self.assertIsNotNone(executions, 'got the executions list')
        
        self.assertEqual(2, len(executions), 'parsed multiple executions')
        ex = executions[0]
        self.assertIsInstance(ex, ExecutionStatus, 'correct obj type')
        self.assertEqual(5, ex.lastShares)
        ex = executions[1]
        self.assertIsInstance(ex, ExecutionStatus, 'correct obj type')        
        self.assertEqual(10, ex.lastShares)
        
    def testEncodeOrderResponseWithMultipleExecutions(self):
        msg = 'HDLI=2|ROID=3|SEQ=19|VER=1|SIDE=2|TIF=0|OQTY=100|PX=10|OTYP=2|ACCT=5CG05400|CLID=EZ-20211025-3|COMM=0|DEST=SIMU|SYM=ABC|TXT=+B.1.a.4|CUMQ=10|EVT=EXEC|LVS=90|PENDREQ=NOPEND|STATE=PAFI|TS=2021-10-25 13:09:27|TOTEX=100|UNAM=gnadan|EZXCLID=2|EZXCLIDVERSION=1|MSGORIGIN=1|CLIENTNAMEID=125|BOID=20211025-2-O|TCUMQ=10|TTOTEX=100|B=EB|EVT=EXEC|EXTRANS=0|EXTYP=2|OQTY=100|OTYP=2|ETIME=2021-10-25 13:09:23|VER=1|LPX=10|LSHRS=5|EID=96|TTIME=20211025-13:09:27.215|IGEN=0|CLID=EZ-20211025-3|BOID=20211025-2-O|E=EB|B=EB|EVT=EXEC|EXTRANS=0|EXTYP=2|OQTY=100|OTYP=2|ETIME=2021-10-25 13:09:23|VER=1|LPX=10|LSHRS=10|EID=97|TTIME=20211025-13:09:27.500|IGEN=0|CLID=EZ-20211025-3|BOID=20211025-2-O|E=EB|B=ORSB|VER=1|REQSTATE=ACCEPTED|CLID=EZ-20211025-3|EZXCLID=2|EZXCLIDVERSION=1|E=ORSB|UID=466|SSID=2|\003'
        msg = msg.replace('|', '\001')
        subtype = api.IserverMsgSubType.ORDERRESPONSE.value
        response = ezx_msg.decode_message(subtype, msg)
        
        encoded = ezx_msg.encode(response)
        expected = 2
        actual = encoded.count("B=EB")
        message = "encoded 2 Execution blocks"
        self.assertEqual(expected, actual, message)
        
        
        response2 = ezx_msg.decode_message(subtype, encoded)
        message = f'decoding encoded message gives same result. expected={response}, was={response2}'
        self.assertEqual(response, response2, message)
        
    def testSetProperties(self):
        l = LogonRequest()
        d = { 'userName' : 'charlie', 'companyName' : 'EZX', 'logonType' : 10 }
        iserver.set_properties(l, d)
        self.assertEqual('charlie', l.userName)
        self.assertEqual('EZX', l.companyName)
        self.assertEqual(10, l.logonType)
        
    def testSetPropertiesNoException(self):
        l = LogonRequest()
        d = { 'bad_name1' : 'charlie', 'companyName' : 'EZX', 'logonType' : 10 }
        iserver.set_properties(l, d)
        # error does not prevent setting other properties
        self.assertEqual('EZX', l.companyName)
        self.assertEqual(10, l.logonType)
        
    
    def testDecodeMessageWithEqualsInValue(self):
        msg = 'MTYP=1|ROID=4|MYID=1647442993787-3|SIDE=1|SYM=AA|PX=10.1|OQTY=100|RETC=2008|RETD=failed to find account group for account=null, company=FEIS(3), order=Buy AA 100x10.10 (ROID=4, ssOrderID=4)|UNAM=Igor|STATE=REJT|LVS=0|CUMQ=0|APX=0|B=ORB|HDLI=2|MTYP=1|ROID=4|SIDE=1|TIF=0|OQTY=100|PX=10.1|OTYP=2|CLID=20220316-5|DEST=SIMU|MYID=1647442993787-3|SYM=AA|TRDR=igor|UID=7|CONAM=FEIS|COID=3|SSID=4|FIXC=simu|DESTID=150|DTGMT=1647473417902|E=ORB|UID=7|'
        msg = msg.replace('|', '\001')
        
        subtype = api.IserverMsgSubType.REJECT.value
        reject = ezx_msg.decode_message(subtype, msg)
        
        expected = 'failed to find account group for account=null, company=FEIS(3), order=Buy AA 100x10.10 (ROID=4, ssOrderID=4)'
        actual = reject.returnDesc
        self.assertEqual(expected, actual, 'decoded with = in value')
        
        
 
   


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_to_string']
    unittest.main()
