import socket
import select
import numpy as np
from scipy import signal
import control
import control.matlab

HEADER_LENGTH = 20

IP = "127.0.0.1"
PORT1 = 6666
PORT2 = 8888

Kp = 2.0    # ganho
tau = 1.0   # constante de tempo
zeta = 0.25 # damping
theta = 0.0 # tempo morto
du = 1.0    # variacao de u

#funcao de transferencia
num = np.array([0,0,Kp])
den = np.array([1,0.25,1])

in0 = 1
out0 = 1
timeout = 10
controle0 = 10

my_username = "Processo 3"

# Cria o socket
server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket1.bind((IP, PORT1))
server_socket2.bind((IP, PORT2))

server_socket1.listen()
server_socket2.listen()

# Lista de sockets
sockets_list = [server_socket1, server_socket2]

# Lista de clientes conectados
clients = {}
print(f'{my_username} > ')
print(f'Escutando conexoes de {IP}:{PORT1}, {PORT2}...')

def receive_message(client_socket):

    try:

        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False
        
        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    # Iteracao sobre sockets notificados
    for notified_socket in read_sockets:

        #se o socket notificado e um socket uma nova conexao e estabelecida
        if notified_socket == server_socket1:

            #conexao estabelecida com socket client
            client_socket1, client_address1 = server_socket1.accept()

            #client enviando seu nome 
            user1 = receive_message(client_socket1)

            if user1 is False:
                continue

            #com a conexao feita o client e anexado a lista de sockets
            sockets_list.append(client_socket1)

            #salva o nome e o header
            clients[client_socket1] = user1
            
            process1 = client_socket1
            
            print('Nova conexao aceita com {}:{}, username: {}'.format(*client_address1, user1['data'].decode('utf-8')))
            
        elif notified_socket == server_socket2:
            client_socket2, client_address2 = server_socket2.accept()

            # cliente enviando seu nome
            user2 = receive_message(client_socket2)

            if user2 is False:
                continue

            #com a conexao feita o client e anexado a lista de sockets
            sockets_list.append(client_socket2)

            #salva nome e o header
            clients[client_socket2] = user2
            
            process2 = client_socket2

            print('Nova conexao aceita com {}:{}, username: {}'.format(*client_address2, user2['data'].decode('utf-8')))
            
        # Else:sockeg enviando mensagem
        else:
            #Mensagem recebida
            message = receive_message(notified_socket)

            #cliente desconectou
            if message is False:
                print('Encerrando conexao com: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                #removendo da lista
                sockets_list.remove(notified_socket)

                #removendo da lista de usuarios
                del clients[notified_socket]

                continue

            #descobrindo o usuario por meio do socket que foi notificado
            user = clients[notified_socket]
            
            PLUS = float(message["data"].decode('utf-8')) * num
            sys1 = control.matlab.tf(PLUS,den)
            out0 = control.matlab.step(sys1)
            x1, x2 = out0
            y1 = x1.max()
           # print('maximo')
            #print(y1)
            
            if y1 > 0:
                process_out = float(y1)
            else:
                process_out = 1
                
            process_out = str(process_out)
                    
            message["data"] = process_out.encode('utf-8')
            
            print(f'Recendo mensagem de {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            # interando por clients e fazendo broadcast das mensagens
            for client_socket in clients:

                # nao enviando para quem a enviou
              if client_socket == client_socket2:

                  client_socket1.send(user1['header'] + user1['data'] + message['header'] + message['data'])
                  break
                    
              else:
                  print('Problemas no recebimento de mensagem')
                    
    for notified_socket in exception_sockets:

        # Removendo da lista de sockets
        sockets_list.remove(notified_socket)

        # Removendo da lista de usuarios
        del clients[notified_socket]