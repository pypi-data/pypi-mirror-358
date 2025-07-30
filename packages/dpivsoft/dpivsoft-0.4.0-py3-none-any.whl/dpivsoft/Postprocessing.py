# General utilities
import numpy as np
import scipy as sp
import networkx as nx
from scipy import interpolate
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors

# Mesh generation and visualization libraries
import gmsh
import cv2
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely import vectorized

# Custom modules
import dpivsoft.meshTools as mt

def vorticity(x, y, u, v, method):
    """
    Vorticity   omega = du/dy - dv/dx
    --------------------------------------------------------------------------
    Calculates the vorticity of a vector field u,v in a domain x,y, by
    different methods. The methods are described in Markus Raffel,
    Christian E. Willert, Steven T. Wereley,  Jürgen Kompenhans	Experimental
    Fluid Mechanics Particle image velocimetry: a practical guide [2nd ed.]
    Springer-Verlag

    WARNING: Only works for equispaced data with x and y produced by meshgrid.

    input:

    The output is omega of size
        leastsq     = (Nx-4)*(Ny-4)
        centered    = (Nx-2)*(Ny-2)
        richardson  = (Nx-4)*(Ny-4)
        circulation = (Nx-2)*(Ny-2)
        curl        = (Nx-2)*(Ny-2)
    L. Parras Universidad de Malaga (2014)
    """

    dx = x[0,1]-x[0,0]
    dy = y[1,0]-y[0,0]
    [Ny, Nx] = np.shape(x)

    if method == 'centered':
        X = x[1:Ny-1,1:Nx-1]
        Y = y[1:Ny-1,1:Nx-1]
        omega = -((u[2:Ny,1:Nx-1]-u[0:Ny-2,1:Nx-1])/dy-
                (v[1:Ny-1,2:Nx]-v[1:Ny-1,0:Nx-2])/dx)

    elif method == 'leastsq':
        X = x[2:Ny-2,2:Nx-2]
        Y = y[2:Ny-2,2:Nx-2]
        omega = -((2*u[4:Ny,2:Nx-2]+u[3:Ny-1,2:Nx-2]-
                   u[1:Ny-3,2:Nx-2]-2*u[0:Ny-4,2:Nx-2])/(10*dy)
                 -(2*v[2:Ny-2,4:Nx]+u[2:Ny-2,3:Nx-1]-
                   u[2:Ny-2,1:Nx-3]-2*u[2:Ny-2,0:Nx-4])/(10*dx))

    elif method == 'richardson':
        X = x[2:Ny-2,2:Nx-2]
        Y = y[2:Ny-2,2:Nx-2]
        omega = ((u[0:Ny-4,2:Nx-2]-8*u[1:Ny-3,2:Nx-2]
                 +8*u[3:Ny-1,2:Nx-2]-2*u[4:Ny,2:Nx-2])/(12*dy)
                 -(v[2:Ny-2,0:Nx-4]+8*u[2:Ny-2,1:Nx-3]
                 +8*u[2:Ny-2,3:Nx-1]-2*u[2:Ny-2,4:Nx])/(12*dx))

    elif method == 'circulation':
        X = x[1:Ny-1,1:Nx-1]
        Y = y[1:Ny-1,1:Nx-1]
        Gamma = (0.5*dx*(u[0:Ny-2,0:Nx-2]+2*u[0:Ny-2,1:Nx-1]+u[0:Ny-2,2:Nx])
                +0.5*dy*(v[0:Ny-2,2:Nx]+2*v[1:Ny-1,2:Nx]+v[2:Ny,2:Nx])
                -0.5*dx*(u[2:Ny,2:Nx]+2*u[2:Ny,1:Nx-1]+u[2:Ny,0:Nx-2])
                -0.5*dy*(v[2:Ny,0:Nx-2]+2*v[1:Ny-1,0:Nx-2]+v[0:Ny-2,0:Nx-2]))
        omega = Gamma/(4*dx*dy)

    elif method == 'curl':
        dummy, dFx_dy = np.gradient (u, x[0,:], y[:,0], axis = [1,0])
        dFy_dx, dummy = np.gradient (v, x[0,:], y[:,0], axis = [1,0])
        omega = dFy_dx - dFx_dy
        #Re-size to keep only O(2) data (np.gradient is O(1) at borders)
        omega = omega[1:-1,1:-1]
        X = x[1:Ny-1,1:Nx-1]
        Y = y[1:Ny-1,1:Nx-1]

    else:
        print('There is not such method')
        pass

    return X, Y, omega

