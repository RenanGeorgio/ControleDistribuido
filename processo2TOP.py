import socket
import select
import errno
import sys
from scipy import signal
import matplotlib.pyplot as plt

Kp = 2.0    # proporcional
Ki = 1.0   # integrativo
Kd = 0.25 # derivativo

#pid
num = [Kd, Kp, Ki]
den = [1, 0]
pid = signal.TransferFunction(num,den)

#interface Client do processo 3
HEADER = 10
IP = "127.0.0.1"
PORT3 = 4444

my_username = "Processo 2"

process_erro = -200

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((IP, PORT3))
c.setblocking(False)

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER}}".encode('utf-8')
c.send(username_header + username)


while True:

    if process_erro != -200:

        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        VC = process_erro * pid
        #message = message.encode('utf-8')
        message_header = f"{len(VC):<{HEADER}}".encode('utf-8')
        c.send(message_header + VC)
    try:
        
      while True:

        username_header = c.recv(HEADER)
        #retorno3 = c.recv(HEADER).decode('utf-8')
        # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(username_header):
            print('Connection closed by the server')
            sys.exit() 
        
        username_length = int(username_header.decode('utf-8').strip())
        username = c.recv(username_length).decode('utf-8')
        
        message_header = c.recv(HEADER)
        message_length = int(message_header.decode('utf-8').strip())
        process_erro = c.recv(message_length)
        
        print(f'{username} > {process_erro}')
        
    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data, error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()    