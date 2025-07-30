# General utilities
import os
import numpy as np
import matplotlib.pyplot as plt

# Mesh generation and visualization libraries
import gmsh
import meshio

# Interpolation and linear algebra (SciPy)
from scipy import interpolate
from scipy.interpolate import griddata
from scipy.sparse.linalg import spsolve

# Finite element tools (scikit-fem)
from skfem import Functional, Basis, FacetBasis, ElementTriP1, ElementTriP2
from skfem.models.poisson import laplace, unit_load
from skfem.assembly import LinearForm, asm
from skfem.visuals.matplotlib import plot
from skfem.io import from_meshio

# Custom modules
import dpivsoft.Postprocessing as Post
import dpivsoft.SyIm as SyIm

def body_options(tmr, name='spline', c=1, points=[]):

    def circleGeneration(c, tmr, cx=0, cy=0):
        # Define inside object (circle)
        center = gmsh.model.geo.addPoint(0, 0, 0, 0.1)  # circle center
        r = c/2

        # Define two points of the circle to create arcs lines
        p11 = gmsh.model.geo.addPoint(cx+r, cy, 0, tmr)
        p12 = gmsh.model.geo.addPoint(cx-r, cy, 0, tmr)

        # Create arcs using previous points
        arc1 = gmsh.model.geo.addCircleArc(p11, center, p12)
        arc2 = gmsh.model.geo.addCircleArc(p12, center, p11)
        obj_lines = [arc1, arc2]

        # Create single line loop for inside object
        cl_inner = gmsh.model.geo.addCurveLoop(obj_lines)

        return cl_inner, obj_lines, center

    if name == 'polygon':
        obj_lines = []
        point_ids = [gmsh.model.geo.addPoint(x, y, z, tmr) for x, y, z in points]
        for i in range(1,len(point_ids)):
            idL = gmsh.model.geo.addLine(point_ids[i-1],point_ids[i])
            obj_lines.append(idL)
        idL = gmsh.model.geo.addLine(point_ids[-1],point_ids[0])
        obj_lines.append(idL)

        cl_inner = gmsh.model.geo.addCurveLoop(obj_lines)

    elif name == 'spline':
        # Create points in Gmsh
        point_ids = [gmsh.model.geo.addPoint(x, y, z, tmr) for x, y, z in points]
        point_ids.append(point_ids[0])

        # Create a B-Spline curve using all points
        splineId = gmsh.model.geo.addSpline(point_ids)

        cl_inner = gmsh.model.geo.addCurveLoop([splineId])

        # Create a closed curve loop from the single B-Spline
        obj_lines = [splineId]  # Store the B-Spline as the object boundary

    elif name == 'circle':
        cl_inner, obj_lines, center = circleGeneration(c, tmr)

    else:
        pass

    return cl_inner, obj_lines

