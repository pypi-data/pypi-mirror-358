from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "dpivsoft",
    version="0.4.0",
    url="https://gitlab.com/jacabello/dpivsoft_python",
    author = "Jorge Aguilar-Cabello",
    python_requires=">=3.7",
    packages = find_packages(),
    include_package_data = True,
    long_description = long_description,
    long_description_content_type = "text/markdown",
    setup_requires=[
        'setuptools',
    ],
    install_requires = [
        'numpy>=1.3,<1.24.0',
        'reikna>=0.7.6',
        'scipy==1.11.1',
        'scikit-image>=0.20',
        'opencv-python==4.8.0.74',
        'Pillow>=9',
        'matplotlib>=3',
        'PyYAML>=5.4',
        'pyopencl>=2021',
        'Shapely>=1.7',
        'importlib_resources>=5',
        'meshio==5.3.5',
        'gmsh==4.13.1',
        'scikit-fem==10.0.2',
        'scikit-learn',

    ],
    extras_require = {
        "dev": [
            "pytest>=3.7",
        ],
    },
    classifiers=[
         # Sublist of all supported Python versions.
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',

        #Miscelaneous metadata
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
    ],
)
