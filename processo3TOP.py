import socket
import select
import errno
import sys
from scipy import signal
import matplotlib.pyplot as plt

Kp = 2.0    # ganho
tau = 1.0   # constante de tempo
zeta = 0.25 # damping
theta = 0.0 # tempo morto
du = 1.0    # variacao de u

#funcao de transferencia
num = [Kp]
den = [tau**2,2*zeta*tau,1]
sys1 = signal.TransferFunction(num,den)

out0 = 1
in0 = 0

#interface Client do processo 3
HEADER = 10
IP = "127.0.0.1"
PORT3 = 5555

my_username = "Processo 3"

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((IP, PORT3))
c.setblocking(False)

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER}}".encode('utf-8')
c.send(username_header + username)


while True:
    if in0 > 0:

        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        out0 = in0 * sys1
        #message = message.encode('utf-8')
        message_header = f"{len(out0):<{HEADER}}".encode('utf-8')
        c.send(message_header + out0)
    try:
        
      while True:

        username_header = c.recv(HEADER)
       # retorno2 = c.recv(HEADER).decode('utf-8')
        # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(username_header):
            print('Connection closed by the server')
            sys.exit() 
        
        username_length = int(username_header.decode('utf-8').strip())
        username = c.recv(username_length).decode('utf-8')
        
        message_header = c.recv(HEADER)
        message_length = int(message_header.decode('utf-8').strip())
        in0 = c.recv(message_length).decode('utf-8')
        
        print(f'{username} > {out0}')
        
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