def vortex_profile(xo, yo, rmax, x, y, u, v, xv, yv, omega, nr, ntheta):
    """
    Vortex data

    Inputs:
    -------
    xo: float
        x position of the vortex center

    yo: float
        y position of the vortex center

    rmax: float
        Radious of the polar grid to

    x: 2d float array
        x meshgrid

    y: 2d float array
        y meshgrid

    omega: 2d float array
        vorticty on the x,y meshgrid

    nr: float
        number of points to interpolate along the radious on
        the polar grid

    n:theta
        number of points to interpolate along the angle on
        the polar grid

    Outputs:
    --------

    R: float array
        radious of the interpolated polar grid

    utheta_mean: float array
        mean azimuthal velocity along the radious of the interpolated
        polar grid

    omega_mean: float array
        mean azimuthal velocity along the radious of the interpolated
        polar grid

    gamma_mean: float array
        mean azimuthal velocity along the radious of the interpolated
        polar grid
    """

    R = np.linspace(0,rmax,nr)
    theta = np.linspace(0,358,ntheta)*np.pi/180
    r, theta = np.meshgrid(R,theta)
    x_vortex = xo + r*np.cos(theta)
    y_vortex = yo + r*np.sin(theta)
    omega = omega.flatten()
    xv = xv.flatten()
    yv = yv.flatten()
    u = u.flatten()
    v = v.flatten()
    x = x.flatten()
    y = y.flatten()

    #Azimuthal velocity on polar grid
    u_int = interpolate.griddata((x,y),u,(x_vortex,y_vortex),method='cubic')
    v_int = interpolate.griddata((x,y),v,(x_vortex,y_vortex),method='cubic')

    u_theta = v_int*np.cos(theta)-u_int*np.sin(theta)
    utheta_mean = np.mean(u_theta,0)

    #Vorticity on polar grid
    w = interpolate.griddata((xv,yv),omega,(x_vortex,y_vortex),method='cubic')
    omega_mean = np.mean(w,0)

    #Circulation using path line on polar grid
    gamma_mean = 2 * np.pi * utheta_mean * R;

    return R, utheta_mean, omega_mean, gamma_mean

def walls_vorticity(xx, yy, pos_x, pos_y, x, y, u, v, omega):
    """
    Modify vorticy over the walls of an object. The derivatives to obtain
    the curl, are done in forward diferences following the surface normal
    vector direction.

    Inputs:
    -------
    xx: float array
        x points along object surface

    yy: float array
        y points along object surface

    pos_x: float array
        x index of points on object surface

    pos_y: float array
        y index of points on object surface

    x: 2d float array
        x meshgrid

    y: 2d float array
        y meshgrid

    u: 2d float array
        velocity in x direction of the field

    v: 2d float array
        velocity in y direction of the field

    omega: 2d float array
       vorticity on the x,y meshgrid

    Outputs:
    --------
    omega: 2d float array
       fixed vorticity on the x,y meshgrid
    """

    #Append the object points array to be a closed figure
    xx = np.append(np.append(xx[-1],xx),xx[0])
    yy = np.append(np.append(yy[-1],yy),yy[0])
    dx = (xx[2:]-xx[0:-2])/2
    dy = (yy[2:]-yy[0:-2])/2

    #normal vector along the axis
    nx = -dy/np.sqrt(dx**2+dy**2)
    ny = dx/np.sqrt(dx**2+dy**2)

    theta = np.zeros(len(dx))
    for i in range(len(theta)):
        #Change referen sistem to be tangential and perpendicular to surface
        theta[i] = np.arctan2(ny[i],nx[i])-np.pi/2
        posx = int(pos_x[i]+np.round(nx[i]))
        posy = int(pos_y[i]+np.round(ny[i]))

        #Velocity tangent to the wall
        Vt = np.cos(theta[i])*u[posy,posx,:]+np.sin(theta[i])*v[posy,posx,:]

        #Calculate vorticiy at walls
        omega[pos_y[i],pos_x[i],:]= -Vt/np.sqrt((x[posy,posx]-xx[i])**2 +
                (y[posy,posx]-yy[i])**2)

    return omega

def divergence(x, y ,u, v):
    """
    Return divergence of the 2D flow, which for a incompressible
    flow should be zero

    Inputs:
    -------
        x: 2d float array
            x meshgrid

        y: 2d float array
            y meshgrid

        u: 2d float array
            velocity in x direction of the field

        v: 2d float array
            velocity in y direction of the field

    Inputs:
    -------

        flow_divergence: 2d float array
            divergence of the 2d flow
    """

    du_dx, du_dy = np.gradient(u, x[0,:], y[:,0], axis = [1,0])
    dv_dx, dv_dy = np.gradient(v, x[0,:], y[:,0], axis = [1,0])

    flow_divergence = du_dx + dv_dy

    return flow_divergence

def stream_lines(x, y, u, v):
    """
    Plot streamlines of the computed 2d flow

    Inputs:
    -------
        x: 2d float array
            x meshgrid

        y: 2d float array
            y meshgrid

        u: 2d float array
            velocity in x direction of the field

        v: 2d float array
            velocity in y direction of the field
    """

    no_boxes_y, no_boxes_x = np.shape(x)

    xx = np.linspace(np.min(x),np.max(x), no_boxes_x)
    yy = np.linspace(np.min(y),np.max(y), no_boxes_y)
    xx, yy = np.meshgrid(xx,yy)

    total_boxes = no_boxes_x * no_boxes_y
    x = x.reshape(total_boxes, order = 'F')
    y = y.reshape(total_boxes, order = 'F')
    u = u.reshape(total_boxes, order = 'F')
    v = v.reshape(total_boxes, order = 'F')

    uu = interpolate.griddata((x, y), u, (xx, yy), method='linear')
    vv = interpolate.griddata((x, y), v, (xx, yy), method='linear')

    vel_magnitude = np.sqrt(uu**2+vv**2)

    fig, ax1 = plt.subplots()
    plt.streamplot(xx, yy, uu, vv,color = vel_magnitude,
            cmap='jet')
    ax1.set_xlabel('x (pixels)', fontsize=18)
    ax1.set_ylabel('y (pixels)', fontsize=18)
    plt.show()

    return 0


