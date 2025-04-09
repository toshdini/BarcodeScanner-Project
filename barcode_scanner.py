import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests
import streamlit as st
from PIL import Image
import io
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BarcodeScanner:
    def __init__(self):
        self.last_scan_time = 0
        self.scan_interval = 2  # seconds between scans
        self.max_retries = 3
        self.retry_delay = 1  # seconds between retries
        self.min_barcode_size = 100  # minimum barcode size in pixels
        self.api_timeout = 5  # seconds

    def preprocess_image(self, image):
        """Enhanced image preprocessing for better barcode detection"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # Apply noise reduction
            denoised = cv2.fastNlMeansDenoising(thresh)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            return enhanced
        except Exception as e:
            logger.error(f"Error in image preprocessing: {str(e)}")
            return image

    def is_barcode_valid(self, barcode_data):
        """Validate barcode format and content"""
        if not barcode_data:
            return False
        # Add more validation rules as needed
        return True

    def scan_barcode(self, image):
        """Enhanced barcode detection with multiple attempts and validation"""
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Try multiple times with different preprocessing
            for attempt in range(self.max_retries):
                barcodes = decode(processed_image)
                
                if barcodes:
                    # Filter out small barcodes
                    valid_barcodes = [b for b in barcodes 
                                    if b.rect.width >= self.min_barcode_size 
                                    and b.rect.height >= self.min_barcode_size]
                    
                    if valid_barcodes:
                        barcode_data = valid_barcodes[0].data.decode('utf-8')
                        if self.is_barcode_valid(barcode_data):
                            return barcode_data
                
                # If no valid barcode found, try different preprocessing
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    processed_image = cv2.rotate(processed_image, cv2.ROTATE_90_CLOCKWISE)
            
            return None
        except Exception as e:
            logger.error(f"Error in barcode scanning: {str(e)}")
            return None

    def get_product_info(self, barcode):
        """Enhanced product information retrieval with retry mechanism"""
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.api_timeout)
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 1:
                        product = data['product']
                        return {
                            'company': product.get('brands', 'Unknown'),
                            'product_name': product.get('product_name', 'Unknown'),
                            'category': product.get('categories', 'Unknown'),
                            'image_url': product.get('image_url', None)
                        }
                elif response.status_code == 404:
                    return {'error': 'Product not found in database'}
            except requests.exceptions.Timeout:
                logger.warning(f"API request timed out (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error fetching product information: {str(e)}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        return {'error': 'Failed to retrieve product information'}

    def webcam_scan(self):
        """Enhanced webcam scanning with better performance and error handling"""
        st.write("Webcam is active. Hold a barcode in front of the camera.")
        
        frame_placeholder = st.empty()
        result_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise Exception("Could not open webcam")
            
            # Optimize webcam settings
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    raise Exception("Could not read from webcam")
                
                # Convert BGR to RGB and display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
                
                # Check scan interval
                current_time = time.time()
                if current_time - self.last_scan_time >= self.scan_interval:
                    status_placeholder.info("Scanning...")
                    barcode = self.scan_barcode(frame)
                    
                    if barcode:
                        self.last_scan_time = current_time
                        result_placeholder.success(f"Barcode detected: {barcode}")
                        product_info = self.get_product_info(barcode)
                        
                        if 'error' in product_info:
                            result_placeholder.error(product_info['error'])
                        else:
                            result_placeholder.write("Product Information:")
                            result_placeholder.write(f"Company: {product_info['company']}")
                            result_placeholder.write(f"Product Name: {product_info['product_name']}")
                            result_placeholder.write(f"Category: {product_info['category']}")
                            if product_info.get('image_url'):
                                result_placeholder.image(product_info['image_url'], 
                                                       caption="Product Image", 
                                                       use_column_width=True)
                            break
                    else:
                        status_placeholder.warning("No barcode detected. Try adjusting the angle or lighting.")
                
                if st.button("Stop Scanning"):
                    break
                    
        except Exception as e:
            st.error(f"Error in webcam scanning: {str(e)}")
        finally:
            if 'cap' in locals():
                cap.release()
            cv2.destroyAllWindows()

def main():
    st.title("Barcode Scanner App")
    st.write("Upload an image or use your webcam to scan a barcode")
    
    scanner = BarcodeScanner()
    
    mode = st.sidebar.radio("Select Input Mode:", ["Upload Image", "Webcam"])
    
    if mode == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image = np.array(image)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            if st.button("Scan Barcode"):
                with st.spinner("Scanning..."):
                    barcode = scanner.scan_barcode(image)
                    if barcode:
                        st.success(f"Barcode detected: {barcode}")
                        product_info = scanner.get_product_info(barcode)
                        
                        if 'error' in product_info:
                            st.error(product_info['error'])
                        else:
                            st.write("Product Information:")
                            st.write(f"Company: {product_info['company']}")
                            st.write(f"Product Name: {product_info['product_name']}")
                            st.write(f"Category: {product_info['category']}")
                            if product_info.get('image_url'):
                                st.image(product_info['image_url'], 
                                       caption="Product Image", 
                                       use_column_width=True)
                    else:
                        st.error("No barcode detected in the image")
    
    else:  # Webcam mode
        if st.button("Start Webcam"):
            scanner.webcam_scan()

if __name__ == "__main__":
    main() 