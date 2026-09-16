import matplotlib.pyplot as plt
import numpy as np

x = np.arange(100)
y = np.arange(100)
X, Y = np.meshgrid(x, y)
vX = np.random.rand(100, 100)
vY = np.random.rand(100, 100)




V = np.sqrt(vX**2 + vY**2)

n = 100
m = 100
p = 0.02

# make me an nxm array of random numbers either true or false with probability p
mask = np.random.rand(n, m) < p

fig = plt.figure()
ax1 = fig.add_subplot(111)
q = ax1.quiver(X[mask], Y[mask], vX[mask]*10, vY[mask]*10)

ax1.quiverkey(q, X=0.85, Y=1.05, U=V.max(), 
    label=f'{V.max()} m/s', labelpos='E', 
    fontproperties={'weight': 'bold'})

plt.show()