def ImpulseMethod(x, y, u, v, omega, rho, Vsol, mu,
         solid_points, t, accel=0):
    """
    Obtain forces over an object using Vortical impulse method, described by
    J.-Z. Wu, X.-Y. Lu, and L.-X. Zhuang. Integral force acting on a body due
    to local ﬂow structures. J. Fluid Mech., 576:265286, 2007. AIAA J.,
    19:432–441, 1981. This formulation is based on the one presented in
    Martín-Alcántara, A., & Fernandez-Feria, R. (2019). Assessment of two
    vortex formulations for computing forces of a flapping foil at high Reynolds
    numbers. Physical Review Fluids, 4(2), 024702. but written in dimensional
    version. The reference frame must be always centered in the object.
    In case of an accelerated reference frame, it is taken into account
    by accel.

    Inputs:
    -------
    x: 2D float array
        X-coordinates of the mesh grid over the flow field.

    y: 2D float array
        Y-coordinates of the mesh grid over the flow field.

    u: 2D float array
        Velocity field in the x-direction, defined on the x, y grid.

    v: 2D float array
        Velocity field in the y-direction, defined on the x, y grid.

    omega: 2D float array
        Vorticity field on the same x, y grid.

    rho: float
        Fluid density. This is a constant value for the entire domain.

    Vsol: float
        Volume of the solid object immersed in the fluid. Used for calculating forces due to added mass, etc.

    mu: float
        Dynamic viscosity of the fluid. Also constant throughout the domain.

    solid_points: list of coordinates tuples
        Coordinates or mask identifying the solid object within the fluid as a list of (x, y) tuples

    t: 1D float array
        Time vector. Each element corresponds to a frame or timestep in the simulation or measurement.

    accel: 2D float array
        Instantaneous acceleration in x and y direction of the moving reference
        frame (centered on the object). Shape (N,2)

    Outputs:
    --------
    F_v: 2D foat array
        Term of vortex force. Size (N,2), for x and y components.

    F_i: 2D float array
        Impulse term of the force. Size (N,2), for x and y components.

    Fsol: 2D float array
        Force integrated over the volume of the object. Size (N,2), for x
        and y components.

    F_oe: 2D float array
        Contribution to the total force of the vorticity leaving the control
        volume. Size (N,2), for x and y components.

    F_mu: 2D float array
        Viscous contribution to the force of vorticity leaving the control
        volume. Size (N,2), for x and y components.
    """

    if solid_points:
    # Check if there is a solid object inside the mesh, obtain points
    # inside the object and make a special treatmen of vorticit on walls
        xx,yy,posx,posy,meshObject = Object(x, y, solid_points)
        omega = walls_vorticity(xx,yy,posx,posy,x,y,u,v,omega)

    dx = x[0,1]-x[0,0]
    dy = y[1,0]-y[0,0]
    dt = t[1]-t[0]

    #Initialize force variables
    F_v = np.zeros([len(t),2])
    F_i = np.zeros([len(t),2])
    Fsol = np.zeros([len(t),2])
    F_oe = np.zeros([len(t),2])
    F_mu = np.zeros([len(t),2])

    #Volumetric terms
    #==========================================================================
    F_v[:,0] = rho*dx*dy*sp.integrate.simps(sp.integrate.simps(
        np.multiply(omega,v),axis=1),axis=0)
    F_v[:,1] = -rho*dx*dy*sp.integrate.simps(sp.integrate.simps(
        np.multiply(omega,u),axis=1),axis=0)

    #Added mass
    #==========================================================================
    if isinstance(accel, np.ndarray):
        Fsol[:,0] = rho * accel[:,0] * Vsol;
        Fsol[:,1] = rho * accel[:,1] * Vsol;

    #Impulse terms
    #==========================================================================
    fz_i = rho*dx*dy*np.trapz(sp.integrate.simps(
        np.einsum('ij,ijk->ijk',x,omega),axis=1),axis=0)
    fx_i = -rho*dx*dy*np.trapz(sp.integrate.simps(
        np.einsum('ij,ijk->ijk',y,omega),axis=1),axis=0)

    #derivative from polynomical fit
    order = 2    #Fit order
    Fz_i = np.zeros(len(t)).astype(np.float)  #Initialize z
    Fx_i = np.zeros(len(t)).astype(np.float)  #Initialize x
    for i in range(2,len(t)-1):
        if order == 1:
            p = np.polyfit(t[i-1:i+2],fx_i[i-1:i+2],1)
            F_i[i,0] = p[0]
            p = np.polyfit(t[i-1:i+2],fz_i[i-1:i+2],1)
            F_i[i,1] = p[0]
        elif order == 2:
            p = np.polyfit(t[i-2:i+3],fx_i[i-2:i+3],2)
            F_i[i,0] = np.polyval(np.polyder(p),t[i])
            p = np.polyfit(t[i-2:i+3],fz_i[i-2:i+3],2)
            F_i[i,1] = np.polyval(np.polyder(p),t[i])

    #First point
    F_i[0,0]= (fx_i[1]-fx_i[0])/(dt)
    F_i[0,1]= (fz_i[1]-fz_i[0])/(dt)
    #Second point
    p = np.polyfit(t[0:3],fx_i[0:3],1)
    F_i[1,0] = p[0]
    p = np.polyfit(t[0:3],fz_i[0:3],1)
    F_i[1,1] = p[0]
    #Second last point
    p = np.polyfit(t[-3:-1],fx_i[-3:-1],1)
    F_i[-2,0] = p[0]
    p = np.polyfit(t[-3:-1],fz_i[-3:-1],1)
    F_i[-2,1] = p[0]
    #Last point
    F_i[-1,0]= (fx_i[-1]-fx_i[-2])/(dt)
    F_i[-1,1]= (fz_i[-1]-fz_i[-2])/(dt)

    #Forces on domain limits
    #==========================================================================
    Fz_oe_left = -rho*dy*sp.integrate.simps(
            omega[:,0,:]*u[:,0,:]*x[0,0],axis=0)
    Fz_oe_right = rho*dy*sp.integrate.simps(
            omega[:,-1,:]*u[:,-1,:]*x[0,-1],axis=0)
    Fz_oe_top = rho*dx*sp.integrate.simps(np.einsum(
            'ij,i->ij', omega[-1,:,:]*v[-1,:,:],x[-1,:]),axis=0)
    Fz_oe_down = -rho*dx*sp.integrate.simps(np.einsum(
            'ij,i->ij', -omega[0,:,:]*v[0,:,:],x[0,:]),axis=0)

    Fx_oe_left = rho*dy*sp.integrate.simps(np.einsum(
            'ij,i->ij', omega[:,0,:]*u[:,0,:],y[:,0]),axis=0)
    Fx_oe_right=-rho*dy*sp.integrate.simps(np.einsum(
            'ij,i->ij', omega[:,-1,:]*u[:,-1,:],y[:,-1]),axis=0)
    Fx_oe_top = -rho*dx*sp.integrate.simps(
            omega[-1,:,:]*v[-1,:,:]*y[-1,0],axis=0)
    Fx_oe_down = rho*dx*sp.integrate.simps(
            omega[0,:,:]*v[0,:,:]*y[0,0],axis=0)

    #Sum of all forzes at domain limits
    F_oe[:,0] = Fx_oe_top+Fx_oe_down+Fx_oe_left+Fx_oe_right
    F_oe[:,1] = Fz_oe_top+Fz_oe_down+Fz_oe_left+Fz_oe_right

    #Viscous forces at domain limits
    #==========================================================================
    #Right
    Fx_mu_right = mu*dy*sp.integrate.simps(np.einsum('ij,i->ij',
        (omega[:,-1,:]-omega[:,-2,:])/dx,y[:,-1]),axis=0)
    Fz_mu_right = mu*dy*sp.integrate.simps(omega[:,-1,:]-np.einsum('ij,i->ij',
        (omega[:,-1,:]-omega[:,-2,:])/dx,x[:,-1]),axis=0)
    #Left
    Fx_mu_left = -mu*dy*sp.integrate.simps(np.einsum('ij,i->ij',
        (omega[:,1,:]-omega[:,0,:])/dx,y[:,0]),axis=0)
    Fz_mu_left = mu*dy*sp.integrate.simps(-omega[:,0,:]+np.einsum('ij,i->ij',
        (omega[:,1,:]-omega[:,0,:])/dx,x[:,0]),axis=0)
    #Top
    Fx_mu_top = mu*dx*sp.integrate.simps(-omega[-1,:,:]+np.einsum('ij,i->ij',
        (omega[-1,:,:]-omega[-2,:,:])/dy,y[-1,:]),axis=0)
    Fz_mu_top = -mu*dx*sp.integrate.simps(np.einsum('ij,i->ij',
        (omega[-1,:,:]-omega[-2,:,:])/dy,x[-1,:]),axis=0)
    #Down
    Fx_mu_down = mu*dx*sp.integrate.simps(omega[0,:,:]-np.einsum('ij,i->ij',
        (omega[1,:,:]-omega[0,:,:])/dy,y[0,:]),axis=0)
    Fz_mu_down = mu*dx*sp.integrate.simps(np.einsum('ij,i->ij',
        (omega[1,:,:]-omega[0,:,:])/dy,x[0,:]),axis=0)

    F_mu[:,0] = Fx_mu_top+Fx_mu_down+Fx_mu_left+Fx_mu_right;
    F_mu[:,1] = Fz_mu_top+Fz_mu_down+Fz_mu_left+Fz_mu_right;

    return F_v, F_i, Fsol, F_oe, F_mu

