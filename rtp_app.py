#!/usr/bin/env python3
"""
Reduction to Pole (1D) - PySide6 Application
Magnetic data processing application with GUI interface.
"""
import os.path
import sys

import numpy as np
import pandas as pd
from PySide6.QtCore import (Qt, QThread, Signal)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDoubleSpinBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSlider, QTabWidget, QTableWidget, QTableWidgetItem,
    QWidget, QFileDialog, QMessageBox, QVBoxLayout, QProgressBar
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Import the RTP processing functions
from common import rtp_1d


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MplCanvas(FigureCanvas):
    """Matplotlib canvas widget for PySide6."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()


class RTPProcessor(QThread):
    """Background thread for RTP processing to prevent UI freezing."""
    
    finished = Signal(np.ndarray)
    error = Signal(str)
    progress = Signal(int)
    
    def __init__(self, distance, anomaly, dx, inc, dec, azimuth):
        super().__init__()
        self.distance = distance
        self.anomaly = anomaly
        self.dx = dx
        self.inc = inc
        self.dec = dec
        self.azimuth = azimuth
    
    def run(self):
        try:
            self.progress.emit(10)
            # Apply RTP transformation
            rtp_result = rtp_1d(self.distance, self.anomaly, self.dx, 
                               self.inc, self.dec, self.azimuth)
            self.progress.emit(90)
            
            # Apply amplitude flip as in original code
            reverse_anomaly = -rtp_result
            self.progress.emit(100)
            
            self.finished.emit(reverse_anomaly)
        except Exception as e:
            self.error.emit(str(e))


class RTPMainWindow(QWidget):
    """Main application window for RTP processing."""
    
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.setupConnections()
        self.setupDefaults()
        
        # Data storage
        self.csv_data = None
        self.processed_data = None
        self.current_file_path = None
        
        # Processing thread
        self.processor_thread = None
        
    def setupUI(self):
        """Initialize the user interface."""
        self.setWindowTitle("Reduction to pole (1-D)")
        self.setGeometry(100, 100, 888, 687)
        
        # Main layout
        self.gridLayout_2 = QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        
        # Title label
        self.label = QLabel(self)
        self.label.setObjectName("label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.label.setSizePolicy(sizePolicy)
        self.label.setFrameShape(QFrame.Shape.NoFrame)
        self.label.setFrameShadow(QFrame.Shadow.Plain)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setText("Reduction to pole (1-D)")
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        self.label.setFont(font)
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 4)
        
        # File loading section
        self.label_2 = QLabel("Load data:", self)
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setPlaceholderText("Select CSV file...")
        self.lineEdit.setReadOnly(True)
        self.gridLayout_2.addWidget(self.lineEdit, 1, 2, 1, 1)
        
        self.pushButton = QPushButton("Browse", self)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 1, 3, 1, 1)
        
        # Tab widget for data display
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        
        # Table tab
        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QGridLayout(self.tab)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        
        self.tableWidget = QTableWidget(self.tab)
        self.tableWidget.setObjectName("tableWidget")
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        
        self.tabWidget.addTab(self.tab, "Table")
        
        # Graph tab
        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_3 = QVBoxLayout(self.tab_2)
        
        # Create matplotlib canvas
        self.canvas = MplCanvas(self.tab_2, width=10, height=5, dpi=100)
        self.gridLayout_3.addWidget(self.canvas)
        
        self.tabWidget.addTab(self.tab_2, "Graph Preview")
        self.gridLayout_2.addWidget(self.tabWidget, 2, 0, 1, 4)
        
        # Column selection
        self.label_3 = QLabel("Distance Column", self)
        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)
        
        self.comboBox = QComboBox(self)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout_2.addWidget(self.comboBox, 3, 1, 1, 3)
        
        self.label_4 = QLabel("Anomaly Column", self)
        self.gridLayout_2.addWidget(self.label_4, 4, 0, 1, 1)
        
        self.comboBox_2 = QComboBox(self)
        self.comboBox_2.setObjectName("comboBox_2")
        self.gridLayout_2.addWidget(self.comboBox_2, 4, 1, 1, 3)
        
        # Parameters section
        self.label_5 = QLabel("Spacing (Meters)", self)
        self.gridLayout_2.addWidget(self.label_5, 5, 0, 1, 1)
        
        self.doubleSpinBox = QDoubleSpinBox(self)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.doubleSpinBox.setDecimals(2)
        self.doubleSpinBox.setMinimum(0.01)
        self.doubleSpinBox.setMaximum(1000.0)
        self.doubleSpinBox.setValue(10.0)
        self.gridLayout_2.addWidget(self.doubleSpinBox, 5, 1, 1, 3)
        
        # Inclination
        self.label_6 = QLabel("Field Inclination", self)
        self.gridLayout_2.addWidget(self.label_6, 6, 0, 1, 1)
        
        self.horizontalSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setMinimum(-90)
        self.horizontalSlider.setMaximum(90)
        self.horizontalSlider.setValue(42)
        self.gridLayout_2.addWidget(self.horizontalSlider, 6, 1, 1, 2)
        
        self.doubleSpinBox_2 = QDoubleSpinBox(self)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.doubleSpinBox_2.setDecimals(3)
        self.doubleSpinBox_2.setMinimum(-90.0)
        self.doubleSpinBox_2.setMaximum(90.0)
        self.doubleSpinBox_2.setValue(42.3)
        self.gridLayout_2.addWidget(self.doubleSpinBox_2, 6, 3, 1, 1)
        
        # Declination
        self.label_7 = QLabel("Field Declination", self)
        self.gridLayout_2.addWidget(self.label_7, 7, 0, 1, 1)
        
        self.horizontalSlider_2 = QSlider(Qt.Orientation.Horizontal, self)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.horizontalSlider_2.setMinimum(0)
        self.horizontalSlider_2.setMaximum(360)
        self.horizontalSlider_2.setValue(1)
        self.gridLayout_2.addWidget(self.horizontalSlider_2, 7, 1, 1, 2)
        
        self.doubleSpinBox_3 = QDoubleSpinBox(self)
        self.doubleSpinBox_3.setObjectName("doubleSpinBox_3")
        self.doubleSpinBox_3.setDecimals(4)
        self.doubleSpinBox_3.setMinimum(0.0)
        self.doubleSpinBox_3.setMaximum(360.0)
        self.doubleSpinBox_3.setValue(0.9719)
        self.gridLayout_2.addWidget(self.doubleSpinBox_3, 7, 3, 1, 1)
        
        # Azimuth
        self.label_8 = QLabel("Azimuth (Strike Angle)", self)
        self.gridLayout_2.addWidget(self.label_8, 8, 0, 1, 1)
        
        self.horizontalSlider_3 = QSlider(Qt.Orientation.Horizontal, self)
        self.horizontalSlider_3.setObjectName("horizontalSlider_3")
        self.horizontalSlider_3.setMinimum(0)
        self.horizontalSlider_3.setMaximum(360)
        self.horizontalSlider_3.setValue(90)
        self.gridLayout_2.addWidget(self.horizontalSlider_3, 8, 1, 1, 2)
        
        self.doubleSpinBox_4 = QDoubleSpinBox(self)
        self.doubleSpinBox_4.setObjectName("doubleSpinBox_4")
        self.doubleSpinBox_4.setDecimals(1)
        self.doubleSpinBox_4.setMinimum(0.0)
        self.doubleSpinBox_4.setMaximum(360.0)
        self.doubleSpinBox_4.setValue(90.0)
        self.gridLayout_2.addWidget(self.doubleSpinBox_4, 8, 3, 1, 1)
        
        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setVisible(False)
        self.gridLayout_2.addWidget(self.progressBar, 9, 0, 1, 2)
        
        # Action buttons
        self.horizontalLayout = QHBoxLayout()
        
        self.pushButton_3 = QPushButton("Compute", self)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        
        self.pushButton_2 = QPushButton("Export Results", self)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setEnabled(False)
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.gridLayout_2.addLayout(self.horizontalLayout, 9, 2, 1, 2)
        stylesheet_path = get_resource_path("light_theme.qss")
        with open(stylesheet_path) as f:
            self.setStyleSheet(f.read())
        
    def setupConnections(self):
        """Connect signals and slots."""
        # File operations
        self.pushButton.clicked.connect(self.browse_file)
        
        # Processing
        self.pushButton_3.clicked.connect(self.compute_rtp)
        self.pushButton_2.clicked.connect(self.export_results)
        
        # Parameter synchronization
        self.horizontalSlider.valueChanged.connect(
            lambda v: self.doubleSpinBox_2.setValue(v))
        self.doubleSpinBox_2.valueChanged.connect(
            lambda v: self.horizontalSlider.setValue(int(v)))
        
        self.horizontalSlider_2.valueChanged.connect(
            lambda v: self.doubleSpinBox_3.setValue(v))
        self.doubleSpinBox_3.valueChanged.connect(
            lambda v: self.horizontalSlider_2.setValue(int(v)))
        
        self.horizontalSlider_3.valueChanged.connect(
            lambda v: self.doubleSpinBox_4.setValue(v))
        self.doubleSpinBox_4.valueChanged.connect(
            lambda v: self.horizontalSlider_3.setValue(int(v)))
        
        # Column selection
        self.comboBox.currentTextChanged.connect(self.update_preview)
        self.comboBox_2.currentTextChanged.connect(self.update_preview)
        
    def setupDefaults(self):
        """Set default values."""
        self.tabWidget.setCurrentIndex(0)
        
    def browse_file(self):
        """Open file dialog to select CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv)")
        
        if file_path:
            try:
                self.csv_data = pd.read_csv(file_path)
                self.current_file_path = file_path
                self.lineEdit.setText(file_path)
                
                # Populate column dropdowns
                columns = list(self.csv_data.columns)
                self.comboBox.clear()
                self.comboBox_2.clear()
                self.comboBox.addItems(columns)
                self.comboBox_2.addItems(columns)
                
                # Auto-select common column names
                for i, col in enumerate(columns):
                    if 'distance' in col.lower() or 'x' in col.lower():
                        self.comboBox.setCurrentIndex(i)
                    elif 'anomaly' in col.lower() or 'y' in col.lower():
                        self.comboBox_2.setCurrentIndex(i)
                
                # Update table display
                self.update_table()
                
                QMessageBox.information(self, "Success", 
                                      f"Loaded {len(self.csv_data)} data points")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
    
    def update_table(self):
        """Update the data table widget."""
        if self.csv_data is None:
            return
        
        df = self.csv_data.copy()
        if self.processed_data is not None:
            df['RTP_Processed'] = self.processed_data
        
        self.tableWidget.setRowCount(len(df))
        self.tableWidget.setColumnCount(len(df.columns))
        self.tableWidget.setHorizontalHeaderLabels(df.columns.tolist())
        
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                value = df.iloc[i, j]
                if isinstance(value, (int, float)):
                    item = QTableWidgetItem(f"{value:.4f}")
                else:
                    item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(i, j, item)
        
        self.tableWidget.resizeColumnsToContents()
    
    def update_preview(self):
        """Update the graph preview."""
        if self.csv_data is None:
            return
        
        distance_col = self.comboBox.currentText()
        anomaly_col = self.comboBox_2.currentText()
        
        if not distance_col or not anomaly_col or distance_col == anomaly_col:
            return
        
        try:
            distance = self.csv_data[distance_col].values
            anomaly = self.csv_data[anomaly_col].values
            
            self.canvas.fig.clear()
            ax = self.canvas.fig.add_subplot(111)
            
            ax.plot(distance, anomaly, 'b-', label='Original Data', linewidth=1.5)
            
            if self.processed_data is not None:
                ax.plot(distance, self.processed_data, 'r--', 
                       label='RTP Processed', linewidth=1.5)
            
            ax.set_xlabel('Distance (m)')
            ax.set_ylabel('Anomaly (nT)')
            ax.set_title('Magnetic Anomaly Data')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            self.canvas.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Preview update error: {e}")
    
    def compute_rtp(self):
        """Start RTP computation in background thread."""
        if self.csv_data is None:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        distance_col = self.comboBox.currentText()
        anomaly_col = self.comboBox_2.currentText()
        
        if not distance_col or not anomaly_col:
            QMessageBox.warning(self, "Warning", "Please select distance and anomaly columns")
            return
        
        if distance_col == anomaly_col:
            QMessageBox.warning(self, "Warning", "Distance and anomaly columns must be different")
            return
        
        try:
            distance = self.csv_data[distance_col].values
            anomaly = self.csv_data[anomaly_col].values
            
            # Get parameters
            dx = self.doubleSpinBox.value()
            inc = self.doubleSpinBox_2.value()
            dec = self.doubleSpinBox_3.value()
            azimuth = self.doubleSpinBox_4.value()
            
            # Start processing thread
            self.processor_thread = RTPProcessor(distance, anomaly, dx, inc, dec, azimuth)
            self.processor_thread.finished.connect(self.on_processing_finished)
            self.processor_thread.error.connect(self.on_processing_error)
            self.processor_thread.progress.connect(self.progressBar.setValue)
            
            # Show progress bar and disable compute button
            self.progressBar.setVisible(True)
            self.progressBar.setValue(0)
            self.pushButton_3.setEnabled(False)
            
            self.processor_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Processing failed: {str(e)}")
    
    def on_processing_finished(self, result):
        """Handle successful RTP processing."""
        self.processed_data = result
        self.progressBar.setVisible(False)
        self.pushButton_3.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        
        # Update displays
        self.update_table()
        self.update_preview()
        
        QMessageBox.information(self, "Success", "RTP processing completed successfully!")
    
    def on_processing_error(self, error_msg):
        """Handle processing errors."""
        self.progressBar.setVisible(False)
        self.pushButton_3.setEnabled(True)
        QMessageBox.critical(self, "Processing Error", f"RTP processing failed: {error_msg}")
    
    def export_results(self):
        """Export processed results to CSV file."""
        if self.processed_data is None:
            QMessageBox.warning(self, "Warning", "No processed data to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "profile_rtp.csv", "CSV Files (*.csv)")
        
        if file_path:
            try:
                # Create export dataframe
                export_df = self.csv_data.copy()
                export_df['RTP_Processed'] = self.processed_data
                
                export_df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Success", 
                                      f"Results exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("RTP Processor")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Magnetic Processing Tools")
    
    # Apply modern styling
    # app.setStyle('Fusion')
    
    # Create and show main window
    window = RTPMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()