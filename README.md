# Reduction to Pole (1D) - PySide6 Application

A professional desktop application for magnetic data processing using 1D Reduction to Pole (RTP) transformation. Built with PySide6 for a modern, cross-platform GUI experience.

## Features

- **Modern GUI Interface**: Clean, professional interface built with PySide6
- **CSV Data Loading**: Easy file loading with automatic column detection
- **Interactive Parameters**: Real-time parameter adjustment with sliders and inputs
- **Live Preview**: Tabular and graphical visualization of data
- **Background Processing**: Non-blocking RTP computation with progress indication
- **Data Export**: Save processed results to CSV format
- **Professional Visualization**: Matplotlib integration for high-quality plots

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone or Download Files

Make sure you have all the required files in the same directory:
- `rtp_app.py` (main application)
- `common.py` (RTP processing functions)
- `requirements.txt` (dependencies)
- `sample_profile.csv` (test data)

### Step 2: Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install PySide6 matplotlib numpy pandas
```

### Step 3: Run the Application

```bash
python rtp_app.py
```

## Usage

### 1. Loading Data

1. Click **Browse** to select a CSV file containing your magnetic data
2. The file should have at least two columns: distance and anomaly values
3. After loading, select appropriate columns from the dropdowns:
   - **Distance Column**: Contains spatial distance measurements (meters)
   - **Anomaly Column**: Contains magnetic anomaly values (nanoTesla)

### 2. Setting Parameters

Adjust the processing parameters using sliders or direct input:

- **Spacing (Meters)**: Data sampling interval (default: 10.0 m)
- **Field Inclination**: Earth's magnetic field inclination in degrees (default: 42.3°)
- **Field Declination**: Earth's magnetic field declination in degrees (default: 0.9719°)  
- **Azimuth (Strike Angle)**: Profile azimuth from North to East (default: 90.0°)

### 3. Data Visualization

Switch between two tabs:
- **Table**: View raw data and processed results in tabular format
- **Graph Preview**: Interactive plot showing original and RTP-transformed data

### 4. Processing Data

1. Click **Compute** to start RTP transformation
2. Progress bar shows processing status
3. Results appear automatically in both table and graph views

### 5. Exporting Results

1. After successful processing, click **Export Results**
2. Choose location and filename for the output CSV file
3. The exported file includes original data plus RTP-processed column

## Algorithm Details

The application implements 1D Reduction to Pole (RTP) transformation:

1. **Detrending**: Removes linear trend from input data
2. **Tapering**: Applies Tukey window (α=0.1) to reduce edge effects
3. **FFT Processing**: Forward FFT with zero-padding to next power of 2
4. **RTP Operator**: Applies frequency-domain RTP filter
5. **Inverse FFT**: Returns to spatial domain
6. **Amplitude Correction**: Applies amplitude flip as per original implementation

### RTP Formula

The RTP operator is defined as:

```
RTP_operator = Fz / (Fx*cos(θ) + Fy*sin(θ) + i*Fz*sign(k))
```

Where:
- Fx, Fy, Fz: Components of Earth's magnetic field vector
- θ: Profile azimuth angle
- k: Wavenumber
- i: Imaginary unit

## File Structure

```
project/
├── rtp_app.py           # Main PySide6 application
├── common.py            # RTP processing algorithms
├── requirements.txt     # Python dependencies
├── sample_profile.csv   # Sample test data
└── README.md           # This file
```

## Sample Data

The included `sample_profile.csv` contains synthetic magnetic anomaly data for testing:
- 41 data points
- Distance range: 0-400 meters
- Typical magnetic anomaly values in nanoTesla

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure all dependencies are installed
   ```bash
   pip install --upgrade PySide6 matplotlib numpy pandas
   ```

2. **Qt Platform Plugin Error**: Install additional Qt dependencies
   ```bash
   pip install PySide6[all]
   ```

3. **File Loading Issues**: Ensure CSV file has proper format with headers

4. **Processing Errors**: Check that:
   - Distance and anomaly columns contain numeric data
   - No missing values in selected columns
   - Data has sufficient length (minimum 3-4 points)

### System-Specific Notes

**Windows**: Application should run directly with Python installed

**macOS**: May require additional Qt dependencies:
```bash
brew install qt6
```

**Linux**: Install Qt development libraries:
```bash
sudo apt-get install qt6-base-dev  # Ubuntu/Debian
sudo yum install qt6-qtbase-devel  # RHEL/CentOS
```

## Development

### Extending the Application

The application is modular and can be extended:

1. **Additional Algorithms**: Add new processing functions to `common.py`
2. **UI Enhancements**: Modify widgets in `setupUI()` method
3. **Export Formats**: Add new export options in `export_results()`
4. **Visualization**: Enhance plotting in `update_preview()`

### Code Structure

- `RTPMainWindow`: Main application window class
- `RTPProcessor`: Background processing thread
- `MplCanvas`: Matplotlib integration widget
- Processing functions imported from `common.py`

## License

This application is provided for educational and research purposes. Ensure proper attribution when using or modifying the code.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are correctly installed
3. Test with the provided sample data first