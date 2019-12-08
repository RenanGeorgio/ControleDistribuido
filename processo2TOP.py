import socket
import select
import errno
import sys
import numpy as np
import control
import control.matlab

Kp = 2.0    # proporcional
Ki = 1.0   # integrativo
Kd = 0.25 # derivativo

#pid
num = np.array([0, 1, 0])
den = np.array([Kd, Kp, Ki])

signalOut = {}
out0 = 1
#interface Client do processo 3
HEADER = 20
IP = "127.0.0.1"
PORT2 = 4444
PORT3 = 8888

my_username = "Processo 2"
timeout = 10
process_erro = 1

c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

c2.connect((IP, PORT2))
c3.connect((IP, PORT3))

c2.setblocking(False)
c3.setblocking(False)

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER}}".encode('utf-8')
c2.send(username_header + username)
c3.send(username_header + username)

print(f'{my_username} > ')

while True:
    ready_sockets, _, _ = select.select([c2], [], [c2])
    
    if ready_sockets:
        out1 = float(process_erro) * num
        sys1 = control.matlab.tf(out1,den)
        ganho = control.matlab.step(sys1)
        z1, z2 = ganho
        out2 = z1.max()
        print('step1')
        print(out2)
        if out2 > 0:    
            num_err0 =  float(out2)
        else:
            num_err0 = 1
            
        num_err0 = str(num_err0)
        message_header = f"{len(num_err0):<{HEADER}}".encode('utf-8')
        c3.send(message_header + num_err0.encode('utf-8'))
    else:
        print('sem mensagem')
        
    try:
        
      while True:

        username_header = c2.recv(HEADER)

        if not len(username_header):
            print('Conexao finalizada pelo server')
            sys.exit() 
        
        username_length = int(username_header.decode('utf-8').strip())
        username = c2.recv(username_length).decode('utf-8')
        
        message_header = c2.recv(HEADER)
        message_length = int(message_header.decode('utf-8').strip())
        process_erro = c2.recv(message_length)
        process_erro = process_erro.decode('utf-8')
        
        print(f'{username} > {process_erro}')
        
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Erro de leitura: {}'.format(str(e)))
            sys.exit()

        continue

    except Exception as e:
        print('Erro de leitura: '.format(str(e)))
        sys.exit()    