from simple_pid import PID
import socket

#processo 1(erro)
s2 = socket.socket()
s2.bind(("192.168.1.32",65009))
s2.listen(5)

#processo 3(planta)
s3 = socket.socket()
s3.connect(("192.168.2.64",5009))

#inicia conexao com processo 1
sc2, addr2 = s2.accept()

pid = PID(1, 0.1, 0.05, sample_time=0.01)


while True:
    # aplica o PID no valor atual da planta
   Xf = sc2.recv(1024)
   control = pid(Xf)
    
   s3.send(control)

sc2.close()
s2.close()
s3.close()