def ProjectionMethod(x, y, u, v, omega, grad_phi, rho, mu,
        solid_points, added_m=np.zeros(2), accel=0):
    """
    Obtain forces over an object using projection method. The formulation used
    is from C.-C. Chang. Potential ﬂow and forces for the incompressible viscous ﬂow.
    Proc. R. Soc. A-Math. Phys. Engng Sci., 437:517–525, 1992. This formulation is
    based on the one presented in Martín-Alcántara, A., & Fernandez-Feria, R. (2019).
    Assessment of two vortex formulations for computing forces of a flapping foil
    at high Reynolds numbers. Physical Review Fluids, 4(2), 024702. but written
    in dimensional version. The reference frame must be centered in the object
    and accelerations on it are taken into account by accel.

    Inputs:
    -------
    x: 2D float array
        X-coordinates of the mesh grid over the flow field.

    y: 2D float array
        Y-coordinates of the mesh grid over the flow field.

    u: 2D float array
        Velocity field in the x-direction, defined on the x, y grid.

    v: 2D float array
        Velocity field in the y-direction, defined on the x, y grid.

    omega: 2D float array
        Vorticity field on the same x, y grid.

    grad_phi: 3D float array
        Hessian of the projection function given by solving
        ∇2 ϕ = 0 , ns · ∇ϕ = −ns
        dimension of (4,x,y) arranged like:
            [ϕ_xx, ϕ_xy]
            [ϕ_yx, ϕ_yy]

    rho: float
        Fluid density. This is a constant value for the entire domain.

    mu: float
        Dynamic viscosity of the fluid. Also constant throughout the domain.

    solid_points: list of coordinates tuples
        Coordinates or mask identifying the solid object within the fluid as a list of (x, y) tuples

    t: 1D float array
        Time vector. Each element corresponds to a frame or timestep in the simulation or measurement.

    added_m: float list
        added mass tensor obtained from integrating ϕ(∂ϕ/∂n)dS along the solid
        surface. Only needed if accelerated reference frame.

    accel: 2D float array
        Instantaneous acceleration in x and y direction of the moving reference
        frame (centered on the object). Shape (N,2)

    Outputs:
    --------
    F: 2D float array
        Total force over the object. Size (N,2), for x and y components.

    Fv: 2D float array
        Vortical contribution to force. Size (N,2), for x and y components.

    Fmu: 2D float array
        Viscous contribution to force. Size (N,2), for x and y components.

    """

    #Matrix inicialization
    Temp1 = 0 * u; Temp2 = 0 * u; Temp3 = 0 * u; Temp4 = 0 * u

    Fam = np.zeros([len(u[0,0,:]), 2])
    Fv = np.zeros(Fam.shape)
    Fmu = np.zeros(Fam.shape)
    Ft = np.zeros(Fam.shape)

    #Surface contribution (not implemented)
    if solid_points:
        # Check if there is a solid object inside the mesh, obtain points inside
        # the object and make a special treatmen of vorticit on walls
        xx, yy, posx, posy, _ = Object(x, y, solid_points)
        omega = walls_vorticity(xx,yy,posx,posy,x,y,u,v,omega)

        Fmu_x, Fmu_y = Surface_projection(xx, yy, posx, posy,
                grad_phi, omega, mu)
        Fmu[:,0] = Fmu_x; Fmu[:,1] = Fmu_y

    #Added mass contribution (not implemented)
    if isinstance(accel, np.ndarray):
        # Otherwise, assume accel is a 2D array with shape (N, 2)
        Fam[:,0] = -added_m[0,0] * accel[:, 0] - added_m[0,1] * accel[:,1]
        Fam[:,1] = -added_m[1,0] * accel[:, 0] - added_m[1,1] * accel[:,1]

    #Vortex contribution
    for i in range(0,len(Temp1[0,0,:])):
        Temp1[:,:,i] = -v[:,:,i] * grad_phi[0,0,:,:]
        Temp2[:,:,i] = +u[:,:,i] * grad_phi[0,1,:,:]
        Temp3[:,:,i] = -v[:,:,i] * grad_phi[1,0,:,:]
        Temp4[:,:,i] = +u[:,:,i] * grad_phi[1,1,:,:]

    Temp1[np.isnan(Temp1)] = 0
    Temp2[np.isnan(Temp2)] = 0
    Temp3[np.isnan(Temp3)] = 0
    Temp4[np.isnan(Temp4)] = 0

    integrate_Cd = omega * (Temp1 + Temp2)
    integrate_Cl = omega * (Temp3 + Temp4)

    dx = x[0,1]-x[0,0]
    dy = abs(y[1,0]-y[0,0])

    for i in range(len(xx)):
        integrate_Cd[posy[i], posx[i],:] = 0
        integrate_Cl[posy[i], posx[i],:] = 0

    Fv[:,0] = rho*dx*dy*sp.integrate.simps(sp.integrate.simps(
        integrate_Cd,axis=1),axis=0)
    Fv[:,1] = rho*dx*dy*sp.integrate.simps(sp.integrate.simps(
        integrate_Cl,axis=1),axis=0)

    #Total Force using projection method
    Ft = Fam + Fv + Fmu

    return Ft, Fv, Fmu, Fam

