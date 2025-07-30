#DPIV_ALGORITHM
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
from scipy.interpolate import griddata

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np
import cv2

from scipy.optimize import fmin
import skimage.transform as skt
import os

class StereoCalibrationApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Stereo Calibration")
        self.geometry("800x500")

        self.left_image = None
        self.right_image = None

        self.left_image_label = None
        self.right_image_label = None

        # Initialize grid options
        self.camera_config = "Front-Front"
        self.pattern = "TSI"
        self.dx = 10
        self.dy = 10
        self.dz = 1
        self.wz = 3

        # Initialize processing options
        self.threshold = 10
        self.min_size = 9

        self.create_widgets()

        # Variables to store the coordinates of the box
        self.box_start = None
        self.box_end = None
        self.black_box = 0

        # Bind mouse events to the labels
        self.left_image_label.bind("<Button-1>", self.start_box_l)
        self.left_image_label.bind("<ButtonRelease-1>", self.end_box)

        self.right_image_label.bind("<Button-1>", self.start_box_r)
        self.right_image_label.bind("<ButtonRelease-1>", self.end_box)

    def create_widgets(self):
        # Create a frame to hold the buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side="top", pady=10)

        # Button to load left and right images
        load_button = tk.Button(
            button_frame, text="Load Images", command=self.load_images
        )
        load_button.pack(side='left', pady=10)

        # Button to open the grid menu
        grid_button = tk.Button(button_frame, text="Select grid",
            command=self.open_grid_menu
        )
        grid_button.pack(side='left', pady=10)

        # Button to open processing options menu
        options_button = tk.Button(
            button_frame, text="Processing Options",
            command=self.open_options_menu
        )
        options_button.pack(side='left', pady=10)

        # Button to run calculation
        calculate_button = tk.Button(button_frame, text="Run Calculation",
                                     command=self.run_calculation)
        calculate_button.pack(side='left', pady=10)

        # Button to run calculation
        save_button = tk.Button(button_frame, text="Save Calibration",
                                     command=self.save_calibration)
        save_button.pack(side='left', pady=10)

        # Labels to display loaded images
        self.left_image_label = tk.Label(self)
        self.left_image_label.pack(side='left', padx=30, pady=10)

        self.right_image_label = tk.Label(self)
        self.right_image_label.pack(side='right', padx=30, pady=10)

    def load_images(self):
        """
        Load the right and left images of the Stereo Calibration and display
        them
        """

        left_image_path = filedialog.askopenfilename(
                title="Select Left Image")
        if left_image_path:
            self.left_image_o = cv2.imread(
                    left_image_path, cv2.IMREAD_GRAYSCALE)
            self.left_image = self.apply_threshold(self.left_image_o)
            self.left_image = self.bwareaopen(self.left_image)
            self.left_image_plot = image = Image.fromarray(self.left_image)
            self.left_image_plot = self.resize_image(self.left_image_plot)
            self.left_image_label.config(image=self.left_image_plot)

        right_image_path = filedialog.askopenfilename(
                title="Select Right Image")
        if right_image_path:
            self.right_image_o = cv2.imread(
                    right_image_path, cv2.IMREAD_GRAYSCALE)
            self.right_image = self.apply_threshold(self.right_image_o)
            self.right_image = self.bwareaopen(self.right_image)
            self.right_image_plot = Image.fromarray(self.right_image)
            self.right_image_plot = self.resize_image(self.right_image_plot)
            self.right_image_label.config(image=self.right_image_plot)

    def resize_image(self, image):
        #Resize the images to fit in the window
        self.org_width, self.org_height = image.size
        width = int(self.winfo_width()/2.5)
        height = int((width / self.org_width) * self.org_height)
        resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(resized_image)

        return photo_image

    def open_grid_menu(self):
        # Create and display the processing options menu
        options_menu = tk.Toplevel(self)
        options_menu.title("Processing Options")
        options_menu.geometry("200x200")

        # Configure row and column weights for responsiveness
        options_menu.grid_columnconfigure(0, weight=1)
        options_menu.grid_columnconfigure(2, weight=1)


        # Camera configuration
        l0 = tk.Label(options_menu, text="Cameras:")
        l0.grid(row=0, column=1)
        camera_list = [
            'Front-Front',
            'Front-Back'
        ]
        camera_config = tk.StringVar()
        camera_config.set(self.camera_config)
        drop_camera = tk.OptionMenu(options_menu, camera_config, *camera_list)
        drop_camera.grid(row=0, column=2, sticky="w")

        # Grid characteristics
        l3 = tk.Label(options_menu, text="grid type:")
        l3.grid(row=1, column=1)
        grid_list = [
            'TSI',
            'LaVision',
            'Help'
        ]
        grid_value = tk.StringVar()
        grid_value.set(self.pattern)
        drop_pattern = tk.OptionMenu(options_menu, grid_value, *grid_list)
        drop_pattern.grid(row=1, column=2, sticky="w")

        l4 = tk.Label(options_menu, text="dx (mm):")
        l4.grid(row=2, column=1)
        grid_dx = tk.Entry(options_menu, width=5)
        grid_dx.grid(row=2, column=2, sticky="w")
        grid_dx.insert(0, str(self.dx))

        l5 = tk.Label(options_menu, text="dy (mm):")
        l5.grid(row=3, column=1)
        grid_dy = tk.Entry(options_menu, width=5)
        grid_dy.grid(row=3, column=2, sticky="w")
        grid_dy.insert(0, str(self.dy))

        l6 = tk.Label(options_menu, text="dz (mm):")
        l6.grid(row=4, column=1)
        grid_dz = tk.Entry(options_menu, width=5)
        grid_dz.grid(row=4, column=2, sticky="w")
        grid_dz.insert(0, str(self.dz))

        l7 = tk.Label(options_menu, text="wz (mm):")
        l7.grid(row=5, column=1)
        grid_wz = tk.Entry(options_menu, width=5)
        grid_wz.grid(row=5, column=2, sticky="w")
        grid_wz.insert(0, str(self.wz))

        # Create empty columns for centering the grid
        empty_label_left = tk.Label(options_menu)
        empty_label_left.grid(row=0, column=0, rowspan=9, sticky="ns")

        empty_label_right = tk.Label(options_menu)
        empty_label_right.grid(row=0, column=3, rowspan=9, sticky="ns")

        def process(*args):
            self.dx = float(grid_dx.get())
            self.dy = float(grid_dy.get())
            self.dz = float(grid_dz.get())
            self.wz = float(grid_wz.get())
            self.camera_config = camera_config.get()
            self.pattern = grid_value.get()

            if self.pattern == "Help":
                messagebox.showinfo("Help",
                    "For the moment only the TSI and LaVision calibration "
                    "targets, used with cameras in left-right configuration "
                    "are included automatically in the code. LaVision "
                    "target, it can only be used straight, as long as "
                    "fiducial points are not used yet to get orientation. "
                    "Using different targets would require to get the cpt "
                    "files throught a different method. Contributions "
                    "to add different targets into the code "
                    "are very welcome. Please visit "
                    "https://gitlab.com/jacabello/dpivsoft_python")

        # Bind the process to the text boxes
        grid_dx.bind('<Return>', process)
        grid_dy.bind('<Return>', process)
        grid_dz.bind('<Return>', process)
        grid_wz.bind('<Return>', process)

        # Bind the process function to the listboxes' <<OptionSelected>> event
        camera_config.trace('w', process)
        grid_value.trace('w', process)

    def open_options_menu(self):
        # Create and display the processing options menu
        options_menu = tk.Toplevel(self)
        options_menu.title("Processing Options")
        options_menu.geometry("200x200")

        # Configure row and column weights for responsiveness
        options_menu.grid_columnconfigure(0, weight=1)
        options_menu.grid_columnconfigure(2, weight=1)

        # Threshold input
        l1 = tk.Label(options_menu, text="Threshold:")
        l1.grid(row=0, column=1)
        thresh = tk.Entry(options_menu, width=5)
        thresh.grid(row=0, column=2, sticky="w")
        thresh.insert(0, str(int(self.threshold)))

        # Minimun Cluster
        l2 = tk.Label(options_menu, text="Minimun size:")
        l2.grid(row=1, column=1)
        min_size = tk.Entry(options_menu, width=5)
        min_size.grid(row=1, column=2, sticky="w")
        min_size.insert(0, str(int(self.min_size)))

        # Button to add a blackbox mask
        blackbox_button = tk.Button(
            options_menu, text="Create blackbox", command=self.start_blackbox
        )
        blackbox_button.grid(
            row=2, column=1, columnspan=2, sticky="w")

        # Button to find centroid of each point
        centroid_button = tk.Button(
            options_menu, text="Find centroids", command=self.get_centroids
        )
        centroid_button.grid(
            row=3, column=1, columnspan=2, sticky="w")

        # Button to save cpt files
        CPT_button = tk.Button(
            options_menu, text="Save CPTs",
            command=self.save_cpt_button_clicked
        )
        CPT_button.grid(
            row=4, column=1, columnspan=2, sticky="w")

        # Button to load cpt files
        CPT_button = tk.Button(
            options_menu, text="Load CPTs",
            command=self.load_cpt_button_clicked
        )
        CPT_button.grid(
            row=5, column=1, columnspan=2, sticky="w")

        def process(event=None):
            self.threshold = float(thresh.get())
            self.min_size = float(min_size.get())
            self.reload_images()

        thresh.bind('<Return>', process)
        min_size.bind('<Return>', process)

        # Create empty columns for centering the grid
        empty_label_left = tk.Label(options_menu)
        empty_label_left.grid(row=0, column=0, rowspan=9, sticky="ns")

        empty_label_right = tk.Label(options_menu)
        empty_label_right.grid(row=0, column=3, rowspan=9, sticky="ns")

    def reload_images(self):
        # reload images
        if hasattr(self, 'left_image_o'):
            self.left_image = self.apply_threshold(self.left_image_o)
            self.left_image = self.bwareaopen(self.left_image)
            self.left_image_plot = Image.fromarray(self.left_image)
            self.left_image_plot = self.resize_image(self.left_image_plot)
            self.left_image_label.config(image=self.left_image_plot)

        if hasattr(self, 'right_image_o'):
            self.right_image = self.apply_threshold(self.right_image_o)
            self.right_image = self.bwareaopen(self.right_image)
            self.right_image_plot = Image.fromarray(self.right_image)
            self.right_image_plot = self.resize_image(self.right_image_plot)
            self.right_image_label.config(image=self.right_image_plot)

    def load_cpt_button_clicked(self):
        filepath = filedialog.askopenfilename(title="Select Left CPT")
        final_matrix_l = self.load_cpt_file(filepath)
        self.final_matrix_l = final_matrix_l

        filepath = filedialog.askopenfilename(title="Select right CPT")
        final_matrix_r = self.load_cpt_file(filepath)
        self.final_matrix_r = final_matrix_r

    def load_cpt_file(self, file_path):
        x = []; y = []; X = []; Y = []; Z = []

        with open(file_path, 'r') as file:
            for line in file:
                values = line.strip().split()
                x.append(float(values[0]))
                y.append(float(values[1]))
                X.append(float(values[2]))
                Y.append(float(values[3]))
                Z.append(float(values[4]))

        final_matrix = np.column_stack([x, y, X, Y, Z])

        return final_matrix

    def save_cpt_button_clicked(self):

        if hasattr(self, "final_matrix_l"):
            file_path = filedialog.asksaveasfilename(
                    title="Left CPT file", defaultextension=".cpt",
                    filetypes=[("CPT files", "*.cpt")]
            )
            if file_path:
                self.save_cpt_file(file_path, self.final_matrix_l)

            file_path = filedialog.asksaveasfilename(
                    title="Right CPT file", defaultextension=".cpt",
                    filetypes=[("CPT files", "*.cpt")]
            )
            if file_path:
                self.save_cpt_file(file_path, self.final_matrix_r)
        else:
            messagebox.showerror("Error","Get centroids first!")

    def save_cpt_file(self, filename, final_matrix):
        with open(filename, 'w') as fid:
            for row in final_matrix:
                fid.write(f'{row[0]:e}   {row[1]:e}   '
                          f'{row[2]:e}   {row[3]:e}   '
                          f'{row[4]:e}\n')

    def apply_threshold(self, image):
        threshold= np.max(image) * (self.threshold / 100)
        dummy, binary_image = cv2.threshold(
            image, threshold, 255, cv2.THRESH_BINARY
        )

        return binary_image

    def bwareaopen(self, img):
        """Remove small objects from binary image (approximation of
        bwareaopen in Matlab for 2D images).
        Args:
            img: a binary image (dtype=uint8) to remove small objects from

        Returns:
            the binary image with small objects removed
        """
        min_size = int(self.min_size)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (min_size, min_size))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

        return img

    def start_blackbox(self):
        if hasattr(self, 'left_image_o') and hasattr(self, 'right_image_o'):
            self.black_box = 1

            # Change the cursor to crosshair when the button is clicked
            self.config(cursor="crosshair")
        else:
            messagebox.showerror("Error", "Load the images first!")

    def start_box_l(self, event):
        # Store the starting coordinates of the box
        self.box_start = [event.x, event.y]
        self.right = 0
        self.left = 1

    def start_box_r(self, event):
        # Store the starting coordinates of the box
        self.box_start = [event.x, event.y]
        self.left = 0
        self.right = 1

    def end_box(self, event):

        if self.black_box:
            # Store the ending coordinates of the box
            self.box_end = [event.x, event.y]
            factor = self.org_width/self.left_image_plot.width()

            self.box_end[0] = int(self.box_end[0] *factor)
            self.box_end[1] = int(self.box_end[1] *factor)
            self.box_start[0] = int(self.box_start[0] * factor)
            self.box_start[1] = int(self.box_start[1] * factor)
            self.box_end = tuple(self.box_end)
            self.box_start = tuple(self.box_start)

            #Draw the blackbox
            if self.left:
                self.left_image_o = cv2.rectangle(
                    self.left_image_o, self.box_start,
                    self.box_end, (0,0,0),-1)
            elif self.right:
                self.right_image_o = cv2.rectangle(
                    self.right_image_o, self.box_start,
                    self.box_end, (0,0,0),-1)

            self.config(cursor="")
            self.reload_images()

        self.black_box = 0

        # Print the coordinates
        print("Box coordinates: {}, {}".format(self.box_start, self.box_end))

    def get_centroids(self):

        if hasattr(self, 'left_image_o') and hasattr(self, 'right_image_o'):
            # Get the centroid of each target dot
            self.get_coordinates()
            self.draw_circles()

            # Rearrange the centroids
            x_l, y_l, index_l, center_idx_l, fiducial_idx_l = (
                    self.sort_points(self.cX1, self.cY1,self.center_l,
                    self.fiducial_l)
            )
            x_r, y_r, index_r, center_idx_r, fiducial_idx_r = (
                    self.sort_points(self.cX2, self.cY2, self.center_r,
                    self.fiducial_r)
            )

            # Create a mesh with real positions
            X_real_l, Y_real_l, Z_real_l = self.calibrationMesh(
                    x_l, y_l, index_l, center_idx_l, "left")
            X_real_r, Y_real_r, Z_real_r = self.calibrationMesh(
                    x_r, y_r, index_r, center_idx_r, "right")

            #Create matrix with all the values
            self.final_matrix_l = np.column_stack(
                    [x_l, y_l, X_real_l, Y_real_l, Z_real_l])
            self.final_matrix_r = np.column_stack(
                    [x_r, y_r, X_real_r, Y_real_r, Z_real_r])
        else:
            messagebox.showerror("Error", "Load the images first!")


    def calibrationMesh(self, x, y, index, idx_o, camera):
        #=========================================================
        # Algorithm to associate each point to a real position
        #=========================================================

        def get_real_TSI(x, y, index, idx_o, camera):

            # find the position of the center
            real_x = np.zeros(len(x))
            real_y = np.zeros(len(x))
            real_z = np.zeros(len(x))

            for i in range(1,len(index)):
                start = index[i-1]+1
                end = index[i]+1
                rang = range(start, end)
                idx = np.argmin(abs(y[rang]-y[idx_o])) + start
                real_y[rang] = np.arange(0, len(rang))
                real_y[rang] = real_y[rang]- real_y[idx]
                real_x[rang] = i-1

            real_x -= real_x[idx_o]

            # Asociate with scale and z position

            temp = np.where(real_y == 0)[0]
            org_z = np.zeros(len(temp))
            org_z[::2] = 1

            if org_z[temp == idx_o] != 0:
                org_z = abs(org_z-1)

            for i in range(0,len(org_z)-1):
                start = index[i]+1
                end = index[i+1]
                rang = range(start, end)
                real_z[start:end:2] = 1
                if real_z[temp[i]] != org_z[i]:
                    real_z[rang] = abs(real_z[rang]-1)

            real_z -= 0.5

            # Apply scale
            real_x *= self.dx
            real_y *= self.dy
            real_z *= self.dz

            # Adapt points to camera configuration
            if self.camera_config == "Front-Back":
                if camera == "left":
                    real_z = real_z - self.wz
                    real_x = -real_x
                elif camera == "right":
                    real_z = self.wz-real_z

            return real_x, real_y, real_z

        def get_real_LaVision(x, y, index, idx_o, camera):

            # find the position of the center
            real_x = np.zeros(len(x))
            real_y = np.zeros(len(x))
            real_z = np.zeros(len(x))

            # Get row of center
            center_row = np.where(index<idx_o)[-1][-1]

            for i in range(1, len(index)):
                start = index[i-1]+1
                end = index[i]+1
                rang = range(start, end)

                real_y[rang] = i-1
                if center_row+1==i:
                    #Center row case
                    idx = np.argmin(abs(x[rang]-x[idx_o])) + start
                    real_x[idx_o] = 0
                    real_x[start:idx_o] = (
                        np.arange(-len(real_x[start:idx_o])+0.5, 0)
                    )
                    real_x[idx_o+1:end] = (
                        np.arange(0.5,len(real_x[idx_o+1:end])+0.5)
                    )
                    real_z[start:end] = -0.5

                elif (i-(center_row+1))%2 == 0:
                    idx = np.argmin(abs(x[rang]-x[idx_o+1])) + start
                    real_x[rang] = np.arange(0.5, len(rang),1)
                    real_x[rang] = real_x[rang] - real_x[idx]+0.5
                    real_z[start:end] = -0.5

                elif center_row == i:
                    #Fiducial row case
                    idx = np.argmin(abs(x[rang]-x[idx_o])) + start
                    real_x[start:idx] =np.arange(-len(real_x[start:idx]), 0)
                    real_x[idx+1] = 0.5
                    real_x[idx+2:end] =1+np.arange(0, len(real_x[idx+2:end]))
                    real_z[start:end] = 0.5

                else:
                    idx = np.argmin(abs(x[rang]-x[idx_o])) + start
                    real_x[rang] = np.arange(0, len(rang))
                    real_x[rang] = real_x[rang] - real_x[idx]
                    real_z[start:end] = 0.5

            real_y -= real_y[idx_o]

            # Apply scale
            real_x *= self.dx
            real_y *= self.dy
            real_z *= self.dz

            if self.camera_config == "Front-Back":

                raise Exception("Front-backward configuration is not aviable yet for LaVision target, as I have no example to test")

                #if camera == "left":
                #    real_z = real_z - self.wz
                #    real_x = - real_x
                #elif camera == "right":
                #    real_z = self.wz - real_z

            return real_x, real_y, real_z

        if self.pattern == "TSI":
            real_x, real_y, real_z = get_real_TSI(x, y, index, idx_o, camera)
        elif self.pattern == "LaVision":
            real_x, real_y, real_z = get_real_LaVision(x, y, index, idx_o, camera)

        return real_x, real_y, real_z

    def sort_points(self, x, y, center, fiducial, showImages=1):
        #=========================================================
        # Algorithm to sort all points in the image
        #=========================================================
        x = np.asarray(x)
        y = np.asarray(y)

        if self.pattern == "TSI":

            fiducial_idx = None

            idx = np.argsort(x)

            x = x[idx]
            y = y[idx]

            dfx = np.diff(x)
            tol = np.median(dfx)+(max(dfx)-np.median(dfx))/2

            index = [i for i in range(len(dfx)) if dfx[i] > tol]
            index.insert(0, -1)
            index.append(len(x)-1)

            for i in range(1,len(index)):
                rang = range(index[i-1]+1,index[i]+1)
                idx = index[i-1]+1 + np.argsort(y[rang])
                x[rang] = x[idx]
                y[rang] = y[idx]

            center_idx = (
                    np.where((x == center[0]) &
                    (self.org_height-y == center[1]))[0][0]
            )

            if showImages:
                plt.scatter(range(0,len(x)-1),np.diff(x))
                plt.plot([0,len(x)], [tol, tol])
                plt.plot([0,len(x)], [np.median(dfx), np.median(dfx)])
                plt.show()

        elif self.pattern == "LaVision":

            idx = np.argsort(y)

            x = x[idx]
            y = y[idx]

            dfy = np.diff(y)
            tol = np.median(dfy)+(max(dfy)-np.median(dfy))/2

            index = [i for i in range(len(dfy)) if dfy[i] > tol]
            index.insert(0, -1)
            index.append(len(y)-1)

            for i in range(1,len(index)):
                rang = range(index[i-1]+1, index[i]+1)
                idx = index[i-1]+1 + np.argsort(x[rang])
                x[rang] = x[idx]
                y[rang] = y[idx]

            center_idx = (np.where(
                    (x == center[0]) & (self.org_height-y == center[1]))[0][0]
            )
            fiducial_idx = (np.where(
                    (x == fiducial[0]) & (self.org_height-y == fiducial[1]))[0][0]
            )

        else:
            return 1

        return x, y, index, center_idx, fiducial_idx

    def get_coordinates(self):

        def find_points_TSI(image):
            cX = []; cY = [];
            # Find connected components and retrieve the labels, stats, and centroids
            num_labels, labels, stats, centroids =(
                cv2.connectedComponentsWithStats(image)
            )

            old_area = 0
            # Iterate over the objects (excluding the background) and print their centroids
            for i in range(1, num_labels):
                cX.append(int(centroids[i][0]))
                cY.append(int(centroids[i][1]))

                # Get the contour of the connected component
                contour_mask = np.uint8(labels == i)
                contours, _ = cv2.findContours(
                    contour_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contour = contours[0]

                # Get area and perimeter of the contour
                area = cv2.contourArea(contour)

                if area>old_area:
                    old_area = area
                    center_idx = i-1
                    center_l = [cX[-1], cY[-1]]

            return cX, cY, center_l, center_idx

        def find_points_LaVision(image):

            cX = []; cY = []; fiducial=0;
            # Find connected components and retrieve the labels, stats, and centroids
            num_labels, labels, stats, centroids =(
                cv2.connectedComponentsWithStats(image)
            )

            old_area = 0
            # Iterate over the objects (excluding the background) and print their centroids
            for i in range(1, num_labels):

                cX.append(int(centroids[i][0]))
                cY.append(int(centroids[i][1]))

                # Get the contour of the connected component
                contour_mask = np.uint8(labels == i)
                contours, _ = cv2.findContours(
                    contour_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contour = contours[0]

                # Get area and perimeter of the contour
                area = cv2.contourArea(contour)

                approx = cv2.approxPolyDP(
                        contour, 0.07*cv2.arcLength(contour,True),True
                )

                if len(approx)==3:
                    fiducial = [cX[-1], cY[-1]]
                    fiducial_idx = i-1

                if area>old_area:
                    old_area = area
                    center_idx = i-1
                    center = [cX[-1], cY[-1]]

            return cX, cY, center, fiducial


        if self.pattern == "TSI":
            #Get coordinates of left image
            cX1, cY1, center_l, fiducial_l = find_points_TSI(self.left_image)

            #Get coordinates of right image
            cX2, cY2, center_r, fiducial_r = find_points_TSI(self.right_image)

        elif self.pattern == "LaVision":
            #Get coordinates of left image
            cX1, cY1, center_l, fiducial_l = find_points_LaVision(self.left_image)

            #Get coordinates of right image
            cX2, cY2, center_r, fiducial_r = find_points_LaVision(self.right_image)

        # Get the variables in the class
        self.cX1 = cX1
        self.cX2 = cX2
        self.center_l = center_l
        self.center_r = center_r
        self.cY1 = self.org_height-np.asarray(cY1)
        self.cY2 = self.org_height-np.asarray(cY2)
        self.fiducial_l = fiducial_l
        self.fiducial_r = fiducial_r

    def draw_circles(self):

        radius =40
        color = (255,0,0)
        thickness = 2
        markerSize = 15
        markerType = cv2.MARKER_CROSS

        left_image = cv2.cvtColor(self.left_image, cv2.COLOR_GRAY2RGB)
        for i in range(len(self.cX1)):
            center = (self.cX1[i], self.org_height-self.cY1[i])
            left_image = cv2.circle(
                left_image, center, radius, color, thickness
            )
            cv2.drawMarker(
                left_image, center, color, markerType, markerSize, thickness
            )
        center = (self.center_l[0], self.center_l[1])
        cv2.drawMarker(
            left_image, center, (0,255,0), markerType, 100, thickness
        )
        self.left_image_plot = Image.fromarray(left_image)
        self.left_image_plot = self.resize_image(self.left_image_plot)
        self.left_image_label.config(image=self.left_image_plot)

        right_image = cv2.cvtColor(self.right_image, cv2.COLOR_GRAY2RGB)
        for i in range(len(self.cX2)):
            center = (self.cX2[i], self.org_height-self.cY2[i])
            right_image = cv2.circle(
                right_image, center, radius, color, thickness
            )
            cv2.drawMarker(
                right_image, center, color, markerType, markerSize, thickness
            )
        center = (self.center_r[0], self.center_r[1])
        cv2.drawMarker(
            right_image, center, (0,255,0), markerType, 100, thickness
        )
        self.right_image_plot = Image.fromarray(right_image)
        self.right_image_plot = self.resize_image(self.right_image_plot)
        self.right_image_label.config(image=self.right_image_plot)

    def run_calculation(self):
        if self.final_matrix_l is None or self.final_matrix_r is None:
            # Display an error message if images are not loaded
            messagebox.showerror("Error","Process Images or load CPT files")
        else:
            # Run the calculation using the loaded cpt
            self.stereo_calibration()

            return  0

    def stereo_calibration(self):

        plotfigures = 0

        # Initialize coordinates vectors
        x_l = self.final_matrix_l[:,0]
        y_l = self.final_matrix_l[:,1]
        X_l = self.final_matrix_l[:,2]
        Y_l = self.final_matrix_l[:,3]
        Z_l = self.final_matrix_l[:,4]

        x_r = self.final_matrix_r[:,0]
        y_r = self.final_matrix_r[:,1]
        X_r = self.final_matrix_r[:,2]
        Y_r = self.final_matrix_r[:,3]
        Z_r = self.final_matrix_r[:,4]

        ntot_l = len(x_l)
        ntot_r = len(x_r)

        # Initialisation of a_l, b_l
        dx_exp = np.mean(np.mean(np.diff(x_l)))
        dy_exp = np.mean(np.mean(np.diff(y_l)))
        a_l_init = np.zeros((7, 1))
        a_l_init[3] = np.mean(np.mean(np.diff(X_l))) / dx_exp
        a_l_init[5] = -np.mean(np.mean(x_l)) * a_l_init[3]
        a_l_init[6] = (np.mean(np.mean((
            X_l - a_l_init[3] * x_l - a_l_init[5]) / Z_l))
        )
        x_reg = x_l + a_l_init[6] / a_l_init[3] * Z_l
        a_l_init[0] = (-np.mean(np.mean(np.diff(
            np.diff(x_reg)))) / dx_exp**2 * a_l_init[3]
        )
        a_l_init[1] = (-np.mean(np.mean(np.diff(
            np.diff(x_reg)))) / dy_exp**2 * a_l_init[3]
        )
        a_l_init[2] = (-np.mean(np.mean(np.diff(
            np.diff(x_reg)))) / dx_exp / dy_exp * a_l_init[3]
        )
        b_l_init = np.zeros((7, 1))
        b_l_init[4] = np.mean(np.mean(np.diff(Y_l))) / dy_exp
        b_l_init[0] = (-np.mean(np.mean(
            np.diff(np.diff(y_l)))) / dx_exp**2 * b_l_init[4]
        )
        b_l_init[1] = (-np.mean(np.mean(
            np.diff(np.diff(y_l)))) / dy_exp**2 * b_l_init[4]
        )
        b_l_init[2] = (-np.mean(np.mean(
            np.diff(np.diff(y_l)))) / dx_exp / dy_exp * b_l_init[4]
        )
        b_l_init[5] = -np.mean(np.mean(y_l)) * b_l_init[4]

        # Initialisation of a_r, b_r
        dx_exp = np.mean(np.mean(np.diff(x_r)))
        dy_exp = np.mean(np.mean(np.diff(y_r)))
        a_r_init = np.zeros((7, 1))
        a_r_init[3] = np.mean(np.mean(np.diff(X_r))) / dx_exp
        a_r_init[5] = -np.mean(np.mean(x_r)) * a_r_init[3]
        a_r_init[6] = np.mean(
            np.mean((X_r - a_r_init[3] * x_r - a_r_init[5]) / Z_r)
        )
        x_reg = x_r + a_r_init[6] / a_r_init[3] * Z_r
        a_r_init[0] = (-np.mean(np.mean(
            np.diff(np.diff(x_reg)))) / dx_exp**2 * a_r_init[3]
        )
        a_r_init[1] = (-np.mean(np.mean(
            np.diff(np.diff(x_reg)))) / dy_exp**2 * a_r_init[3]
        )
        a_r_init[2] = (-np.mean(np.mean(
            np.diff(np.diff(x_reg)))) / dx_exp / dy_exp * a_r_init[3]
        )
        b_r_init = np.zeros((7, 1))
        b_r_init[4] = np.mean(np.mean(np.diff(Y_r))) / dy_exp
        b_r_init[0] = (-np.mean(np.mean(np.diff(
            np.diff(y_r)))) / dx_exp**2 * b_r_init[4]
        )
        b_r_init[1] = (-np.mean(np.mean(
            np.diff(np.diff(y_r)))) / dy_exp**2 * b_r_init[4]
        )
        b_r_init[2] = (-np.mean(np.mean(
            np.diff(np.diff(y_r)))) / dx_exp / dy_exp * b_r_init[4]
        )
        b_r_init[5] = -np.mean(np.mean(y_r)) * b_r_init[4]

        C_l = np.zeros((ntot_l, 7))
        C_r = np.zeros((ntot_r, 7))

        op = {'maxfun': 100000, 'ftol': 1e-10, 'maxiter': 100000,
              'disp': True, 'xtol': 1e-10}

        #Left
        for i in range(ntot_l):
            C_l[i, 0] = x_l[i]**2
            C_l[i, 1] = y_l[i]**2
            C_l[i, 2] = x_l[i] * y_l[i]
            C_l[i, 3] = x_l[i]
            C_l[i, 4] = y_l[i]
            C_l[i, 5] = 1
            C_l[i, 6] = Z_l[i]

        f0 = np.sum((C_l.dot(a_l_init) - X_l)**2)
        a_l = fmin(lambda a: np.sum(
            (C_l.dot(a) - X_l)**2) / f0, a_l_init, **op)

        f0 = np.sum((C_l.dot(b_l_init) - Y_l)**2)
        b_l = fmin(lambda b: np.sum(
            (C_l.dot(b) - Y_l)**2) / f0, b_l_init, **op)

        coeff_l = np.concatenate((a_l, b_l))
        C_L = np.concatenate((np.hstack((
            C_l, np.zeros_like(C_l))),
            np.hstack((np.zeros_like(C_l), C_l))))

        f0 = np.sum((C_L.dot(coeff_l) -np.concatenate((X_l, Y_l)))**2)

        #Right
        C_r = np.zeros((ntot_r, 7))
        for i in range(ntot_r):
            C_r[i, 0] = x_r[i]**2
            C_r[i, 1] = y_r[i]**2
            C_r[i, 2] = x_r[i] * y_r[i]
            C_r[i, 3] = x_r[i]
            C_r[i, 4] = y_r[i]
            C_r[i, 5] = 1
            C_r[i, 6] = Z_r[i]

        f0 = np.sum((C_r.dot(a_r_init) - X_r)**2)
        a_r = fmin(lambda a: np.sum(
            (C_r.dot(a) - X_r)**2) / f0, a_r_init, **op)

        f0 = np.sum((C_r.dot(b_r_init) - Y_r)**2)
        b_r = fmin(lambda b: np.sum(
            (C_r.dot(b) - Y_r)**2) / f0, b_r_init, **op)

        coeff_r = np.concatenate((a_r, b_r))
        C_R = np.concatenate((np.hstack((
            C_r, np.zeros_like(C_r))),
            np.hstack((np.zeros_like(C_r), C_r))))

        f0 = np.sum((C_R.dot(coeff_r) -np.concatenate((X_r, Y_r)))**2)

        XLt = C_l*a_l
        YLt = C_l*b_l
        XRt = C_r*a_r
        YRt = C_r*b_r

        theta_l = np.abs(np.arctan(a_l[6]) * 180 / np.pi)
        beta_l = np.arctan(b_l[6]) * 180 / np.pi
        theta_r = np.abs(np.arctan(a_r[6]) * 180 / np.pi)
        beta_r = np.arctan(b_r[6]) * 180 / np.pi

        fwd_a_l = a_l[:6]
        fwd_b_l = b_l[:6]
        fwd_a_r = a_r[:6]
        fwd_b_r = b_r[:6]

        self.a_l = fwd_a_l
        self.b_l = fwd_b_l
        self.a_r = fwd_a_r
        self.b_r = fwd_b_r
        self.theta_l = theta_l
        self.beta_l = beta_l
        self.theta_r = theta_r
        self.beta_r = beta_r

        pxpcm = 150
        #Error per square centimeter
        cm = (np.sqrt(max(
            [np.sum((C_L.dot(coeff_l) - np.concatenate((X_l, Y_l)))**2),
            np.sum((C_R.dot(coeff_r) - np.concatenate((X_r, Y_r)))**2)]))
            / pxpcm
        )

        if plotfigures:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            # Plot points for left camera
            ax.scatter(C_l.dot(a_l), C_l.dot(b_l), Z_l, marker='*', color='blue')

            # Plot points for right camera
            ax.scatter(C_r.dot(a_r), C_r.dot(b_r), Z_r, marker='o', color='red')

            # Plot original points for left camera
            ax.scatter(X_l, Y_l, Z_l, marker='d', color='black')

            # Plot original points for right camera
            ax.scatter(X_r, Y_r, Z_r, marker='d', color='black')

            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')

            plt.show()

        #============================================================
        # INVERSE
        #============================================================

        dx_exp = np.mean(np.mean(np.diff(X_l)))
        dy_exp = np.mean(np.mean(np.diff(Y_l)))
        a_l_init = np.zeros((7, 1))
        a_l_init[3] = np.mean(np.mean(np.diff(x_l))) / dx_exp
        a_l_init[5] = -np.mean(np.mean(X_l)) * a_l_init[3]
        a_l_init[6] = np.mean(
            np.mean((x_l - a_l_init[3] * X_l - a_l_init[5]) / Z_l)
        )
        X_reg = X_l + a_l_init[6] / a_l_init[3] * Z_l
        a_l_init[0] = (-np.mean(np.mean(
            np.diff(np.diff(X_reg)))) / dx_exp**2 * a_l_init[3]
        )
        a_l_init[1] = (-np.mean(np.mean(
            np.diff(np.diff(X_reg)))) / dy_exp**2 * a_l_init[3]
        )
        a_l_init[2] = (-np.mean(np.mean(
            np.diff(np.diff(X_reg)))) / dx_exp / dy_exp * a_l_init[3]
        )
        b_l_init = np.zeros((7, 1))
        b_l_init[4] = np.mean(np.mean(np.diff(y_l))) / dy_exp
        b_l_init[0] = (-np.mean(np.mean(
            np.diff(np.diff(Y_l)))) / dx_exp**2 * b_l_init[4]
        )
        b_l_init[1] = (-np.mean(np.mean(
            np.diff(np.diff(Y_l)))) / dy_exp**2 * b_l_init[4]
        )
        b_l_init[2] = (-np.mean(np.mean(
            np.diff(np.diff(Y_l)))) / dx_exp / dy_exp * b_l_init[4]
        )
        b_l_init[5] = -np.mean(np.mean(Y_l)) * b_l_init[4]

        dx_exp = np.mean(np.mean(np.diff(X_r)))
        dy_exp = np.mean(np.mean(np.diff(Y_r)))
        a_r_init = np.zeros((7, 1))
        a_r_init[3] = np.mean(np.mean(np.diff(x_r))) / dx_exp
        a_r_init[5] = -np.mean(np.mean(X_r)) * a_r_init[4]
        a_r_init[6] = np.mean(np.mean(
            (x_r - a_r_init[3] * X_r - a_r_init[5]) / Z_r)
        )
        x_reg = X_r + a_r_init[6] / a_r_init[3] * Z_r
        a_r_init[0] = (-np.mean(np.mean(
            np.diff(np.diff(x_reg)))) / dx_exp**2 * a_r_init[3]
        )
        a_r_init[1] = (-np.mean(np.mean(
            np.diff(np.diff(x_reg)))) / dy_exp**2 * a_r_init[3]
        )
        a_r_init[2] = (-np.mean(np.mean(
            np.diff(np.diff(x_reg)))) / dx_exp / dy_exp * a_r_init[3]
        )
        b_r_init = np.zeros((7, 1))
        b_r_init[4] = np.mean(np.mean(np.diff(y_r))) / dy_exp
        b_r_init[0] = (-np.mean(np.mean(
            np.diff(np.diff(Y_r)))) / dx_exp**2 * b_r_init[4]
        )
        b_r_init[1] = (-np.mean(np.mean(
            np.diff(np.diff(Y_r)))) / dy_exp**2 * b_r_init[4]
        )
        b_r_init[2] = (-np.mean(np.mean(
            np.diff(np.diff(Y_r)))) / dx_exp / dy_exp * b_r_init[4]
        )
        b_r_init[5] = -np.mean(np.mean(Y_r)) * b_r_init[4]

        C_l = np.zeros((ntot_l, 7))
        C_r = np.zeros((ntot_r, 7))
        for i in range(ntot_l):
            C_l[i, 0] = X_l[i]**2
            C_l[i, 1] = Y_l[i]**2
            C_l[i, 2] = X_l[i] * Y_l[i]
            C_l[i, 3] = X_l[i]
            C_l[i, 4] = Y_l[i]
            C_l[i, 5] = 1
            C_l[i, 6] = Z_l[i]

        f0 = np.sum((C_l.dot(a_l_init) - x_l)**2)
        a_l = fmin(lambda a: np.sum((C_l.dot(a) - x_l)**2) / f0, a_l_init, **op)

        f0 = np.sum((C_l.dot(b_l_init) - y_l)**2)
        b_l = fmin(lambda b: np.sum((C_l.dot(b) - y_l)**2) / f0, b_l_init, **op)
        coeff_l = np.concatenate((a_l, b_l))
        C_L = np.concatenate((np.hstack(
            (C_l, np.zeros_like(C_l))), np.hstack((np.zeros_like(C_l), C_l))))
        f0 = np.sum((C_L.dot(coeff_l) - np.concatenate((x_l, y_l)))**2)
        coeff_l = fmin(lambda coeff:
            np.sum((C_L.dot(coeff) - np.concatenate((x_l, y_l)))**2) / f0,
            coeff_l, **op
        )
        a_l = coeff_l[:7]
        b_l = coeff_l[7:14]

        for i in range(ntot_r):
            C_r[i, 0] = X_r[i]**2
            C_r[i, 1] = Y_r[i]**2
            C_r[i, 2] = X_r[i] * Y_r[i]
            C_r[i, 3] = X_r[i]
            C_r[i, 4] = Y_r[i]
            C_r[i, 5] = 1
            C_r[i, 6] = Z_r[i]

        f0 = np.sum((C_r.dot(a_r_init) - x_r)**2)
        a_r = fmin(lambda a: np.sum((C_r.dot(a) - x_r)**2) / f0, a_r_init, **op)

        f0 = np.sum((C_r.dot(b_r_init) - y_r)**2)
        b_r = fmin(lambda b: np.sum((C_r.dot(b) - y_r)**2) / f0, b_r_init, **op)
        coeff_r = np.concatenate((a_r, b_r))
        C_R = np.concatenate((np.hstack((C_r, np.zeros_like(C_r))),
            np.hstack((np.zeros_like(C_r), C_r)))
        )
        f0 = np.sum((C_R.dot(coeff_r) - np.concatenate((x_r, y_r)))**2)
        coeff_r = fmin(lambda coeff:
            np.sum((C_R.dot(coeff) - np.concatenate((x_r, y_r)))**2) / f0,
            coeff_r, **op
        )
        a_r = coeff_r[:7]
        b_r = coeff_r[7:14]

        a_l = a_l[:6]
        b_l = b_l[:6]
        a_r = a_r[:6]
        b_r = b_r[:6]

        Xreal = np.concatenate((X_l, X_r))
        Yreal = np.concatenate((Y_l, Y_r))
        Xp = np.array([[1, 1],
                       [self.org_width, 1],
                       [self.org_width, self.org_height],
                       [1, self.org_height],
                       [1, 1]])

        def forward_mapping_left(x):
            return np.column_stack(
                (fwd_a_l[0]*x[:, 0]**2 + fwd_a_l[1]*x[:, 1]**2
                 + fwd_a_l[2]*x[:, 0]*x[:, 1] + fwd_a_l[3]*x[:, 0]
                 + fwd_a_l[4]*x[:, 1] + fwd_a_l[5]*np.ones(x.shape[0]),
                 fwd_b_l[0]*x[:, 0]**2 + fwd_b_l[1]*x[:, 1]**2
                 + fwd_b_l[2]*x[:, 0]*x[:, 1] + fwd_b_l[3]*x[:, 0]
                 + fwd_b_l[4]*x[:, 1] + fwd_b_l[5]*np.ones(x.shape[0]))
            )

        def inverse_mapping_left(x, unused):
            return np.column_stack(
                (a_l[0]*x[:, 0]**2 + a_l[1]*x[:, 1]**2
                + a_l[2]*x[:, 0]*x[:, 1] + a_l[3]*x[:, 0]
                + a_l[4]*x[:, 1] + a_l[5]*np.ones(x.shape[0]),
                b_l[0]*x[:, 0]**2 + b_l[1]*x[:, 1]**2 + b_l[2]*x[:, 0]*x[:, 1]
                + b_l[3]*x[:, 0] + b_l[4]*x[:, 1] + b_l[5]*np.ones(x.shape[0]))
            )

        def forward_mapping_right(x):
            return np.column_stack(
                (fwd_a_r[0]*x[:, 0]**2 + fwd_a_r[1]*x[:, 1]**2
                 + fwd_a_r[2]*x[:, 0]*x[:, 1] + fwd_a_r[3]*x[:, 0]
                 + fwd_a_r[4]*x[:, 1] + fwd_a_r[5]*np.ones(x.shape[0]),
                 fwd_b_r[0]*x[:, 0]**2 + fwd_b_r[1]*x[:, 1]**2
                 + fwd_b_r[2]*x[:, 0]*x[:, 1] + fwd_b_r[3]*x[:, 0]
                 + fwd_b_r[4]*x[:, 1] + fwd_b_r[5]*np.ones(x.shape[0]))
            )

        def inverse_mapping_right(x, unused):
            return np.column_stack(
                (a_r[0]*x[:, 0]**2 + a_r[1]*x[:, 1]**2 + a_r[2]*x[:, 0]*x[:, 1]
                + a_r[3]*x[:, 0] + a_r[4]*x[:, 1] + a_r[5]*np.ones(x.shape[0]),
                b_r[0]*x[:, 0]**2 + b_r[1]*x[:, 1]**2 + b_r[2]*x[:, 0]*x[:, 1]
                + b_r[3]*x[:, 0] + b_r[4]*x[:, 1] + b_r[5]*np.ones(x.shape[0]))
            )

        ndims_in = 2
        ndims_out = 2
        tformleft = skt.PiecewiseAffineTransform()
        tformleft.estimate(Xp, forward_mapping_left(Xp))
        tformleft.inverse_map = inverse_mapping_left

        tformright = skt.PiecewiseAffineTransform()
        tformright.estimate(Xp, forward_mapping_right(Xp))
        tformright.inverse_map = inverse_mapping_right

        fXpL = tformleft(Xp)
        fXpR = tformright(Xp)

        print('Finished')

        Xpin = np.array([[48, 48],
                         [48, 1938],
                         [1938, 1938],
                         [1938, 48],
                         [48, 48]])

        fXpLin = tformleft(Xpin)  # /150-10
        fXpRin = tformright(Xpin)  # /150-10

        plt.plot(fXpL[:,0], fXpL[:,1], '*-', fXpR[:,0], fXpR[:,1], 'o-',
            Xreal, Yreal, '.r')
        plt.plot(0, 0, '+k', markersize=25)
        text = "error =" + str(cm)
        plt.title(text)
        plt.xlabel('X (mm)')
        plt.ylabel('Y (mm)')
        plt.show()

        return fwd_a_l, fwd_b_l, fwd_a_r, fwd_b_r, theta_l, beta_l, theta_r, beta_r

    def save_calibration(self):

        if hasattr(self, 'a_l') and hasattr(self, 'beta_r'):
            file_path = filedialog.asksaveasfilename(
                    title="Calibration file", defaultextension=".npz",
                    filetypes=[("numpy files", "*.npz")]
            )
            np.savez(file_path, a_l=self.a_l, b_l=self.b_l, a_r=self.a_r,
                     b_r=self.b_r, theta_l=self.theta_l, beta_l=self.beta_l, 
                     theta_r=self.theta_r, beta_r=self.beta_r)
        else:
            messagebox.showerror("Error", "Run calculation first!")

def stereo_velocity(x_l, y_l, u_l, v_l, x_r, y_r, u_r, v_r, calibration):
    a_l = calibration.a_l
    b_l = calibration.b_l
    a_r = calibration.a_r
    b_r = calibration.b_r
    theta_l = calibration.theta_l
    beta_l = calibration.beta_l
    theta_r = calibration.theta_r
    beta_r = calibration.beta_r

    theta_l_pi = theta_l / 180 * np.pi
    theta_r_pi = theta_r / 180 * np.pi
    beta_l_pi = beta_l / 180 * np.pi
    beta_r_pi = beta_r / 180 * np.pi
    if any(
        var is None or np.any(np.isnan(var))
        for var in [a_l, b_l, a_r, b_r, theta_l, theta_r, beta_l, beta_r]
    ):
        warndlg('Please enter the parameters(aij and the angle)!', 'WARNING!')
    else:
        u_l_c = ((2 * a_l[0] * x_l + a_l[2] * y_l + a_l[3]) * u_l
                 + (2 * a_l[1] * y_l + a_l[2] * x_l + a_l[4])
                 * v_l).flatten()
        v_l_c = ((2 * b_l[0] * x_l + b_l[2] * y_l + b_l[3]) * u_l
                 + (2 * b_l[1] * y_l + b_l[2] * x_l + b_l[4])
                 * v_l).flatten()

        u_r_c = ((2 * a_r[0] * x_r + a_r[2] * y_r + a_r[3]) * u_r
                 + (2 * a_r[1] * y_r + a_r[2] * x_r + a_r[4])
                 * v_r).flatten()
        v_r_c = ((2 * b_r[0] * x_r + b_r[2] * y_r + b_r[3]) * u_r
                 + (2 * b_r[1] * y_r + b_r[2] * x_r + b_r[4])
                 * v_r).flatten()

        X_z_l = (a_l[0] * (x_l ** 2) + a_l[1] * (y_l ** 2)
                 + a_l[2] * (x_l * y_l) + a_l[3] * x_l
                 + a_l[4] * y_l + a_l[5])
        size_m = X_z_l.shape
        X_z_l = X_z_l.flatten()

        Y_z_l = (b_l[0] * (x_l ** 2) + b_l[1] * (y_l ** 2)
                 + b_l[2] * (x_l * y_l) + b_l[3] * x_l
                 + b_l[4] * y_l + b_l[5]).flatten()

        X_z_r = (a_r[0] * (x_r ** 2) + a_r[1] * (y_r ** 2)
                 + a_r[2] * (x_r * y_r) + a_r[3] * x_r
                 + a_r[4] * y_r + a_r[5]).flatten()
        Y_z_r = (b_r[0] * (x_r ** 2) + b_r[1] * (y_r ** 2)
                 + b_r[2] * (x_r * y_r) + b_r[3] * x_r
                 + b_r[4] * y_r + b_r[5]).flatten()

        x_sup = np.max([np.max(X_z_l), np.max(X_z_r)])
        x_inf = np.min([np.min(X_z_l), np.min(X_z_r)])
        y_sup = np.max([np.max(Y_z_l), np.max(Y_z_r)])
        y_inf = np.min([np.min(Y_z_l), np.min(Y_z_r)])

        deltx_reg = (x_sup - x_inf) / (size_m[1] - 1)
        delty_reg = (y_sup - y_inf) / (size_m[0] - 1)
        x_reg, y_reg = np.meshgrid(
                np.arange(x_inf, x_sup + deltx_reg, deltx_reg),
                np.arange(y_inf, y_sup + delty_reg, delty_reg))

        U_l = griddata(
            (X_z_l, Y_z_l), u_l_c, (x_reg, y_reg), method='linear')
        V_l = griddata(
            (X_z_l, Y_z_l), v_l_c, (x_reg, y_reg), method='linear')
        U_r = griddata(
            (X_z_r, Y_z_r), u_r_c, (x_reg, y_reg), method='linear')
        V_r = griddata(
            (X_z_r, Y_z_r), v_r_c, (x_reg, y_reg), method='linear')

        u = ((U_r * np.tan(theta_l_pi) + U_l * np.tan(theta_r_pi))
             / (np.tan(theta_r_pi) + np.tan(theta_l_pi)))
        v = ((V_l + V_r) / 2 + (U_l - U_r) / 2 * (np.tan(beta_l_pi)
            - np.tan(beta_r_pi)) / (np.tan(theta_r_pi) + np.tan(theta_l_pi)))
        u_z = (U_l - U_r) / (np.tan(theta_r_pi) + np.tan(theta_l_pi))

        x = x_reg
        y = y_reg

        stereo = 1

        return x, y, u, v, u_z

def save(x, y, u, v, u_z, filename, option='dpivsoft', Matlab=False, param=False):
    """
    save flow field to a file. Option indicates the saving
    format.

    dpivsof: save in python .npz file using the original
    formating of dpivsoft in matlab

    openpiv: save the field in an ascii file compatible
    with openpiv
    """

    from dpivsoft.Classes  import Parameters

    # Scale results
    x = x
    y = y
    u = u/Parameters.delta_t
    v = v/Parameters.delta_t
    u_z = u_z/Parameters.delta_t

    if Matlab:
        mdic = {"x":x*1.0,  "y":y*1.0,  "u":u*1.0, "v":v*1.0, "u_z":u_z*1.0,
               "calibration": float(Parameters.calibration),
               "delta_t": float(Parameters.delta_t),
               "median_limit": float(Parameters.median_limit),
               "no_calculation_1": float(Parameters.no_iter_1),
               "no_calculation_2": float(Parameters.no_iter_2),
               "box_size_1_x": float(Parameters.box_size_1_x),
               "box_size_1_y": float(Parameters.box_size_1_y),
               "box_size_2_x": float(Parameters.box_size_2_x),
               "box_size_2_y": float(Parameters.box_size_2_y),
               "no_boxes_1_x": float(Parameters.no_boxes_1_x),
               "no_boxes_1_y": float(Parameters.no_boxes_1_y),
               "no_boxes_2_x": float(Parameters.no_boxes_2_x),
               "no_boxes_2_y": float(Parameters.no_boxes_2_y),
               "no_calculation": float(Parameters.no_iter_1),
               "direct_calculation": float(Parameters.direct_calc),
               "gaussian_size": float(Parameters.gaussian_size),
               "window_1_x": float(Parameters.window_1_x),
               "window_1_y": float(Parameters.window_1_y),
               "window_2_x": float(Parameters.window_2_x),
               "window_2_y": float(Parameters.window_2_y),
               "weighting": float(Parameters.weighting),
               "peak_ratio": float(Parameters.peak_ratio),
               "image_width": float(Parameters.Data.width),
               "image_height": float(Parameters.Data.height),
               "mask": float(Parameters.mask)}
        savemat(filename+'.mat', mdic)

    if option == 'dpivsoft':
        if param:
            np.savez(filename, x=x,  y=y,  u=u,  v=v, u_z=u_z,
                    calibration = Parameters.calibration,
                    delta_t = Parameters.delta_t,
                    median_limit = Parameters.median_limit,
                    gaussian_size = Parameters.gaussian_size,
                    no_calculation_1 = Parameters.no_iter_1,
                    no_calculation_2 = Parameters.no_iter_2,
                    box_size_1_x = Parameters.box_size_1_x,
                    box_size_1_y = Parameters.box_size_1_y,
                    box_size_2_x = Parameters.box_size_2_x,
                    box_size_2_y = Parameters.box_size_2_y,
                    window_1_x = Parameters.window_1_x,
                    window_1_y = Parameters.window_1_y,
                    window_2_x = Parameters.window_2_x,
                    window_2_y = Parameters.window_2_y,
                    weighting = Parameters.weighting,
                    peak_ratio = Parameters.peak_ratio,
                    mask = Parameters.mask,
                    direct_calc = Parameters.direct_calc
                    )
        else:
            np.savez(filename, x=x,  y=y,  u=u,  v=v, u_z=u_z,
                    calibration = Parameters.calibration)

    elif option == 'openpiv':
        fmt="%8.4f"
        delimiter="\t"

        # Build output array
        out = np.vstack([m.flatten() for m in [x, y, u, v, u_z, grid.mask_2]])

        np.savetxt(
            filename,
            out.T,
            fmt=fmt,
            delimiter=delimiter,
            header="x"
            + delimiter
            + "y"
            + delimiter
            + "u"
            + delimiter
            + "v"
            + delimiter
            + "u_z"
            + delimiter
            + "mask",
            )
    else:
        sys.exit("Saving option not found")


if __name__ == "__main__":
    app = StereoCalibrationApp()
    app.mainloop()

def calibration_GUI():
    app = StereoCalibrationApp()
    app.mainloop()
