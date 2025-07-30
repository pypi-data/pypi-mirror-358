import matplotlib.pyplot as plt
import numpy as np
import os

import dpivsoft.Postprocessing as post
import dpivsoft.meshTools as mt

dirCode = os.getcwd()   #Current path
dirSave = dirCode + "/Results/Forces" #Images folder

# Create Mesh to apply FEM method
size = 6  # how many chords in all directions are used
tm =0.4  # element size of the mesh in the outbound
tmr = 0.005 # element size of the mesh in the object
c = 1

# Solve Chang functions on mesh
fileName = "object.msh"
meshFile = dirSave + '/' + fileName

if not os.path.exists(dirSave):
    os.makedirs(dirSave)

# Create NACA0012 geometry
t = 0.12
x = np.linspace(0,1,1000)
yc = 5*t*(0.2969*np.sqrt(x)-0.1260*x-0.3516*x**2+0.2843*x**3-0.1015*x**4)
x = x-0.5

x = np.concatenate([x, x[::-1]])
yc = np.concatenate([yc, -yc[::-1]])
points = list(zip(x.flatten(), yc.flatten(), np.zeros_like(x.flatten())))


# Generation of finite element mesh to calculate projection functions
mt.mesh_generator('spline', dirSave, c=c, size=size, tm=tm,
        points=points, tmr=tmr, visualize=1, filename=fileName)

# Solve proyection function and the added_mass tensor
[mesh, mesh_cell, mesh_elem, phi, grad_phi, added_mass] = mt.projection_FEM_Solver(
        meshFile, dirSave, visualize=1)

print(added_mass)
