import os
import sys
from pathlib import Path

import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# 抑制 macOS 上的 Qt layer-backing 警告
if sys.platform == 'darwin':
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
    import warnings

    warnings.filterwarnings("ignore", message="Layer-backing is always enabled")

from ._nifti_loader import NiftiLoader


class NiftiViewerWidget(QWidget):
    """Main interface for NIfTI file viewer"""

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.nifti_loader = NiftiLoader()
        self.current_data = None
        self.current_metadata = None

        # 设置界面
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout()

        # File loading area
        load_group = QGroupBox("File Loading")
        load_layout = QVBoxLayout()

        # File selection
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_path.setPlaceholderText("Select a .nii or .nii.gz file...")

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.load_file)

        load_btn = QPushButton("Load to Napari")
        load_btn.clicked.connect(self.load_to_napari)
        load_btn.setEnabled(False)
        self.load_btn = load_btn

        file_layout.addWidget(QLabel("File:"))
        file_layout.addWidget(self.file_path, 1)
        file_layout.addWidget(browse_btn)
        file_layout.addWidget(load_btn)

        load_layout.addLayout(file_layout)
        load_group.setLayout(load_layout)
        layout.addWidget(load_group)

        # Create tabbed interface
        self.tabs = QTabWidget()

        # File overview tab (merge basic info + data statistics)
        self.setup_overview_tab()

        # Detailed info tab (merge header info + metadata)
        self.setup_detailed_info_tab()

        # Label analysis tab
        self.setup_labels_tab()

        layout.addWidget(self.tabs)

        # 导出按钮
        export_layout = QHBoxLayout()
        export_btn = QPushButton("Export Metadata as JSON")
        export_btn.clicked.connect(self.export_metadata)
        export_btn.setEnabled(False)
        self.export_btn = export_btn

        export_layout.addStretch()
        export_layout.addWidget(export_btn)
        layout.addLayout(export_layout)

        self.setLayout(layout)

    def setup_overview_tab(self):
        """Set up file overview tab (merge basic info and data statistics)"""
        overview_tab = QWidget()
        layout = QVBoxLayout()

        # Basic file information
        file_group = QGroupBox("File Information")
        file_layout = QVBoxLayout()

        self.file_info_text = QTextEdit()
        self.file_info_text.setReadOnly(True)
        self.file_info_text.setMaximumHeight(120)
        file_layout.addWidget(self.file_info_text)
        file_group.setLayout(file_layout)

        # Data statistics information (using table)
        stats_group = QGroupBox("Data Statistics")
        stats_layout = QVBoxLayout()

        self.overview_stats_table = QTableWidget()
        self.overview_stats_table.setColumnCount(2)
        self.overview_stats_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.overview_stats_table.horizontalHeader().setStretchLastSection(True)
        self.overview_stats_table.verticalHeader().setVisible(False)  # Hide row numbers
        self.overview_stats_table.setMaximumHeight(200)

        stats_layout.addWidget(self.overview_stats_table)
        stats_group.setLayout(stats_layout)

        # Coordinate system and affine transformation
        transform_group = QGroupBox("Coordinate System & Transform")
        transform_layout = QVBoxLayout()

        self.transform_text = QTextEdit()
        self.transform_text.setReadOnly(True)
        self.transform_text.setMaximumHeight(150)
        transform_layout.addWidget(self.transform_text)
        transform_group.setLayout(transform_layout)

        layout.addWidget(file_group)
        layout.addWidget(stats_group)
        layout.addWidget(transform_group)
        layout.addStretch()

        overview_tab.setLayout(layout)
        self.tabs.addTab(overview_tab, "File Overview")

    def setup_detailed_info_tab(self):
        """Set up detailed info tab (merge NIfTI header info and complete metadata)"""
        detailed_tab = QWidget()
        layout = QVBoxLayout()

        # 创建水平分割器
        splitter = QSplitter(Qt.Horizontal)

        # Left side: NIfTI header fields
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("NIfTI Header Fields"))

        self.header_tree = QTreeWidget()
        self.header_tree.setHeaderLabels(["Field", "Value", "Description"])
        self.header_tree.setAlternatingRowColors(
            False
        )  # Turn off alternating row colors
        self.header_tree.setRootIsDecorated(False)  # Don't show root node decoration

        # Set better styling
        self.header_tree.setStyleSheet(
            """
            QTreeWidget {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
                selection-background-color: #404040;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #404040;
            }
            QTreeWidget::item:selected {
                background-color: #404040;
            }
            QHeaderView::section {
                background-color: #3c3c3c;
                color: white;
                padding: 6px;
                border: 1px solid #555;
                font-weight: bold;
            }
        """
        )
        left_layout.addWidget(self.header_tree)
        left_widget.setLayout(left_layout)

        # Right side: Complete metadata JSON
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Complete Metadata (JSON Format)"))

        self.raw_metadata_text = QTextEdit()
        self.raw_metadata_text.setReadOnly(True)
        self.raw_metadata_text.setFont(self.raw_metadata_text.font())  # 使用等宽字体
        right_layout.addWidget(self.raw_metadata_text)
        right_widget.setLayout(right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([1, 1])  # 平分空间

        layout.addWidget(splitter)
        detailed_tab.setLayout(layout)
        self.tabs.addTab(detailed_tab, "Detailed Info")

    def setup_labels_tab(self):
        """Set up label information tab"""
        labels_tab = QWidget()
        layout = QVBoxLayout()

        # Label detection results
        detection_group = QGroupBox("Label Detection")
        detection_layout = QVBoxLayout()

        self.label_detection_text = QTextEdit()
        self.label_detection_text.setReadOnly(True)
        self.label_detection_text.setMaximumHeight(100)
        detection_layout.addWidget(self.label_detection_text)
        detection_group.setLayout(detection_layout)

        # Label statistics table
        label_stats_group = QGroupBox("Label Statistics")
        label_stats_layout = QVBoxLayout()

        self.label_stats_table = QTableWidget()
        self.label_stats_table.setColumnCount(3)
        self.label_stats_table.setHorizontalHeaderLabels(
            ["Label Value", "Voxel Count", "Percentage (%)"]
        )
        self.label_stats_table.horizontalHeader().setStretchLastSection(True)
        self.label_stats_table.verticalHeader().setVisible(False)  # Hide row numbers

        label_stats_layout.addWidget(self.label_stats_table)
        label_stats_group.setLayout(label_stats_layout)

        layout.addWidget(detection_group)
        layout.addWidget(label_stats_group)
        layout.addStretch()

        labels_tab.setLayout(layout)
        self.tabs.addTab(labels_tab, "Label Analysis")

    def load_file(self):
        """Load NIfTI file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select NIfTI File",
            "",
            "NIfTI Files (*.nii *.nii.gz);;All Files (*.*)",
        )

        if file_path:
            try:
                # 加载文件和元数据
                data, metadata = self.nifti_loader.load_file(file_path)
                self.current_data = data
                self.current_metadata = metadata

                # 更新界面
                self.file_path.setText(file_path)
                self.update_all_displays()

                # 启用按钮
                self.load_btn.setEnabled(True)
                self.export_btn.setEnabled(True)

                QMessageBox.information(self, "Success", "File loaded successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading file: {str(e)}")

    def load_to_napari(self):
        """Load data into Napari viewer"""
        if self.current_data is not None:
            try:
                # 根据数据特征选择合适的显示方式
                file_name = Path(self.file_path.text()).name

                # 检查是否可能是标签图像
                is_labels = (
                    self.current_metadata.get('labels', {}).get(
                        'is_likely_labels', False
                    )
                    if self.current_metadata
                    else False
                )

                if is_labels:
                    # Add as label layer
                    self.viewer.add_labels(
                        self.current_data.astype(np.int32), name=f"Labels: {file_name}"
                    )
                else:
                    # Add as image layer
                    self.viewer.add_image(self.current_data, name=f"Image: {file_name}")

                QMessageBox.information(self, "Success", "Data added to Napari viewer!")

            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error adding data to Napari: {str(e)}"
                )

    def update_all_displays(self):
        """更新所有显示内容"""
        if self.current_metadata is None:
            return

        self.update_overview()
        self.update_detailed_info()
        self.update_labels_info()

    def update_overview(self):
        """更新文件概览显示"""
        metadata = self.current_metadata

        # File information
        if 'file_info' in metadata:
            file_info = metadata['file_info']
            file_text = f"""Filename: {file_info.get('file_name', 'Unknown')}
File Size: {file_info.get('file_size', 0) / 1024 / 1024:.2f} MB
Format: {file_info.get('format', 'Unknown')} (Version: {file_info.get('version', 'Unknown')})"""
            self.file_info_text.setText(file_text)

        # Data statistics table
        if 'data_info' in metadata:
            data_info = metadata['data_info']

            stats_items = [
                ('Data Shape', str(data_info.get('shape', []))),
                ('Data Type', str(data_info.get('dtype', 'Unknown'))),
                ('Min Value', f"{data_info.get('min_value', 0):.6f}"),
                ('Max Value', f"{data_info.get('max_value', 0):.6f}"),
                ('Mean Value', f"{data_info.get('mean_value', 0):.6f}"),
                ('Std Deviation', f"{data_info.get('std_value', 0):.6f}"),
                ('Unique Values', str(data_info.get('unique_values_count', 0))),
                ('Non-zero Voxels', str(data_info.get('non_zero_count', 0))),
            ]

            self.overview_stats_table.setRowCount(len(stats_items))
            for i, (name, value) in enumerate(stats_items):
                self.overview_stats_table.setItem(i, 0, QTableWidgetItem(name))
                self.overview_stats_table.setItem(i, 1, QTableWidgetItem(value))

        # 坐标系统和仿射变换
        transform_parts = []

        if 'coordinate_system' in metadata:
            coord_info = metadata['coordinate_system']
            transform_parts.append(
                f"Voxel Size: {coord_info.get('voxel_size', [])} {coord_info.get('spatial_unit', '')}"
            )
            transform_parts.append(
                f"Transform Codes: QForm={coord_info.get('qform_code', 0)}, SForm={coord_info.get('sform_code', 0)}"
            )

        if 'affine' in metadata:
            affine_info = metadata['affine']
            affine_matrix = np.array(affine_info['affine_matrix'])
            transform_parts.append(f"\nAffine Transform Matrix:\n{affine_matrix}")
            transform_parts.append(
                f"Translation Vector: {affine_info.get('translation', [])}"
            )
            transform_parts.append(
                f"Determinant: {affine_info.get('determinant', 0):.6f}"
            )

        self.transform_text.setText('\n'.join(transform_parts))

    def update_detailed_info(self):
        """更新详细信息显示"""
        # 更新头部信息树
        self.header_tree.clear()

        if 'header' in self.current_metadata:
            header_info = self.current_metadata['header']
            explanations = header_info.get('explanations', {})

            for key, value in header_info.items():
                if key == 'explanations':
                    continue

                item = QTreeWidgetItem(self.header_tree)
                item.setText(0, key)
                item.setText(1, str(value))
                item.setText(2, explanations.get(key, ''))

            # 调整列宽
            self.header_tree.resizeColumnToContents(0)
            self.header_tree.resizeColumnToContents(1)

        # Update complete metadata JSON
        try:
            # Use the same type conversion logic as export
            def convert_numpy_types(obj):
                if isinstance(obj, dict):
                    return {
                        key: convert_numpy_types(value) for key, value in obj.items()
                    }
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

            json_serializable_metadata = convert_numpy_types(self.current_metadata)

            import json

            json_text = json.dumps(
                json_serializable_metadata, ensure_ascii=False, indent=2
            )
            self.raw_metadata_text.setText(json_text)
        except Exception as e:
            self.raw_metadata_text.setText(f"JSON serialization failed: {str(e)}")

    def update_labels_info(self):
        """Update label information display"""
        if 'labels' not in self.current_metadata:
            return

        labels_info = self.current_metadata['labels']

        # Label detection results
        is_labels = labels_info.get('is_likely_labels', False)
        label_count = labels_info.get('label_count', 0)

        detection_text = f"""Label Image Detection: {'Yes' if is_labels else 'No'}
Label Count: {label_count}
All Unique Values: {labels_info.get('unique_values', [])}"""
        self.label_detection_text.setText(detection_text)

        # Label statistics table
        if 'label_statistics' in labels_info:
            stats = labels_info['label_statistics']

            self.label_stats_table.setRowCount(len(stats))
            for i, (label_val, label_stats) in enumerate(stats.items()):
                self.label_stats_table.setItem(i, 0, QTableWidgetItem(label_val))
                self.label_stats_table.setItem(
                    i, 1, QTableWidgetItem(str(label_stats['voxel_count']))
                )
                self.label_stats_table.setItem(
                    i, 2, QTableWidgetItem(f"{label_stats['percentage']:.2f}")
                )
        else:
            self.label_stats_table.setRowCount(0)

    def export_metadata(self):
        """Export metadata to JSON file"""
        if self.current_metadata is None:
            QMessageBox.warning(self, "Warning", "No metadata to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Metadata",
            f"{Path(self.file_path.text()).stem}_metadata.json",
            "JSON Files (*.json);;All Files (*.*)",
        )

        if file_path:
            try:
                self.nifti_loader.export_metadata_to_json(
                    self.current_metadata, file_path
                )
                QMessageBox.information(
                    self, "Success", f"Metadata saved to: {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving metadata: {str(e)}")