def mesh_generator(obj, dirSave, c=1, size=3, tm=0.1, tmr=0.01, points=[],
                   elementOrder=1, filename='mesh.msh', visualize=1):

    # Initialize gmsh
    gmsh.initialize()
    gmsh.model.add('mesh')
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)

    # Set mesh to use Quadratic Elements (P2)
    gmsh.option.setNumber("Mesh.ElementOrder", elementOrder)

    # Define outbound points
    width = c*size
    height = c*size
    p1 = gmsh.model.geo.addPoint(-height, -width, 0, tm)
    p2 = gmsh.model.geo.addPoint(height, -width, 0, tm)
    p3 = gmsh.model.geo.addPoint(height, width, 0, tm)
    p4 = gmsh.model.geo.addPoint(-height, width, 0, tm)

    # Define outbound lines
    l1 = gmsh.model.geo.addLine(p1, p2)
    l2 = gmsh.model.geo.addLine(p2, p3)
    l3 = gmsh.model.geo.addLine(p3, p4)
    l4 = gmsh.model.geo.addLine(p4, p1)

    # Create single line loop for outbound
    cl_outer = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])

    # Define inside object
    cl_inner, obj_lines = body_options(tmr, name=obj, points=points)

    # Create surface plane for the fluid
    surface = gmsh.model.geo.addPlaneSurface([cl_outer, cl_inner])

    # Ensure obj_lines is always a list (for splines, circles, etc.)
    if isinstance(obj_lines, int):
        obj_lines = [obj_lines]

    # Syncronize mesh
    gmsh.model.geo.synchronize()

    # Physical groups
    gmsh.model.addPhysicalGroup(1, [l1, l2, l3, l4], 102)
    gmsh.model.setPhysicalName(1, 102, "outbound")

    gmsh.model.addPhysicalGroup(1, obj_lines, 103)
    gmsh.model.setPhysicalName(1, 103, "object")

    gmsh.model.addPhysicalGroup(2, [surface], 104)
    gmsh.model.setPhysicalName(2, 104, "fluid")

    # Generate 2D mesh
    gmsh.model.mesh.generate(2)

    # Assign physical groups explicitly for curved edges (P2 elements create "line3" elements)
    gmsh.model.mesh.optimize("Netgen")  # Optional, helps with quality

    # Visualize mesh
    if visualize:
        gmsh.fltk.run()

    # save mesh file
    output_file = dirSave + '/'+filename
    gmsh.write(output_file)

    # Close mesh
    gmsh.finalize()

def projection_FEM_Solver(path, dirSave, fileName="mesh", visualize=1):

    # Load mesh
    meshio_mesh = meshio.read(path)
    mesh = from_meshio(meshio_mesh)

    [mesh_cell, mesh_elem, phix, grad_phix] = FEM_Solver(
            mesh, [1,0])
    [mesh_cell, mesh_elem, phiy, grad_phiy] = FEM_Solver(
            mesh, [0,1])

    phi = np.zeros([2,len(phix)])
    grad_phi = np.zeros([2,2,len(grad_phix[0,:])])

    phi[0,:] = phix ; phi[1,:] = phiy

    grad_phi[0,:,:] = grad_phix
    grad_phi[1,:,:] = grad_phiy

    added_mass = compute_added_mass(mesh, phi)

    # Plot if needed
    if visualize:
        plotPhiResults(mesh, phi, grad_phi)

    if isinstance(dirSave, str):
        np.savez(dirSave + '/' + fileName,
                 mesh_elem=mesh_elem,
                 phi=phi,
                 grad_phi=grad_phi,
                 added_mass=added_mass)

    return mesh, mesh_cell, mesh_elem, phi, grad_phi, added_mass

def FEM_Solver(mesh, direction):

    # Finite element setup
    element = ElementTriP1()
    basis = Basis(mesh, element)
    A = asm(laplace, basis)
    b = np.zeros(basis.N)

    # Identify boundary regions
    object_facets = mesh.boundaries["object"]
    outlet_facets = mesh.boundaries["outbound"]
    D_outlet = basis.get_dofs(outlet_facets)

    # --- Neumann BC: n · ∇φ = -n · direction on object ---
    facet_basis_object = FacetBasis(mesh, element, facets=object_facets)

    @LinearForm
    def flux(v, w):
        dot = direction[0] * w.n[0] + direction[1] * w.n[1]
        return -dot * v

    b += asm(flux, facet_basis_object)

    # Apply Dirichlet BC at outlet: φ = 0
    from scipy.sparse import lil_matrix, eye
    A = lil_matrix(A)
    D_outlet = np.array(D_outlet)
    A[D_outlet, :] = 0
    A[:, D_outlet] = 0
    for i in range(len(D_outlet)):
        A[D_outlet[i], D_outlet[i]] = 1
    b[D_outlet] = 0
    A = A.tocsr()

    # Solve the system
    phi = spsolve(A, b)

    # Compute gradients at element centers
    grad_phi = basis.interpolate(phi).grad.mean(axis=2)  # shape: (2, num_elements)

    # Map gradients to nodes
    num_nodes = basis.doflocs.shape[1]
    num_elements = mesh.t.shape[1]
    grad_x_nodes = np.zeros(num_nodes)
    grad_y_nodes = np.zeros(num_nodes)
    node_count = np.zeros(num_nodes)

    for i in range(num_elements):
        nodes = mesh.t[:, i]
        grad_x_nodes[nodes] += grad_phi[0, i]
        grad_y_nodes[nodes] += grad_phi[1, i]
        node_count[nodes] += 1

    grad_x_nodes /= node_count
    grad_y_nodes /= node_count

    mesh_cell = basis.doflocs.T
    mesh_elem = mesh.p[:, mesh.t].mean(axis=1).T


    return mesh_cell, mesh_elem, phi, grad_phi

