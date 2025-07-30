from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "A comprehensive napari plugin for NIfTI file analysis and visualization"

setup(
    name="napari-nifti-viewer",
    version="0.1.1",
    author="Yohanchiu",
    author_email="qyhohh@163.com",
    description="A comprehensive napari plugin for NIfTI file analysis and visualization",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yohanchiu/napari-nifti-viewer",
    project_urls={
        "Bug Tracker": "https://github.com/yohanchiu/napari-nifti-viewer/issues",
        "Documentation": "https://github.com/yohanchiu/napari-nifti-viewer/wiki",
        "Source Code": "https://github.com/yohanchiu/napari-nifti-viewer",
        "Changelog": "https://github.com/yohanchiu/napari-nifti-viewer/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "napari_nifti_viewer": ["napari.yaml"],
    },
    python_requires=">=3.8",
    install_requires=[
        "napari>=0.4.18",
        "numpy>=1.21.0",
        "nibabel>=5.2.1",
        "qtpy>=2.0.0",
        "magicgui>=0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
            "pre-commit",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-cov",
        ],
    },
    entry_points={
        "napari.manifest": [
            "napari-nifti-viewer = napari_nifti_viewer:napari.yaml",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: napari",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="napari, nifti, neuroimaging, medical imaging, visualization, plugin",
    zip_safe=False,
) 