def Surface_projection(xx, yy, pos_x, pos_y, grad_phi, omega, mu):
    """
    Compute the viscous vortex-force contribution on a solid surface for the
    projection method.

    The object boundary is defined by ordered points (`xx`, `yy`) and their
    corresponding mesh indices (`pos_x`, `pos_y`). Normal vectors are estimated
    along the path, and the viscous contribution is integrated using Simpson’s rule.

    Inputs:
    -------
    xx, yy: 1D float arrays
        Ordered coordinates of the object boundary.

    pos_x, pos_y: 1D int arrays
        Mesh indices corresponding to the boundary coordinates.

    x, y: 2D float arrays
        Mesh grid coordinates (used only for consistency).

    grad_phi: 4D float array
        Hessian of the potential function, shape (2, 2, ny, nx).

    omega: 3D float array
        Vorticity field over time, shape (ny, nx, nt).

    mu: float
        Dynamic viscosity of the fluid.

    Outputs:
    --------
    Fx: 1D float array
        x-component of the viscous surface force over time.

    Fy: 1D float array
        y-component of the viscous surface force over time.
    """

    # Append the object points array to be a closed figure
    xx = np.append(xx,xx[0])
    yy = np.append(yy,yy[0])
    pos_x = np.append(pos_x,pos_x[0])
    pos_y = np.append(pos_y,pos_y[0])
    dx = (xx[1:]-xx[0:-1])
    dy = (yy[1:]-yy[0:-1])

    line = np.sqrt(dx**2+dy**2)
    axis_l = np.zeros(len(xx))
    for i in range(1,len(axis_l)):
        axis_l[i] = axis_l[i-1]+line[i-1]

    # Normal vector along the axis
    xx = np.append(xx[-2],xx)
    yy = np.append(yy[-2],yy)
    d2x = (xx[2:]-xx[0:-2])/2
    d2y = (yy[2:]-yy[0:-2])/2

    nx = -d2y/np.sqrt(d2x**2+d2y**2)
    ny = d2x/np.sqrt(d2x**2+d2y**2)
    nx = np.append(nx,nx[0])
    ny = np.append(ny,ny[0])

    int_x = np.zeros((len(axis_l),len(omega[0,0,:])))
    int_y = np.zeros((len(axis_l),len(omega[0,0,:])))

    for i in range(len(axis_l)):
        # Calculates integrand term of the surface
        int_x[i,:] = (omega[pos_y[i],pos_x[i],:]*(nx[i]*(grad_phi[0,1,pos_y[i],pos_x[i]]) -
                 ny[i]*(grad_phi[0,0,pos_y[i],pos_x[i]]+1)))
        int_y[i,:] = (omega[pos_y[i],pos_x[i],:]*(nx[i]*(grad_phi[1,1,pos_y[i],pos_x[i]]+1) -
                 ny[i]*(grad_phi[1,0,pos_y[i],pos_x[i]])))

    Fx = 2*mu*sp.integrate.simps(int_x, axis_l, axis=0)
    Fy = mu*sp.integrate.simps(int_y, axis_l, axis=0)

    return Fx, Fy

