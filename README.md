# Barcode Scanner App

A Python application that detects barcodes from images or live camera feed, extracts the barcode number, and retrieves information about the product's parent company using the Open Food Facts API.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Implementation Details](#implementation-details)
- [Testing](#testing)
- [Future Enhancements](#future-enhancements)
- [Contributors](#contributors)
- [License](#license)

## Features

- **Barcode Detection**
  - Support for static images and live webcam feed
  - Multiple barcode format support
  - Enhanced image preprocessing for better detection
  - Automatic rotation handling

- **Product Information**
  - Company/Brand name retrieval
  - Product name and category information
  - Product image display
  - Real-time API integration

- **User Interface**
  - Streamlit-based modern interface
  - Real-time feedback and status updates
  - Easy mode switching between image upload and webcam
  - Loading indicators and error messages

## Requirements

- Python 3.8 or higher
- OpenCV 4.8.1
- pyzbar 0.1.9
- Streamlit 1.31.1
- Other dependencies listed in requirements.txt

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd BarcodeScanner-Project
```

2. Create a virtual environment (recommended):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
streamlit run barcode_scanner.py
```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Choose your preferred scanning mode:
   - **Upload Image**: Select an image file containing a barcode
   - **Webcam**: Use your computer's camera to scan barcodes in real-time

4. For best results:
   - Ensure good lighting conditions
   - Hold the barcode steady
   - Keep the barcode within the frame
   - Avoid glare or reflections

## Project Structure

```
BarcodeScanner-Project/
├── barcode_scanner.py    # Main application file
├── requirements.txt      # Project dependencies
└── README.md            # Project documentation
```

## Implementation Details

### Image Processing
- Grayscale conversion
- Adaptive thresholding
- Noise reduction
- Contrast enhancement
- Multiple preprocessing attempts

### Barcode Detection
- pyzbar integration
- Size validation
- Format validation
- Rotation handling
- Multiple scanning attempts

### API Integration
- Open Food Facts API
- Retry mechanism
- Timeout handling
- Error management
- Product information parsing

### User Interface
- Streamlit framework
- Real-time feedback
- Status indicators
- Error messages
- Loading spinners

## Testing

The application includes:
- Error handling for various scenarios
- Input validation
- API response validation
- Webcam access verification
- Image processing validation

## Future Enhancements

- [ ] Support for additional barcode formats
- [ ] Offline barcode database
- [ ] Batch processing of multiple images
- [ ] Mobile app version
- [ ] Additional product information sources
- [ ] Enhanced image preprocessing
- [ ] Machine learning-based barcode detection
- [ ] Multi-language support

## Contributors

- Joshua Dinham
- Rahman Mohamed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## External Resources

1. **OpenCV Documentation**
   - [https://docs.opencv.org](https://docs.opencv.org)
   - Provides in-depth knowledge on image processing and barcode detection

2. **pyzbar Library**
   - [https://github.com/NaturalHistoryMuseum/pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar)
   - Official documentation for barcode decoding

3. **Open Food Facts API**
   - [https://world.openfoodfacts.org/data](https://world.openfoodfacts.org/data)
   - Free and open-source database for product information

---

## 2. Project Overview  
This project aims to develop a barcode scanning application that can detect barcodes from an image or live camera feed, extract the barcode number, and query an online database to retrieve information about the parent company of the product.

The application will provide real-time feedback on whether a barcode has been successfully scanned and display relevant product/company details.

---

## 3. Objectives

- Detect and decode barcodes from images or a live webcam feed.  
- Retrieve product information (e.g., manufacturer, brand, category) using an API.  
- Display the results in an intuitive interface.  
- Handle low-light or blurry barcodes with preprocessing techniques.

---

## 4. Tools & Technologies

| Component             | Technology                                 |
|-----------------------|--------------------------------------------|
| Barcode Detection     | OpenCV, pyzbar (ZBar)                      |
| API for Data Retrieval| Open Food Facts, Barcode Lookup API        |
| User Interface (UI)   | Tkinter (GUI), Flask (web), or Streamlit   |
| Programming Language  | Python                                     |
| Image Processing      | OpenCV (grayscale, thresholding)           |

---

## 5. Timeline

| Week | Task                                             | Assigned To |
|------|--------------------------------------------------|-------------|
| 1    | Research barcode scanning techniques, set up OpenCV and pyzbar | Joshua      |
| 2    | Implement barcode detection in static images     | Rahman      |
| 3    | Implement barcode detection in real-time from a webcam | Joshua  |
| 4    | Integrate an API for product lookup              | Rahman      |
| 5    | Develop the UI for displaying product details    | Joshua      |
| 6    | Optimize performance and handle edge cases       | Rahman      |
| 7    | Testing and final refinements                    | Joshua      |
| 8    | Prepare documentation and presentation           | Rahman      |

---

## 6. External Resources

To successfully complete this project, the following resources will be utilized:

1. **OpenCV Documentation** – Provides in-depth knowledge on image processing and barcode detection using OpenCV.  
   [https://docs.opencv.org](https://docs.opencv.org)

2. **pyzbar Library** – Official documentation for decoding barcodes using Python's pyzbar library.  
   [https://github.com/NaturalHistoryMuseum/pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar)

3. **Open Food Facts API** – A free and open-source database for retrieving product and company information based on barcode numbers.  
   [https://world.openfoodfacts.org/data](https://world.openfoodfacts.org/data)
