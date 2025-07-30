text = """
This Tutorial cover using vorticity based method to estimate forces over
an object in a 2D flow. There is included the unfinished volume control
method, which is unusable unless you already have the pressure field.

Samples of the flow over an object are not included in order to keep the
library as light as possible. However, it should be easy addapt this script
to your own data.

This message appears only becouse the data is not correct, copy the original
file and addapt it to your own data.

All methods are a dimensional adaptation of some of the methods shown in
Martín-Alcántara, A., & Fernandez-Feria, R. (2019). Assessment of two
vortex formulations for computing forces of a flapping foil at high Reynolds
numbers. Physical Review Fluids, 4(2), 024702.
"""
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

import dpivsoft.Postprocessing as post
import dpivsoft.meshTools as mt

#Plot control
AXESW = 1.5
TICKL = 6.0
TICKD = 'in'
SMALL_SIZE = 10
MEDIUM_SIZE = 12
BIGGER_SIZE = 14

plt.rc('font',   size=BIGGER_SIZE)
plt.rc('axes',   titlesize=BIGGER_SIZE)
plt.rc('axes',   labelsize=BIGGER_SIZE)
plt.rc('xtick',  labelsize=BIGGER_SIZE)
plt.rc('ytick',  labelsize=BIGGER_SIZE)
plt.rc('legend', fontsize=BIGGER_SIZE)
plt.rc('figure', titlesize=BIGGER_SIZE)
plt.rcParams['axes.linewidth'] = AXESW

#=============================================================================
# WORKING PATHS
#=============================================================================
dirCode = os.getcwd()   #Current path
dirSave = dirCode + "/Results/Forces" #Images folder
dirFlow = '/mnt/Almacen/Universidad/Doctorado/Forces/Interpolated/Re100_N20C'

#=============================================================================
# READING VELOCITY FIELD
#=============================================================================
try:
    # Read velocity field. Example using a non included OpenFoam simulation
    # saved on a meshgrid for testing. You can use any meshgrid type velocity
    # field.
    [X, Y, U, V, Omega, P, Name] = mt.Read_Mesh(dirFlow)

    x_l = [-3,3]
    y_l = [-3,3]

    #Define sub_square to perform calculations
    pos1, pos2 = np.where((X>=x_l[0])&(X<=x_l[1])&(Y>=y_l[0])&(Y<=y_l[1]))
    x = X[pos1[0]:pos1[-1]+1, pos2[0]:pos2[-1]+1]
    y = Y[pos1[0]:pos1[-1]+1, pos2[0]:pos2[-1]+1]
    u = U[pos1[0]:pos1[-1]+1, pos2[0]:pos2[-1]+1,:]
    v = V[pos1[0]:pos1[-1]+1, pos2[0]:pos2[-1]+1,:]
    p = P[pos1[0]:pos1[-1]+1, pos2[0]:pos2[-1]+1,:]
    omega = Omega[pos1[0]:pos1[-1]+1, pos2[0]:pos2[-1]+1,:]

except:
    print(text)
    sys.exit()

#=============================================================================
# PROBLEM DEFINITION
#=============================================================================
# Define shape of object to calculate forces on
points=[(0.5,-0.5,0), (0.5,0.5,0), (-0.5,0.5,0), (-0.5,-0.5,0)]

#Data of the problem for force calculation
t = np.arange(len(Name))*0.05 # Time vector
accel = np.zeros([len(Name),2])  # Aceleration vector (only if moving reference frame)

mu = 0.01 # Viscosity
U_inf = 1 # Characteristic velocity
rho = 1 # Density
c = 1 # Characteristic length (Chord)

#====================================================================
# PROJECTION METHOD
#====================================================================
# Create Mesh to apply FEM method
size = 4  # how many chords in all directions are used
tm =0.1  # element size of the mesh in the outbound
tmr = 0.005 # element size of the mesh in the object

# Solve Chang functions on mesh
fileName = "object.msh"
meshFile = dirSave + '/' + fileName

if not os.path.exists(dirSave):
    os.makedirs(dirSave)

# Generation of finite element mesh to calculate projection functions
mt.mesh_generator('polygon', dirSave, c=c, size=size, tm=tm,
        points=points, tmr=tmr, visualize=0, filename=fileName)

# Projection functions calculations over the unstructured mesh
[mesh, mesh_cell, mesh_elem, phi, grad_phi, added_mass] = mt.projection_FEM_Solver(
        meshFile, dirSave, visualize=0)

# Interpolation of projection functions into PIV grid
phi, grad_phi = mt.projectionMesh2Grid(
        mesh_elem, grad_phi, x, y, points)

# Forces calculation following projection method
FP, FPv, FPmu, FPam = post.ProjectionMethod(x, y, u, v, omega, grad_phi,
        rho, mu, points, accel)

fig, (ax1,ax2) = plt.subplots(2,1)
ax1.plot(t,FP[:,0],'k',
         t,FPv[:,0],'b--',
         t, FPam[:,1], 'r:',
         t,FPmu[:,0],'g-.')