def Object(x, y, points, res=4):
    """
    Generate a binary mask and extract ordered boundary coordinates of a 2D object
    defined by a polygon within a structured mesh. The function identifies which
    mesh nodes lie inside the polygon, detects the boundary via dilation, and
    reorders the perimeter points to form a continuous path using a nearest-neighbor
    graph.

    Inputs:
    -------
    x: 2D float array
        X-coordinates of the mesh grid.

    y: 2D float array
        Y-coordinates of the mesh grid.

    points: array-like
        (x, y) coordinates defining the polygonal shape of the object.

    res: int, optional
        Decimal precision for rounding mesh coordinates (default = 4).

    Outputs:
    --------
    x: 1D float array
        Ordered x-coordinates of boundary points.

    y: 1D float array
        Ordered y-coordinates of boundary points.

    posx: 1D int array
        Mesh x-indices of boundary points.

    posy: 1D int array
        Mesh y-indices of boundary points.

    mesh: 2D uint8 array
        Binary mask of the domain (0 = solid, 1 = fluid).
    """

    # Round to assure that boundaries are taken into account correctly
    x = np.round(x, res)
    y = np.round(y, res)

    #Generates a polygon geometry inside the x,y mesh, from an array
    #of points
    polygon = Polygon(points)

    #Check if points of the mesh are inside polygon
    mesh = vectorized.contains(polygon, x, y).astype(np.uint8)

    #Obtain position of outside boundaries
    kernel = np.ones((3,3))
    border = cv2.dilate(mesh, kernel, iterations=1) - mesh
    posy, posx = np.where(border == 1)

    x = x[posy,posx]
    y = y[posy,posx]

    #Order the points into a path
    points = np.c_[x, y]

    clf = NearestNeighbors(n_neighbors=2).fit(points)
    G = clf.kneighbors_graph()

    T = nx.from_scipy_sparse_array(G)

    paths = [list(nx.dfs_preorder_nodes(T, i)) for i in range(len(points))]

    mindist = np.inf
    minidx = 0

    for i in range(len(points)):
        p = paths[i]           # order of nodes
        ordered = points[p]    # ordered nodes
        # find cost of that order by the sum of euclidean distances between
        # points (i) and (i+1)
        cost = (((ordered[:-1] - ordered[1:])**2).sum(1)).sum()
        if cost < mindist:
            mindist = cost
            minidx = i

    opt_order = paths[minidx]

    # Points ordered following a path
    x = x[opt_order]
    y = y[opt_order]

    posx = posx[opt_order]
    posy = posy[opt_order]

    mesh = (1 - mesh).astype(np.uint8)

    return x, y, posx, posy, mesh

