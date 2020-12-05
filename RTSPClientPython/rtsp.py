import io, socket
from threading import Thread
import _thread
import socket 
import time


class Packet:
    def __init__(self, pt, m, sq, tmp_stamp, payload):
        self.pt = pt
        self.m = m
        self.sq = sq
        self.tmp_stamp = tmp_stamp
        self.payload = payload

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
        self.num_pkts = 0
        self.time_start = 0
        self.time_end = 0
        self.session_id = None
        self.client_port = 2502
        self.msg = None
        self.state = 'INIT'
        self.cseq = 0
        self.session = session
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(address[0], address[1], "\n")
        addrr = str(address[0])
        port = int(address[1])
        self.sock.connect((addrr, port))
        self.end_rtp_conn = False
        self.sq = 0
        self._max_sq = -1
        self.packet_queue = []
        self.thread_listening = None
        self.thread_processing = None

        # TODO

    def process_pkt(self):
        '''This thread will process packets in queue in 40 ms intervals
        this new thread is to remedy the problems caused by the 
        funky server such as burst of packets arriving and out of order packets'''
        dummy_item = Packet(-2, -2, -2, -2, -2)
        while(not self.end_rtp_conn):
            time.sleep(0.04)
            while(not self.end_rtp_conn):
                self.packet_queue.sort(key=lambda x: x.sq)
                try:
                    item = self.packet_queue.pop(0)
                except:
                    item = dummy_item
                if (item.sq > self._max_sq):
                    self._max_sq = item.sq
                    self.session.process_frame(item.pt, item.m, item.sq, item.tmp_stamp, item.payload)
                    break

    def listen_rtp(self):
        '''This thread listens for packes on the rtp socket and process them'''
        prev_time = self.time_start
        time_lapsed = 0
        while(not self.end_rtp_conn):
            try:
                data = self.rtpsocket.recv(Connection.BUFFER_LENGTH)
                time_lapsed = time.time()-prev_time
                prev_time = time.time()
                self.process_rtp_msg(data)
            except:
                print("Error: An exception occurred in listen_rtp()")

    def process_rtp_msg(self, packet): 
        # retrieves the needed info from the packet
        self.num_pkts += 1
        cc = 0b00001111 & packet[0]
        m = 0b10000000 & packet[1]
        m = m >> 6
        pt = 0b01111111 & packet[1]
        sq = (packet[2] << 8) + packet[3]
        tmp_stamp = (packet[4] << 24) + (packet[5] << 16) + (packet[6] << 8) + packet[7]
        startofpayload = 12 + cc*4
        payload = packet[startofpayload:]
        packet = Packet(pt, m, sq, tmp_stamp, payload)
        self.packet_queue.append(packet)
        self.sq = sq
        
    def send_request(self, command, include_session=True, extra_headers=None):
        '''Helper function that generates an RTSP request and sends it to the
        RTSP connection.
        '''
        msg = command + ' ' + self.session.video_name + ' ' + 'RTSP/1.0\n'
        msg += 'CSeq: ' + str(self.cseq) + '\n'
        if (include_session):
            msg += 'Session: ' + str(self.session_id) + '\n\n'
        elif (extra_headers is not None):
            msg += extra_headers
        msg = msg.encode()
        sent = self.sock.send(msg)
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def start_rtp_timer(self):
        '''Starts a thread that reads RTP packets repeatedly and process the
	corresponding frame (method ). The data received from the
	datagram socket is assumed to be no larger than BUFFER_LENGTH
	bytes. This data is then parsed into its useful components,
	and the method `self.session.process_frame()` is called with
	the resulting data. In case of timeout no exception should be
	thrown.
        '''
        self.end_rtp_conn = False
        self.time_start = time.time()
        self.thread_listening = Thread(target=self.listen_rtp, args=())
        self.thread_processing = Thread(target=self.process_pkt, args=())
        self.thread_listening.start()
        self.thread_processing.start()
        # TODO

    def stop_rtp_timer(self):
        self.end_rtp_conn = True
        self.time_end = time.time()
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

        # establishes an RTP datagram socket (using UDP)
        self.rtpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtpsocket.bind(('localhost', 0))
        self.client_port = self.rtpsocket.getsockname()[1]

        header = 'Transport: RTP/UDP; client_port= '+ str(self.client_port) + '\n\n'
        self.send_request('SETUP', False, header)
        
        # receive & print server SETUP reply
        response = self.process_received_msg()
        if(response is None):
            return
        self.print_server_reply(response)

        # session id becomes the one returned by server
        self.session_id = response.session_id
        self.state = 'READY'
        # TODO

    def play(self):
        '''Sends a PLAY request to the server. This method is responsible for
	sending the request, receiving the response and, in case of a
	successful response, starting the RTP timer responsible for
	receiving RTP packets with frames.
        '''
        if (self.state != 'READY'):
            return
        self.cseq += 1
        # print & send PLAY message
        self.send_request('PLAY', True)

        # receive & print server PLAY reply
        response = self.process_received_msg()
        if(response is None):
            return
        self.print_server_reply(response)

        self.start_rtp_timer()
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

        # print & send PAUSE message
        print(self.msg)
        self.send_request('PAUSE', True)

        # receive & print server PAUSE reply
        response = self.process_received_msg()
        if(response is None):
            return
        self.print_server_reply(response)
        self.stop_rtp_timer()
        self.state = 'READY'
        rate = self.num_pkts/(self.time_end - self.time_start)
        print("FRAME RATE: ", rate)
        print("LOSS RATE: ", self.num_pkts/self.sq)
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

        # print & send TEARDOWN message
        # receive & print server PAUSE reply
        self.send_request('TEARDOWN', True)
        response = self.process_received_msg()
        if(response is None):
            return
        self.print_server_reply(response)

        self.rtpsocket.close()
        self.state = 'INIT'
        self.session_id = None
        self.stop_rtp_timer()
        self.sq = 0
        self._max_sq = -1
        self.packet_queue = []
        # TODO

    def close(self):
        '''Closes the connection with the RTSP server. This method should also
	close any open resource associated to this connection, such as
	the RTP connection, if it is still open.
        '''
        self.cseq = 1
        self.rtpsocket.close()
        self.sock.close()
        self.state = 'INIT'
        self.stop_rtp_timer()
        # TODO

    def process_received_msg(self):
        chunk = self.sock.recv(1024)
        msgbuff = io.StringIO(chunk.decode("utf-8"))
        response = Response(msgbuff)
        if (self.cseq != response.cseq):
            return None
        if (self.session_id is not None and self.session_id == response.session_id):
            return response
        elif (self.session_id is None):
            return response
        else:
            return None

    def print_server_reply(self, response):
        server_reply = "%s %d %s" % (response.version, response.response_code, response.message)
        server_reply += "CSeq: %d\n" % response.cseq
        server_reply += "Session %d" % response.session_id
        print(server_reply)