def compute_added_mass(mesh, phi):

    element = ElementTriP1()
    basis = Basis(mesh, element)
    f_basis = FacetBasis(mesh, element, facets=mesh.boundaries["object"])

    M = np.zeros((2, 2))

    for j in range(2):
        phi_j = phi[j]

        for i in range(2):

            @Functional
            def integrand(w):
                # interpolate phi_j on facets
                phi_gf = f_basis.interpolate(phi_j)
                # normal component n_i times phi_j
                return w.n[i] * phi_gf.value

            M[i, j] = -integrand.assemble(f_basis)

    return M

def plotPhiResults(mesh, phi, grad_phi):

   fig = plt.figure(figsize=(18, 8))

   # First subplot: dphi/dx
   ax1 = fig.add_subplot(1, 2, 1)  # 1 row, 2 columns, first plot
   plot(mesh, phi[0], ax=ax1, colorbar=True)
   ax1.set_title("Gradient Component: $\phi_x$")
   ax1.set_xlabel("$x$")
   ax1.set_ylabel("$y$")

   # Second subplot: dphi/dy
   ax2 = fig.add_subplot(1, 2, 2)  # 1 row, 2 columns, second plot
   plot(mesh, phi[1], ax=ax2, colorbar=True)
   ax2.set_title("Gradient Component: $\phi_y$")
   ax2.set_xlabel("$x$")
   ax2.set_ylabel("$y$")

   plt.tight_layout()

   fig2 = plt.figure(figsize=(18, 24))

   ax3 = fig2.add_subplot(2, 2, 1)  # 1 row, 2 columns, second plot
   plot(mesh, grad_phi[0,0], ax=ax3, colorbar=True)
   ax3.set_title("Gradient Component: $d \phi_x/dx$")
   ax3.set_xlabel("$x$")
   ax3.set_ylabel("$y$")

   ax4 = fig2.add_subplot(2, 2, 2)  # 1 row, 2 columns, second plot
   plot(mesh, grad_phi[0,1], ax=ax4, colorbar=True)
   ax4.set_title("Gradient Component: $d \phi_x/dy$")
   ax4.set_xlabel("$x$")
   ax4.set_ylabel("$y$")

   ax5 = fig2.add_subplot(2, 2, 3)  # 1 row, 2 columns, second plot
   plot(mesh, grad_phi[1,0], ax=ax5, colorbar=True)
   ax5.set_title("Gradient Component: $d \phi_y/dx$")
   ax5.set_xlabel("$x$")
   ax5.set_ylabel("$y$")

   ax6 = fig2.add_subplot(2, 2, 4)  # 1 row, 2 columns, second plot
   plot(mesh, grad_phi[1,1], ax=ax6, colorbar=True)
   ax6.set_title("Gradient Component: $d \phi_y/dy$")
   ax6.set_xlabel("$x$")
   ax6.set_ylabel("$y$")

   # Display the figures
   plt.show()

