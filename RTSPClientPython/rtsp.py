import io, socket
from threading import Thread
import _thread

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
        self.session = session

        # TODO
        

    def send_request(self, command, include_session=True, extra_headers=None):
        '''Helper function that generates an RTSP request and sends it to the
        RTSP connection.
        '''
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

        # TODO

    def play(self):
        '''Sends a PLAY request to the server. This method is responsible for
	sending the request, receiving the response and, in case of a
	successful response, starting the RTP timer responsible for
	receiving RTP packets with frames.
        '''

        # TODO

    def pause(self):
        '''Sends a PAUSE request to the server. This method is responsible for
	sending the request, receiving the response and, in case of a
	successful response, cancelling the RTP thread responsible for
	receiving RTP packets with frames.
        '''

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

        # TODO

    def close(self):
        '''Closes the connection with the RTSP server. This method should also
	close any open resource associated to this connection, such as
	the RTP connection, if it is still open.
        '''

        # TODO
        