def ControlVolume(x, y, u, v, rho, mu, t, accel=0, p=0):
    """
    Compute hydrodynamic forces on a 2D body using the Control Volume
    method, based on the integral formulation of the momentum equation
    applied to a moving volume enclosing the body. This method follows the
    approach described in:

    FERIA, Ramón Fernández; CASANOVA, J. Ortega. Mecánica de fluidos. Servicio
    de Publicaciones e Intercambio Científico de la Universidad de Málaga, 2001.

    The implementation assumes a 2D incompressible flow over a domain defined by
    the (x, y) mesh, with velocity fields u and v. The control volume encloses the
    object and may be moving or accelerating. The total force is computed from
    several contributing terms: the unsteady and convective momentum flux, pressure
    contribution, viscous stresses, and added-mass effect if the reference frame
    is non-inertial.

    The reference frame must always be centered on the object. In case of a moving
    or accelerated frame, the added-mass correction is applied using `accel`.

    Inputs:
    -------
    x: 2D float array
        X-coordinates of the mesh grid over the flow field.

    y: 2D float array
        Y-coordinates of the mesh grid over the flow field.

    u: 3D float array
        X-component of the velocity field over time. Shape (nx, ny, nt).

    v: 3D float array
        Y-component of the velocity field over time. Shape (nx, ny, nt).

    rho: float
        Fluid density (assumed constant).

    mu: float
        Dynamic viscosity of the fluid (assumed constant).

    t: 1D float array
        Time vector. Each entry corresponds to a timestep.

    accel: float or 2D float array, optional
        Acceleration of the reference frame. If scalar, assumed zero contribution.
        If array of shape (nt, 2), it is used for added mass correction.

    p: 2D float array or float, optional
        Pressure field (same shape as u and v) or scalar zero if not used.

    Outputs:
    --------
    F_v: 2D float array
        Convective momentum flux contribution to total force. Shape (nt, 2).

    F_i: 2D float array
        Local (unsteady) momentum contribution. Shape (nt, 2).

    Fsol: 2D float array
        Added-mass term due to acceleration of the control volume. Shape (nt, 2).

    F_oe: 2D float array
        Net outflow of momentum across control volume boundaries. Shape (nt, 2).

    F_mu: 2D float array
        Viscous stress contribution to the force. Shape (nt, 2).
    """

    dx = x[0,1]-x[0,0]
    dy = y[1,0]-y[0,0]
    dt = t[1]-t[0]

    [Gradx,Grady,u,v,dudx,dudy,dvdx,dvdy] = FieldDerivatives(rho,dx,dy,
        u,v,accel,mu,dt)

    #initialize vectors
    FV = np.zeros([len(t),2])
    FSo = np.zeros([len(t),2])
    Fmu = np.zeros([len(t),2])
    Fp = np.zeros([len(t),2])
    Fm = np.zeros([len(t),2])

    # Pressure term
    #==========================================================================
    if len(p)==1:
        text = """
        Calculation of pressure is not integrated in the code yet. If not
        provided, this term is computed as 0. Total result of force is not
        correct.
        """
        print(text)
        p = np.zeros(Gradx.shape)

    #Pressure forces acting on domain limits
    Fp_Left = dy*np.trapz(p[:,0,:],axis=0)
    Fp_Right = -dy*np.trapz(p[:,-1,:],axis=0)
    Fp_Top = -dx*np.trapz(p[-1,:,:],axis=0)
    Fp_Down = dx*np.trapz(p[0,:,:],axis=0)
    Fp[:,0] = Fp_Left + Fp_Right
    Fp[:,1] = Fp_Top + Fp_Down

    #Volume term
    #==========================================================================
    Vx_int = -dx*dy*np.trapz(np.trapz(u,axis=0),axis=0) # x component
    Vy_int = -dx*dy*np.trapz(np.trapz(v,axis=0),axis=0) # y component

    FV[0,0] = rho*(Vx_int[1]-Vx_int[0])/dt
    FV[0,1] = rho*(Vy_int[1]-Vy_int[0])/dt
    FV[-1,0] = rho*(Vx_int[-1]-Vx_int[-2])/dt
    FV[-1,1] = rho*(Vy_int[-1]-Vy_int[-2])/dt
    FV[1:-1,0] = rho*(Vx_int[2:]-Vx_int[0:-2])/(2*dt)
    FV[1:-1,1] = rho*(Vy_int[2:]-Vy_int[0:-2])/(2*dt)

    # Convective term
    #==========================================================================
    S_Left_x = rho*dy*np.trapz(u[:,0,:]**2,axis=0)
    S_Right_x = -rho*dy*np.trapz(u[:,-1,:]**2,axis=0)
    S_Top_x = -rho*dx*np.trapz(u[-1,:,:]*v[-1,:,:],axis=0)
    S_Down_x = rho*dx*np.trapz(u[0,:,:]*v[0,:,:],axis=0)
    S_Left_y = rho*dy*np.trapz(u[:,0,:]*v[:,0,:],axis=0)
    S_Right_y = -rho*dy*np.trapz(u[:,-1,:]*v[:,-1,:],axis=0)
    S_Top_y = -rho*dx*np.trapz(v[-1,:,:]**2,axis=0)
    S_Down_y = rho*dx*np.trapz(v[0,:,:]**2,axis=0)

    FSo[:,0] = S_Left_x+S_Right_x+S_Top_x+S_Down_x
    FSo[:,1] = S_Left_y+S_Right_y+S_Top_y+S_Down_y

    # Viscous term
    #==========================================================================
    Fmu_Left_x = -2*mu*dy*np.trapz(dudx[:,0,:],axis=0)
    Fmu_Right_x = 2*mu*dy*np.trapz(dudx[:,-1,:],axis=0)
    Fmu_Top_x = mu*dx*np.trapz(dvdx[-1,:,:]+dudy[-1,:,:],axis=0)
    Fmu_Down_x = -mu*dx*np.trapz(dvdx[0,:,:]+dudy[0,:,:],axis=0)

    Fmu_Left_y = -mu*dy*np.trapz(dvdx[:,0,:]+dudy[:,0,:],axis=0)
    Fmu_Right_y = mu*dy*np.trapz(dvdx[:,-1,:]+dudy[:,-1,:],axis=0)
    Fmu_Top_y = 2*mu*dx*np.trapz(dvdy[-1,:,:],axis=0)
    Fmu_Down_y = -2*mu*dx*np.trapz(dvdy[0,:,:],axis=0)

    Fmu[:,0] = Fmu_Left_x + Fmu_Right_x + Fmu_Top_x + Fmu_Down_x
    Fmu[:,1] = Fmu_Left_y + Fmu_Right_y + Fmu_Top_y + Fmu_Down_y

    # Non intertial frame term
    #==========================================================================
    Vc = (np.max(x)-np.min(x))*(np.max(y)-np.min(y))
    if isinstance(accel, np.ndarray):
        Fm[:,0] = -rho*Vc*accel[:,0]
        Fm[:,1] = -rho*Vc*accel[:,1]

    Ftot = FV + FSo + Fmu + Fp + Fm

    return Ftot, FV, FSo, Fmu, Fp, Fm

