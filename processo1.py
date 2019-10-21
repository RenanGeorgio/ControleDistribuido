import socket

#processo 3(planta)
s1 = socket.socket()
s1.bind(("192.168.3.127",55555))
s1.listen(5)

#processo 2(controle)
s2 = socket.socket()
s2.connect(("192.168.1.32",65009))

#abrindo conexao
sc1, addr1 = s1.accept()

while True:
   #setpoint obtido do teclado
   Xi = input()

   Xo = sc1.recv(4096)
   e = Xi - Xo
   s2.send(e)

sc1.close()
s1.close()
s2.close()

