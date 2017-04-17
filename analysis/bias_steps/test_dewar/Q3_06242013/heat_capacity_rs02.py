import numpy as np
import matplotlib.pyplot as plt

tau_rs02=np.array([28.4,  25.4,  23.3,  22.5,  21.1,  21.,   19.8])*1e-3

G2=65e-12

biases2=[3200,3100,3000,2900,2850,2800,2750]

L2=np.array([-0.333,-0.266,-0.198,-0.164,-0.056, 0.011,0.09])

C2=tau_rs02*G2*(1+L2)

fig=plt.figure(1)

ax1=fig.add_subplot(211)
ax2=fig.add_subplot(212)
ax1.plot(biases2,tau_rs02*1e3,'or',markersize=10)
ax1.invert_xaxis()
ax2.plot(L2,C2*1e12,'s',markersize=12, linewidth=8)
ax1.set_title('Dark G=65pW/K Q3 detector rs.02')
ax1.set_ylabel('Time constant (mS)')
ax1.set_xlabel('detector Bias in DACs')
ax2.set_ylabel('Heat Capacity of TES (pJ/K)')
ax2.set_xlabel(r'$\mathscr{L}_I/(1+\beta)$ from I-V')

print np.mean(C2)
plt.show()