ax1.set_xlabel('t(s)',fontsize=14)
ax1.set_ylabel('$F_x$',fontsize=14)
ax1.legend(['$F_{total}$','$F_v$','$F_{\mu}$', '$F_{am}$'])
ax1.set_title('PROJECTION METHOD')
ax1.tick_params(direction=TICKD,right=True, top=True, length=TICKL, width=AXESW)

ax2.plot(t,FP[:,1],'k',
         t,FPv[:,1],'b--',
         t, FPam[:,1], 'r:',
         t,FPmu[:,1],'g-.')
ax2.set_xlabel('t(s)',fontsize=14)
ax2.set_ylabel('$F_y$',fontsize=14)
ax2.tick_params(direction=TICKD,right=True, top=True, length=TICKL, width=AXESW)
plt.tight_layout()
plt.show()

#====================================================================
# IMPULSE METHOD
#====================================================================
# Calculation of forces using Impulse method
[F_V, F_i, Fsol, F_oe, F_mu] = post.ImpulseMethod(
        x, y, u, v, omega, rho, c*c, mu, points, t)

FI = F_V+F_i+Fsol+F_oe+F_mu

fig, (ax1,ax2) = plt.subplots(2,1)
ax1.plot(t, FI[:,0], 'k-',
         t, F_V[:,0], 'b--',
         t, F_i[:,0], 'g-.',
         t, F_oe[:,0], 'c--',
         t, F_mu[:,0], 'r:',
         t, Fsol[:,0], 'm-')
ax1.set_xlabel('t(s)',fontsize=14)
ax1.set_ylabel('$F_x$',fontsize=14)
ax1.legend(['$F_{total}$','$F_v$','$F_i$','$F_{oe}$','$F_{sol}$','$F_{Re}$'])
ax1.set_title('IMPULSE METHOD')
ax1.tick_params(direction=TICKD,right=True, top=True, length=TICKL, width=AXESW)

ax2.plot(t, FI[:,1], 'k-',
         t, F_V[:,1], 'b--',
         t, F_i[:,1], 'g-.',
         t, F_oe[:,1], 'c--',
         t, F_mu[:,1], 'r:',
         t, Fsol[:,1], 'm-')
ax2.set_xlabel('t(s)',fontsize=14)
ax2.set_ylabel('$F_y$',fontsize=14)
ax2.tick_params(direction=TICKD,right=True, top=True, length=TICKL, width=AXESW)
plt.tight_layout()
plt.show()

#====================================================================
# CONTROL VOLUMEN
#====================================================================
# Calculation of forces using control volume method
Ftot, FV, FSo, Fmu, Fp, Fm = post.ControlVolume(
        x, y, u, v, rho, mu, t, accel, p)

fig, (ax1,ax2) = plt.subplots(2,1)
ax1.plot(t, Ftot[:,0], 'k-',
         t, FV[:,0], 'b--',
         t, FSo[:,0], 'g-.',
         t, Fmu[:,0], 'c-.',
         t, Fp[:,0], 'r:',
         t, Fm[:,0], 'm-')
ax1.set_xlabel('t(s)',fontsize=14)
ax1.set_ylabel('$F_x$',fontsize=14)
ax1.legend(['$F_{tot}$','$F_V$','$F_{So}$','$F_{\mu}$','$F_p$','$F_m$'])
ax1.set_title('CONTROL VOLUME')
ax1.tick_params(direction=TICKD,right=True, top=True, length=TICKL, width=AXESW)

ax2.plot(t, Ftot[:,1], 'k-',
         t, FV[:,1], 'b--',
         t, FSo[:,1], 'g-.',
         t, Fmu[:,1], 'c-.',
         t, Fp[:,1], 'r:',
         t, Fm[:,1], 'm-')
ax2.set_xlabel('t(s)',fontsize=14)
ax2.set_ylabel('$F_y$',fontsize=14)
ax2.tick_params(direction=TICKD,right=True, top=True, length=TICKL, width=AXESW)
plt.tight_layout()
plt.show()

#====================================================================
# COMPARATION METHODS
#====================================================================
fig, (ax1,ax2) = plt.subplots(2,1)
ax1.plot(t[20:], Ftot[20:,0], 'k-',
         t[20:], FP[20:,0], 'b--',
         t[20:], FI[20:,0], 'g:')
ax1.set_xlabel('t(s)',fontsize=14)
ax1.set_ylabel('$F_x$',fontsize=14)
ax1.legend(['Momentum','Projection','Impulse'])
ax1.set_title('IMPULSE METHOD')
ax1.tick_params(direction=TICKD,right=True, top=True, length=TICKL, width=AXESW)

ax2.plot(t[20:], Ftot[20:,1], 'k-',
         t[20:], FP[20:,1], 'b--',
         t[20:], FI[20:,1], 'g:')
ax2.set_xlabel('t(s)',fontsize=14)
ax2.set_ylabel('$F_y$',fontsize=14)
ax2.tick_params(direction=TICKD,right=True, top=True, length=TICKL, width=AXESW)
plt.tight_layout()
plt.show()
