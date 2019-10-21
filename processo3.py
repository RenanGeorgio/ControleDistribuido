from scipy import signal
import matplotlib.pyplot as plt
import socket

Kp = 2.0    # ganho
tau = 1.0   # constante de tempo
zeta = 0.25 # damping
theta = 0.0 # tempo morto
du = 1.0    # variacao de u

#funcao de transferencia
num = [Kp]
den = [tau**2,2*zeta*tau,1]
sys1 = signal.TransferFunction(num,den)

#processo 3
s3 = socket.socket()
s3.bind(("192.168.2.64",5009))
s3.listen(5)

#processo 1(erro)
s1 = socket.socket()
s1.connect(("192.168.3.127",55555))

sc3, addr3 = s3.accept()

while True:
   In = sc3.recv(4096)
   sys2 = In * sys1
   t1,y1 = signal.step(sys2)
   s1.send(y1)

sc3.close()
s3.close()
s1.close()

plt.figure(1)
plt.plot(t1,y1*du,'b--',linewidth=3,label='Transfer Fcn')
y_ss = Kp * du
plt.plot([0,max(t1)],[y_ss,y_ss],'k:')
plt.xlim([0,max(t1)])
plt.xlabel('Time')
plt.ylabel('Response (y)')
plt.legend(loc='best')
plt.savefig('2nd_order.png')
plt.show()