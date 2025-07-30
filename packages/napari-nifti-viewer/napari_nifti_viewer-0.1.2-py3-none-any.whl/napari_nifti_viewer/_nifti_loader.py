import json
from pathlib import Path
from typing import Dict, List, Tuple, Union

import nibabel as nib
import numpy as np


class NiftiLoader:
    """Specialized loader for NIfTI files, extracting data, metadata, etc."""

    def __init__(self):
        self.supported_formats = {'.nii', '.nii.gz'}
        self.current_file = None
        self.current_nii = None

    def load_file(self, file_path: Union[str, Path]) -> Tuple[np.ndarray, Dict]:
        """Load NIfTI file and extract all information

        Args:
            file_path: Path to NIfTI file

        Returns:
            (image data, complete metadata dictionary)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        # Check file format
        if not self._is_nifti_file(file_path):
            raise ValueError(
                "Unsupported file format, only .nii and .nii.gz are supported"
            )

        # Load NIfTI file
        self.current_file = file_path
        self.current_nii = nib.load(str(file_path))

        # Extract data
        data = self.current_nii.get_fdata()

        # Extract all metadata
        metadata = self._extract_all_metadata()

        return data, metadata

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

    def _extract_all_metadata(self) -> Dict:
        """Extract all metadata information from NIfTI file"""
        if self.current_nii is None:
            return {}

        metadata = {}

        # Basic file information
        metadata['file_info'] = self._extract_file_info()

        # Header information
        metadata['header'] = self._extract_header_info()

        # Affine transformation matrix
        metadata['affine'] = self._extract_affine_info()

        # Data information
        metadata['data_info'] = self._extract_data_info()

        # Coordinate system information
        metadata['coordinate_system'] = self._extract_coordinate_info()

        # Label information (if exists)
        metadata['labels'] = self._extract_label_info()

        # Extension header information (if exists)
        metadata['extensions'] = self._extract_extensions()

        return metadata

    def _extract_file_info(self) -> Dict:
        """Extract basic file information"""
        return {
            'file_path': str(self.current_file),
            'file_name': self.current_file.name,
            'file_size': self.current_file.stat().st_size,
            'format': 'NIfTI',
            'version': self.current_nii.header.get('sizeof_hdr', 348),
        }

    def _extract_header_info(self) -> Dict:
        """Extract detailed NIfTI header information"""
        header = self.current_nii.header

        header_info = {}

        # Basic header fields
        basic_fields = [
            'sizeof_hdr',
            'data_type',
            'db_name',
            'extents',
            'session_error',
            'regular',
            'dim_info',
            'dim',
            'intent_p1',
            'intent_p2',
            'intent_p3',
            'intent_code',
            'datatype',
            'bitpix',
            'slice_start',
            'pixdim',
            'vox_offset',
            'scl_slope',
            'scl_inter',
            'slice_end',
            'slice_code',
            'xyzt_units',
            'cal_max',
            'cal_min',
            'slice_duration',
            'toffset',
            'glmax',
            'glmin',
            'descrip',
            'aux_file',
            'qform_code',
            'sform_code',
            'quatern_b',
            'quatern_c',
            'quatern_d',
            'qoffset_x',
            'qoffset_y',
            'qoffset_z',
            'srow_x',
            'srow_y',
            'srow_z',
            'intent_name',
            'magic',
        ]

        for field in basic_fields:
            try:
                value = header.get(field)
                if value is not None:
                    # Convert numpy types to Python native types for JSON serialization
                    if isinstance(value, np.ndarray):
                        header_info[field] = value.tolist()
                    elif isinstance(value, (np.integer, np.floating)):
                        header_info[field] = value.item()
                    elif isinstance(value, bytes):
                        header_info[field] = value.decode(
                            'utf-8', errors='ignore'
                        ).strip('\x00')
                    else:
                        header_info[field] = value
            except Exception as e:
                header_info[field] = f"Extraction failed: {str(e)}"

        # Add explanatory information
        header_info['explanations'] = self._get_header_explanations(header_info)

        return header_info

    def _extract_affine_info(self) -> Dict:
        """Extract affine transformation matrix information"""
        affine = self.current_nii.affine

        return {
            'affine_matrix': affine.tolist(),
            'translation': affine[:3, 3].tolist(),
            'rotation_scaling': affine[:3, :3].tolist(),
            'determinant': float(np.linalg.det(affine[:3, :3])),
            'is_orthogonal': bool(
                np.allclose(np.dot(affine[:3, :3], affine[:3, :3].T), np.eye(3))
            ),
        }

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

    def _extract_coordinate_info(self) -> Dict:
        """Extract coordinate system information"""
        header = self.current_nii.header

        # Get voxel size
        pixdim = header.get_zooms()

        # Get unit information
        xyzt_units = header.get('xyzt_units', 0)
        spatial_unit = xyzt_units & 0x07
        temporal_unit = (xyzt_units & 0x38) >> 3

        spatial_units_map = {
            0: 'Unknown',
            1: 'meters (m)',
            2: 'millimeters (mm)',
            3: 'micrometers (μm)',
        }

        temporal_units_map = {
            0: 'Unknown',
            8: 'seconds (s)',
            16: 'milliseconds (ms)',
            24: 'microseconds (μs)',
        }

        return {
            'voxel_size': list(pixdim) if pixdim else [],
            'spatial_unit': spatial_units_map.get(
                spatial_unit, f'Unknown unit ({spatial_unit})'
            ),
            'temporal_unit': temporal_units_map.get(
                temporal_unit, f'Unknown unit ({temporal_unit})'
            ),
            'qform_code': int(header.get('qform_code', 0)),
            'sform_code': int(header.get('sform_code', 0)),
            'slice_code': int(header.get('slice_code', 0)),
        }

    def _extract_label_info(self) -> Dict:
        """Extract label information (if it exists)"""
        data = self.current_nii.get_fdata()

        # Check if this might be a label image
        unique_values = np.unique(data)

        label_info = {
            'unique_values': unique_values.tolist(),
            'is_likely_labels': self._is_likely_label_image(data, unique_values),
            'label_count': len(unique_values),
        }

        # If likely a label image, extract more information
        if label_info['is_likely_labels']:
            label_info['label_statistics'] = {}
            for label_val in unique_values:
                mask = data == label_val
                label_info['label_statistics'][str(float(label_val))] = {
                    'voxel_count': int(np.sum(mask)),
                    'percentage': float(np.sum(mask) / data.size * 100),
                }

        return label_info

    def _is_likely_label_image(
        self, data: np.ndarray, unique_values: np.ndarray
    ) -> bool:
        """Determine if this is likely a label image"""
        # Heuristic rules for label detection

        # 1. If unique values are few and integers
        if len(unique_values) <= 50 and np.allclose(
            unique_values, unique_values.astype(int)
        ):
            return True

        # 2. If data type is integer
        if np.issubdtype(data.dtype, np.integer):
            return True

        # 3. If all values are integers (even if data type is float)
        if np.allclose(data, np.round(data)):
            return True

        return False

    def _extract_extensions(self) -> List[Dict]:
        """Extract NIfTI extension information"""
        extensions = []

        if hasattr(self.current_nii, 'extra') and self.current_nii.extra:
            for i, ext in enumerate(self.current_nii.extra):
                ext_info = {
                    'index': i,
                    'esize': ext.get('esize', 0),
                    'ecode': ext.get('ecode', 0),
                }

                # Try to decode extension data
                if 'edata' in ext:
                    try:
                        ext_info['edata'] = ext['edata'].decode(
                            'utf-8', errors='ignore'
                        )
                    except (UnicodeDecodeError, AttributeError):
                        ext_info['edata'] = f"Binary data (length: {len(ext['edata'])})"

                extensions.append(ext_info)

        return extensions

    def _get_header_explanations(self, header_info: Dict) -> Dict:
        """Provide explanations for header fields"""
        explanations = {}

        # Data type explanations
        datatype_map = {
            2: 'Unsigned char (uint8)',
            4: 'Signed short (int16)',
            8: 'Signed int (int32)',
            16: 'Single precision float (float32)',
            64: 'Double precision float (float64)',
            256: 'Signed char (int8)',
            512: 'Unsigned short (uint16)',
            768: 'Unsigned int (uint32)',
        }

        if 'datatype' in header_info:
            explanations['datatype'] = datatype_map.get(
                header_info['datatype'], f"Unknown datatype ({header_info['datatype']})"
            )

        # Intent code explanations
        intent_map = {
            0: 'No special intent',
            2: 'Correlation coefficient',
            3: 'T-statistic',
            4: 'F-statistic',
            5: 'Z-score',
        }

        if 'intent_code' in header_info:
            explanations['intent_code'] = intent_map.get(
                header_info['intent_code'],
                f"Other intent ({header_info['intent_code']})",
            )

        return explanations

    def get_metadata_summary(self, metadata: Dict) -> str:
        """Generate human-readable metadata summary"""
        summary = []

        # File information
        if 'file_info' in metadata:
            info = metadata['file_info']
            summary.append(f"Filename: {info.get('file_name', 'Unknown')}")
            summary.append(
                f"File size: {info.get('file_size', 0) / 1024 / 1024:.2f} MB"
            )

        # Data information
        if 'data_info' in metadata:
            data = metadata['data_info']
            summary.append(f"Data shape: {data.get('shape', [])}")
            summary.append(f"Data type: {data.get('dtype', 'Unknown')}")
            summary.append(
                f"Value range: [{data.get('min_value', 0):.3f}, {data.get('max_value', 0):.3f}]"
            )
            summary.append(f"Mean value: {data.get('mean_value', 0):.3f}")
            summary.append(f"Std deviation: {data.get('std_value', 0):.3f}")

        # Coordinate system information
        if 'coordinate_system' in metadata:
            coord = metadata['coordinate_system']
            if coord.get('voxel_size'):
                summary.append(
                    f"Voxel size: {[f'{v:.3f}' for v in coord['voxel_size']]} {coord.get('spatial_unit', '')}"
                )

        # Label information
        if 'labels' in metadata and metadata['labels'].get('is_likely_labels'):
            labels = metadata['labels']
            summary.append(f"Label image: Yes")
            summary.append(f"Label count: {labels.get('label_count', 0)}")

        return "\n".join(summary)

    def export_metadata_to_json(
        self, metadata: Dict, output_path: Union[str, Path]
    ) -> None:
        """Export metadata to JSON file"""
        output_path = Path(output_path)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Deep copy and convert numpy types to JSON serializable types
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, bytes):
                return obj.decode('utf-8', errors='ignore').strip('\x00')
            else:
                return obj

        json_serializable_metadata = convert_numpy_types(metadata)

        # Write JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_serializable_metadata, f, ensure_ascii=False, indent=2)
