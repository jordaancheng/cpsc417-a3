import io, socket
from threading import Thread
import _thread
import socket 

class RTSPException(Exception):
    def __init__(self, response):
        super().__init__(f'Server error: {response.message} (error code: {response.response_code})')

class Response:
    def __init__(self, reader):
        '''Reads and parses the data associated to an RTSP response'''
        first_line = reader.readline().split(' ', 2)
        if len(first_line) != 3:
            raise Exception('Invalid response format. Expected first line with version, code and message')
        self.version, _, self.message = first_line
        if self.version != 'RTSP/1.0':
            raise Exception('Invalid response version. Expected RTSP/1.0')
        self.response_code = int(first_line[1])
        self.headers = {}
        
        while True:
            line = reader.readline().strip()
            if not line or ':' not in line: break
            hdr_name, hdr_value = line.split(':', 1)
            self.headers[hdr_name.lower()] = hdr_value
            if hdr_name.lower() == 'cseq':
                self.cseq = int(hdr_value)
            elif hdr_name.lower() == 'session':
                self.session_id = int(hdr_value)
        
        if self.response_code != 200:
            raise RTSPException(self)
    
class Connection:
    BUFFER_LENGTH = 0x10000

    def __init__(self, session, address):
        '''Establishes a new connection with an RTSP server. No message is
	sent at this point, and no stream is set up.
        '''
        self.session_id = None
        self.client_port = 2502
        self.msg = None
        self.state = 'INIT'
        self.cseq = 0
        self.session = session
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(address[0], address[1])
        addrr = str(address[0])
        port = int(address[1])
        self.sock.connect((addrr, port))
        self.rtpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.end_rtp_conn = False
        # self.sock.connect
        # TODO
        
    def listen_rtp(self, port):
        print("listen_rtp")
        while(not self.end_rtp_conn):
            print("LISTENING ON: ", self.rtpsocket.getsockname()[1])
            try:
                data = self.rtpsocket.recv(Connection.BUFFER_LENGTH)
            except:
                pass
            self.process_rtp_msg(data)

    def process_rtp_msg(self, packet):
        cc = 0b00001111 & packet[0]
        m = 0b10000000 & packet[1]
        m = m >> 6
        pt = 0b01111111 & packet[1]
        sq = (packet[2] << 8) + packet[3]
        tmp_stamp = (packet[4] << 24) + (packet[5] << 16) + (packet[6] << 8) + packet[7]
        startofpayload = 12 + cc*4
        payload = packet[startofpayload:]
        print("payload: ", payload)
        print("cc: ", cc)
        print("pt: ", pt)
        print("m: ", m)
        print("sq: ", sq)
        print("tmp_stamp: ", tmp_stamp)
        self.session.process_frame(pt, m, sq, tmp_stamp, payload)
        
    def send_request(self, command, include_session=True, extra_headers=None):
        '''Helper function that generates an RTSP request and sends it to the
        RTSP connection.
        '''
        totalsent = 0
        MSGLEN = len(command)
        print("MSGLEN",MSGLEN)
        while totalsent < MSGLEN:
            sent = self.sock.send(command[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        print(sent)
        # TODO

    def start_rtp_timer(self):
        '''Starts a thread that reads RTP packets repeatedly and process the
	corresponding frame (method ). The data received from the
	datagram socket is assumed to be no larger than BUFFER_LENGTH
	bytes. This data is then parsed into its useful components,
	and the method `self.session.process_frame()` is called with
	the resulting data. In case of timeout no exception should be
	thrown.
        '''
        _thread.start_new_thread( self.listen_rtp, (self.client_port, ) )
        print("END OF THREAD")
        # TODO

    def stop_rtp_timer(self):
        '''Stops the thread that reads RTP packets'''
        # TODO

    def setup(self):
        '''Sends a SETUP request to the server. This method is responsible for
	sending the SETUP request, receiving the response and
	retrieving the session identification to be used in future
	messages. It is also responsible for establishing an RTP
	datagram socket to be used for data transmission by the
	server. The datagram socket should be created with a random
	UDP port number, and the port number used in that connection
	has to be sent to the RTSP server for setup. This datagram
	socket should also be defined to timeout after 1 second if no
	packet is received.
        '''
        if (self.state != 'INIT'):
            return
        self.cseq += 1
        self.rtpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtpsocket.bind(('localhost', 0))
        self.client_port =self.rtpsocket.getsockname()[1]
        self.msg = 'SETUP ' + self.session.video_name + ' RTSP/1.0'
        self.msg += '\n' + 'CSeq:' + str(self.cseq) + '\n' + 'Transport: RTP/UDP; client_port= ' + str(self.client_port) + '\n\n' 

        print(self.msg)
        self.send_request(self.msg.encode())
        response = self.process_recvd_msg()
        if(response is None):
            return
        self.session_id = response.session_id
        print(response.session_id)
        self.state = 'READY'
        print("state = READY")
        # TODO

    def play(self):
        '''Sends a PLAY request to the server. This method is responsible for
	sending the request, receiving the response and, in case of a
	successful response, starting the RTP timer responsible for
	receiving RTP packets with frames.
        '''
        if (self.state != 'READY'):
            return
        self.end_rtp_conn = False
        self.start_rtp_timer()
        self.cseq += 1
        self.msg = 'PLAY ' + self.session.video_name + ' RTSP/1.0'
        self.msg += '\n' + 'CSeq: ' + str(self.cseq) + '\n' + 'Session: ' + str(self.session_id) + '\n\n' 
        self.send_request(self.msg.encode())
        print("state = PLAYING")
        self.state = 'PLAYING'
        # TODO

    def pause(self):
        '''Sends a PAUSE request to the server. This method is responsible for
	sending the request, receiving the response and, in case of a
	successful response, cancelling the RTP thread responsible for
	receiving RTP packets with frames.
        '''
        if (self.state != 'PLAYING'):
            return
        self.cseq += 1
        self.msg = 'PAUSE ' + self.session.video_name + ' RTSP/1.0'
        self.msg += '\n' + 'CSeq: ' + str(self.cseq) + '\n' + 'Session: ' + str(self.session_id) + '\n\n' 
        self.send_request(self.msg.encode())
        print("state = READY")
        self.state = 'READY'

        # TODO

    def teardown(self):
        '''Sends a TEARDOWN request to the server. This method is responsible
	for sending the request, receiving the response and, in case
	of a successful response, closing the RTP socket. This method
	does not close the RTSP connection, and a further SETUP in the
	same connection should be accepted. Also this method can be
	called both for a paused and for a playing stream, so the
	timer responsible for receiving RTP packets will also be
	cancelled.
        '''
        if (self.state != 'PLAYING' and self.state != 'READY'):
            return
        self.cseq += 1
        self.msg = 'TEARDOWN ' + self.session.video_name + ' RTSP/1.0'
        self.msg += '\n' + 'CSeq: ' + str(self.cseq) + '\n' + 'Session: ' + str(self.session_id) + '\n\n' 
        self.send_request(self.msg.encode())
        print("state = INIT")
        self.state = 'INIT'
        self.cseq = 1 
        self.rtpsocket.close()
        self.end_rtp_conn = True
        # TODO

    def close(self):
        '''Closes the connection with the RTSP server. This method should also
	close any open resource associated to this connection, such as
	the RTP connection, if it is still open.
        '''
        self.sock.close()
        self.rtpsocket.close()
        self.end_rtp_conn = True
        # TODO

    def process_recvd_msg(self):
        chunk = self.sock.recv(1024)
        msgbuff = io.StringIO(chunk.decode("utf-8"))
        print(chunk)
        response = Response(msgbuff)
        print("cseq", self.cseq)
        print("response.cseq", response.cseq)
        if (self.cseq != response.cseq):
            return None
        if (self.session_id is not None and self.session_id == response.session_id):
            return response
        elif (self.session_id is None):
            return response
        else:
            return None
