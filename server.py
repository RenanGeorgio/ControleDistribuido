import socket
import select

HEADER_LENGTH = 20

IP = "127.0.0.1"
PORT1 = 3333
PORT2 = 4444
PORT3 = 5555


# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket1.bind((IP, PORT1))
server_socket2.bind((IP, PORT2))
server_socket3.bind((IP, PORT3))

# This makes server listen to new connections
server_socket1.listen()
server_socket2.listen()
server_socket3.listen()

# List of sockets for select.select()
sockets_list = [server_socket1, server_socket2, server_socket3]

# List of connected clients - socket as a key, user header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT1}, {PORT2}, {PORT3}...')

# Handles message receiving
def receive_message(client_socket):

    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False

while True:

    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket1:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket1, client_address1 = server_socket1.accept()

            # Client should send his name right away, receive it
            user1 = receive_message(client_socket1)

            # If False - client disconnected before he sent his name
            if user1 is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket1)

            # Also save username and username header
            clients[client_socket1] = user1
            
            process1 = client_socket1
            
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address1, user1['data'].decode('utf-8')))
        
            #server_socket2.send('veio do processo 1')
            
        elif notified_socket == server_socket2:
            client_socket2, client_address2 = server_socket2.accept()

            # Client should send his name right away, receive it
            user2 = receive_message(client_socket2)

            # If False - client disconnected before he sent his name
            if user2 is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket2)

            # Also save username and username header
            clients[client_socket2] = user2
            
            process2 = client_socket2

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address2, user2['data'].decode('utf-8')))
        
            #server_socket3.send('veio do processo 2')
            
        elif notified_socket == server_socket3:
            client_socket3, client_address3 = server_socket3.accept()

            # Client should send his name right away, receive it
            user3 = receive_message(client_socket3)

            # If False - client disconnected before he sent his name
            if user3 is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket3)

            # Also save username and username header
            clients[client_socket3] = user3
            
            process3 = client_socket3

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address3, user3['data'].decode('utf-8')))
            
            #server_socket1.send(b'1')
            
        # Else existing socket is sending a message
        else:
            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]
            
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Iterate over connected clients and broadcast message
            for client_socket in clients:

                # But don't sent it to sender
                if client_socket == client_socket1:

                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket2.send(user['header'] + user['data'] + message['header'] + message['data'])
                    
                elif client_socket == client_socket2:

                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket3.send(user['header'] + user['data'] + message['header'] + message['data'])

                else:

                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket1.send(user['header'] + user['data'] + message['header'] + message['data'])
                    
    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]