# Project Proposal: Barcode Scanner App

**Course:** Computer Vision  
**Student Name:** Joshua Dinham, Rahman Mohamed  
**Date:** 2025-03-03  

---

## 1. Project Title  
**Barcode Scanner App for Identifying Product Parent Companies**

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

2. **pyzbar Library** – Official documentation for decoding barcodes using Python’s pyzbar library.  
   [https://github.com/NaturalHistoryMuseum/pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar)

3. **Open Food Facts API** – A free and open-source database for retrieving product and company information based on barcode numbers.  
   [https://world.openfoodfacts.org/data](https://world.openfoodfacts.org/data)
