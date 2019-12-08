import socket
import errno
import sys
import matplotlib.pyplot as plt
import numpy as np

HEADER_LENGTH = 20

IP = "127.0.0.1"
PORT1 = 3333
PORT3 = 6666
my_username = "Processo 1"

sysOut = 0
# Criando socket
client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket1.connect((IP, PORT1))
client_socket3.connect((IP, PORT3))

client_socket1.setblocking(False)
client_socket3.setblocking(False)

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket1.send(username_header + username)
client_socket3.send(username_header + username)

while True:
    setP = int(float(input(f'{my_username} > ')))
    set_point = setP
    
    if set_point:
        PLUS = set_point - float(sysOut)
        PLUS = abs(PLUS)
        process_erro = str(PLUS)
        message_header = f"{len(process_erro):<{HEADER_LENGTH}}".encode('utf-8')
         
        client_socket1.send(username_header + process_erro.encode('utf-8'))

    try:
        #loop sobre as mesnagens recebidas
        while True:

            # Recebe header
            username_header = client_socket3.recv(HEADER_LENGTH)

            if not len(username_header):
                print('Conexao encerrada pelo server')
                sys.exit()

            username_length = int(username_header.decode('utf-8').strip())

            # Recebendo e decodificando o username
            username = client_socket3.recv(username_length).decode('utf-8')

            message_header = client_socket3.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            sysOut = client_socket3.recv(message_length)
            sysOut = sysOut.decode('utf-8')
            
            print(f'{username} > {sysOut}')
            
            # Plot
            t = np.linspace(0,10,10)
            tSys = np.linspace(float(sysOut),float(sysOut),10)
            plt.plot(t,tSys)
            plt.ylabel('Processo')
            plt.legend(['SetPoint'],loc='best')
            plt.xlabel('N')
            plt.show()

    except IOError as e:

        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Erro de leitura: {}'.format(str(e)))
            sys.exit()

        # Se nao recebermos nada
        continue

    except Exception as e:
        print('Erro de leitura: '.format(str(e)))
        sys.exit()