def plot_mesh(mesh):
    nodes = mesh.points  # Nodes are in the 'points' attribute
    elements = mesh.cells  # Elements are in the 'cells' attribute

    # The cell type we're interested in
    cell_type = "line3"

    # Get the cells of the specified type
    cells = mesh.get_cells_type(cell_type)

    # Get the cell data, which contains the physical region IDs
    cell_data = mesh.get_cell_data("gmsh:physical", cell_type)

    # Identify the indices for the "outbound" and "object" physical regions (102 and 103)
    outbound_indices = np.where(cell_data == 102)[0]
    object_indices = np.where(cell_data == 103)[0]

    # Get the nodes corresponding to these indices
    outbound_nodes = np.unique(cells[outbound_indices])  # Unique nodes in the outbound region
    object_nodes = np.unique(cells[object_indices])  # Unique nodes in the object region

    # Identify all nodes
    all_nodes = np.arange(nodes.shape[0])

    # Identify nodes that are neither in outbound nor object
    other_nodes = np.setdiff1d(all_nodes, np.concatenate([outbound_nodes, object_nodes]))

    # Plot the points
    plt.figure(figsize=(8, 6))

    # Plot outbound points in blue
    plt.scatter(nodes[outbound_nodes, 0], nodes[outbound_nodes, 1], color='blue', label="Outbound", s=50)

    # Plot object points in red
    plt.scatter(nodes[object_nodes, 0], nodes[object_nodes, 1], color='red', label="Object", s=50)

    # Plot all other nodes in gray
    plt.scatter(nodes[other_nodes, 0], nodes[other_nodes, 1], color='gray', label="Other Nodes", s=10)

    # Add labels and title
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('2D Mesh: Outbound and Object Physical Regions')
    plt.legend()
    plt.grid(True)
    plt.show()

def projectionMesh2Grid(mesh_elem, grad_phi, X, Y, points, method='linear'):

    w, h = X.shape
    Phi = np.zeros([2, w, h])
    gradPhi = np.zeros([2, 2, w, h])

    _,_,_,_,mesh = Post.Object(X,Y,points)

    gradPhi[0,0,:,:] = interpolate.griddata(
            (mesh_elem[:,0],mesh_elem[:,1]), grad_phi[0,0,:], (X, Y),
            method = method)*mesh
    gradPhi[0,1,:,:] = interpolate.griddata(
            (mesh_elem[:,0],mesh_elem[:,1]), grad_phi[1,0,:], (X, Y),
            method = method)*mesh
    gradPhi[1,0,:,:] = interpolate.griddata(
            (mesh_elem[:,0],mesh_elem[:,1]), grad_phi[0,1,:], (X, Y),
            method = method)*mesh
    gradPhi[1,1,:,:] = interpolate.griddata(
            (mesh_elem[:,0],mesh_elem[:,1]), grad_phi[1,1,:], (X, Y),
            method = method)*mesh

    return Phi, gradPhi

def Read_Mesh(dirRes):
    #Load all the data
    os.chdir(dirRes)
    Name = sorted(os.listdir())
    Data = np.load(Name[0])
    [a,b] = Data['x'].shape
    U = np.zeros([a-2,b-2,len(Name)])
    V = np.zeros([a-2,b-2,len(Name)])
    P = np.zeros([a-2,b-2,len(Name)])
    Omega = np.zeros([a-2,b-2,len(Name)])
    for i in range(1,len(Name)):
        Data = np.load(Name[i])
        x = Data['x']; y = Data['y']
        u = Data['u']; v = Data['v']

        # Load pressure if exist
        try:
            p = Data['p']
        except:
            p = x*0

        # Load vorticity if exist otherwise compute it
        try:
            omega = Data['omega']
        except:
            [X,Y,omega] = Post.vorticity(x,y,u,v,'circulation')
            u = u[1:len(u[:,1])-1,1:len(u[1,:])-1]
            v = v[1:len(v[:,1])-1,1:len(v[1,:])-1]
            p = p[1:len(p[:,1])-1,1:len(p[1,:])-1]

        U[:,:,i] = u; V[:,:,i] = v
        P[:,:,i] = p; Omega[:,:,i] = omega

        print('loading results:',i,'/',len(Name))

    return X, Y, U, V, Omega, P, Name

