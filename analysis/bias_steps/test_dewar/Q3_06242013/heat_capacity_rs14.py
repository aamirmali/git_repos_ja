import numpy as np
import matplotlib.pyplot as plt

tau_rs14=np.array([36.4 ,34.5 ,33.3 ,32.4 ,27.2 ,24.4 ,15.5, 23.5, 23.3, 21.4, 16.8, 16.5])*1e-3

G14=65e-12

biases14=[6000,5500,5000,4500,4000,3500,3000,3500, 3400, 3300, 3250,3200]

L14=np.array([-0.473,-0.472, -0.452, -0.432,-0.251, -0.204,0.300, -0.204, -0.068,-0.0015, 0.014,0.098])

C14=tau_rs14*G14*(1+L14)

fig=plt.figure(1)

ax1=fig.add_subplot(211)
ax2=fig.add_subplot(212)
ax1.plot(biases14,tau_rs14*1e3,'or',markersize=10)
ax1.invert_xaxis()
ax2.plot(L14,C14*1e12,'s',markersize=12, linewidth=8)
ax1.set_title('Dark G=65pW/K Q3 detector rs.14')
ax1.set_ylabel('Time constant (mS)')
ax1.set_xlabel('detector Bias in DACs')
ax2.set_ylabel('Heat Capacity of TES (pJ/K)')
ax2.set_xlabel(r'$\mathscr{L}_I/(1+\beta)$ from I-V')

print np.mean(C14)
plt.show()
