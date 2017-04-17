import numpy as np

ctime=np.array([])
position=np.array([])

for i in np.arange(609)+1:
    f='/data/cryo/20151204/12.04/12.04Cryo3FTS'+str(i)+'.txt'
    x=np.genfromtxt(f)
    ctime=np.concatenate((ctime,x[:,0]))
    position=np.concatenate((position,x[:,1]))
    print i

np.save('/data/cryo/20151204/ctime_fts',ctime)
np.save('/data/cryo/20151204/position_fts',position)