def FieldDerivatives(rho, dx, dy, u, v, accel, mu, dt):

    #Initialize time derivatives
    a, b, c = u.shape
    dudt = np.zeros([a-2,b-2,c])
    dvdt = np.zeros([a-2,b-2,c])

    #Spatial derivatives using central finite differences
    dudx = (u[1:-1,2:,:]-u[1:-1,0:-2,:])/(2*dx)
    dudy = (u[2:,1:-1,:]-u[0:-2,1:-1,:])/(2*dy)

    dvdx = (v[1:-1,2:,:]-v[1:-1,0:-2,:])/(2*dx)
    dvdy = (v[2:,1:-1,:]-v[0:-2,1:-1,:])/(2*dy)

    #Time derivatives using central finite difference scheme
    dudt[:,:,1:-1] = (u[1:-1,1:-1,2:]-u[1:-1,1:-1,0:-2])/(2*dt)
    dvdt[:,:,1:-1] = (v[1:-1,1:-1,2:]-v[1:-1,1:-1,0:-2])/(2*dt)

    dudt[:,:,0] = (u[1:-1,1:-1,1]-u[1:-1,1:-1,0])/dt
    dvdt[:,:,0] = (v[1:-1,1:-1,1]-v[1:-1,1:-1,0])/dt

    dudt[:,:,-1] = (u[1:-1,1:-1,-1]-u[1:-1,1:-1,-2])/dt
    dvdt[:,:,-1] = (v[1:-1,1:-1,-1]-v[1:-1,1:-1,-2])/dt

    #Second spatial derivatives using central finite diference scheme
    ddudx = (u[1:-1,0:-2,:]-2*u[1:-1,1:-1,:]+u[1:-1,2:,:])/(dx**2)
    ddudy = (u[0:-2,1:-1,:]-2*u[1:-1,1:-1,:]+u[2:,1:-1,:])/(dy**2)

    ddvdx = (v[1:-1,0:-2,:]-2*v[1:-1,1:-1,:]+v[1:-1,2:,:])/(dx**2)
    ddvdy = (v[0:-2,1:-1,:]-2*v[1:-1,1:-1,:]+v[2:,1:-1,:])/(dy**2)

    #Reduce domain to macht with pressure
    u = u[1:-1,1:-1,:]
    v = v[1:-1,1:-1,:]

    #Obtain the 2 components of the pressure gradient
    Gradx = mu*(ddudx+ddudy)-rho*((u*dudx)
            + (v*dudy) + dudt)
    Grady = mu*(ddvdx+ddvdy)-rho*(np.multiply(u,dvdx)
            + np.multiply(v,dvdy) + dvdt)

    return Gradx, Grady, u, v, dudx, dudy, dvdx, dvdy
