"""Core functionality tests without any package imports."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pytest


class NiftiLoaderForTesting:
    """Test core NiftiLoader functionality without Qt dependencies."""
    
    def __init__(self):
        self.supported_formats = {'.nii', '.nii.gz'}
        self.current_file = None
        self.current_nii = None

    def _is_nifti_file(self, file_path: Path) -> bool:
        """Check if file is a NIfTI file"""
        suffixes = [s.lower() for s in file_path.suffixes]

        # Check .nii.gz
        if len(suffixes) >= 2 and suffixes[-2] == '.nii' and suffixes[-1] == '.gz':
            return True

        # Check .nii
        if file_path.suffix.lower() == '.nii':
            return True

        return False

    def _extract_data_info(self) -> Dict:
        """Extract data statistics information"""
        data = self.current_nii.get_fdata()

        return {
            'shape': list(data.shape),
            'ndim': data.ndim,
            'dtype': str(data.dtype),
            'min_value': float(np.min(data)),
            'max_value': float(np.max(data)),
            'mean_value': float(np.mean(data)),
            'std_value': float(np.std(data)),
            'median_value': float(np.median(data)),
            'unique_values_count': int(len(np.unique(data))),
            'non_zero_count': int(np.count_nonzero(data)),
            'zero_count': int(np.sum(data == 0)),
            'nan_count': int(np.sum(np.isnan(data))),
            'inf_count': int(np.sum(np.isinf(data))),
        }


def test_loader_initialization():
    """Test NiftiLoader initialization."""
    loader = NiftiLoaderForTesting()
    assert loader.supported_formats == {'.nii', '.nii.gz'}
    assert loader.current_file is None
    assert loader.current_nii is None


def test_file_format_detection():
    """Test NiftiLoader file format detection."""
    loader = NiftiLoaderForTesting()
    
    # Valid formats
    assert loader._is_nifti_file(Path("test.nii")) is True
    assert loader._is_nifti_file(Path("test.nii.gz")) is True
    assert loader._is_nifti_file(Path("data.NII")) is True
    assert loader._is_nifti_file(Path("brain.NII.GZ")) is True
    
    # Invalid formats
    assert loader._is_nifti_file(Path("test.txt")) is False
    assert loader._is_nifti_file(Path("test.nii.txt")) is False
    assert loader._is_nifti_file(Path("test.gz")) is False
    assert loader._is_nifti_file(Path("test")) is False


def test_data_statistics_extraction():
    """Test data statistics extraction with mock data."""
    loader = NiftiLoaderForTesting()
    
    # Create mock 3D data
    mock_data = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    
    class MockNiftiImage:
        def get_fdata(self):
            return mock_data
    
    loader.current_nii = MockNiftiImage()
    
    data_info = loader._extract_data_info()
    
    # Check basic properties
    assert data_info['shape'] == [2, 2, 2]
    assert data_info['ndim'] == 3
    assert data_info['min_value'] == 1.0
    assert data_info['max_value'] == 8.0
    assert data_info['mean_value'] == 4.5
    assert data_info['unique_values_count'] == 8
    assert data_info['non_zero_count'] == 8
    assert data_info['zero_count'] == 0


def test_data_with_zeros_and_nans():
    """Test data statistics with zeros and NaN values."""
    loader = NiftiLoaderForTesting()
    
    # Create mock data with zeros and NaN
    mock_data = np.array([0, 1, 2, np.nan, 0, 5])
    
    class MockNiftiImage:
        def get_fdata(self):
            return mock_data
    
    loader.current_nii = MockNiftiImage()
    
    data_info = loader._extract_data_info()
    
    # Check properties with special values
    assert data_info['shape'] == [6]
    assert data_info['ndim'] == 1
    assert data_info['zero_count'] == 2
    assert data_info['nan_count'] == 1
    assert data_info['non_zero_count'] == 4  # NaN counts as non-zero in numpy 