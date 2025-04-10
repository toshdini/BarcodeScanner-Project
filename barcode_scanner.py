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
        """Enhanced image preprocessing specifically for barcode detection"""
        try:
            # Ensure image is in BGR format
            if len(image.shape) == 2:  # If grayscale
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Increase contrast
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # Apply bilateral filter to reduce noise while preserving edges
            denoised = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(denoised, 255, 
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 15, 2)
            
            # Morphological operations to clean up the image
            kernel = np.ones((3,3), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return processed
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
        """Enhanced barcode detection optimized for EAN-13"""
        try:
            # Scale the image if it's too small
            min_width = 640
            if image.shape[1] < min_width:
                scale = min_width / image.shape[1]
                image = cv2.resize(image, None, fx=scale, fy=scale)

            # Try multiple preprocessing techniques
            for attempt in range(self.max_retries):
                if attempt == 0:
                    processed_image = self.preprocess_image(image)
                elif attempt == 1:
                    # Try with Otsu's thresholding
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    _, processed_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                else:
                    # Try with different blur and threshold
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                    processed_image = cv2.adaptiveThreshold(blurred, 255,
                                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                         cv2.THRESH_BINARY, 11, 2)

                # Try different rotations
                for angle in [0, 90, 180, 270]:
                    rotated = processed_image
                    if angle > 0:
                        rotated = cv2.rotate(processed_image,
                                           cv2.ROTATE_90_CLOCKWISE if angle == 90 else
                                           cv2.ROTATE_180 if angle == 180 else
                                           cv2.ROTATE_90_COUNTERCLOCKWISE)

                    # Try to decode barcodes with different options
                    barcodes = decode(rotated)
                    if not barcodes:
                        # Try inverting the image
                        barcodes = decode(cv2.bitwise_not(rotated))

                    if barcodes:
                        for barcode in barcodes:
                            # Check if it's a valid EAN-13 barcode
                            barcode_data = barcode.data.decode('utf-8')
                            if len(barcode_data) == 13 and barcode_data.isdigit():
                                logger.info(f"Found valid EAN-13 barcode: {barcode_data}")
                                return barcode_data

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

            logger.warning("No valid barcode found after all attempts")
            return None

        except Exception as e:
            logger.error(f"Error in barcode scanning: {str(e)}")
            return None

    def get_product_info(self, barcode, barcode_type=None):
        """Enhanced product information retrieval with format-specific handling and improved error handling"""
        try:
            logger.info(f"Starting product info retrieval for barcode: {barcode}")
            
            # Validate barcode input
            if not barcode or not isinstance(barcode, str):
                logger.error(f"Invalid barcode input: {barcode}")
                return {
                    'error': 'Invalid barcode format',
                    'details': 'Barcode must be a non-empty string',
                    'barcode': barcode
                }
            
            # Format-specific API endpoints and handling
            api_handlers = {
                'EAN13': self._handle_ean13,
                'UPC_A': self._handle_upc_a,
                'CODE128': self._handle_code128,
                'QRCODE': self._handle_qrcode,
                'CODE39': self._handle_code39
            }
            
            # If barcode_type is not provided, try to determine it
            if not barcode_type:
                logger.debug("Barcode type not provided, attempting to determine type")
                barcode_type = self._determine_barcode_type(barcode)
                logger.info(f"Determined barcode type: {barcode_type}")
            
            # Validate barcode type
            if barcode_type not in api_handlers:
                logger.warning(f"Unsupported barcode type: {barcode_type}")
                return {
                    'error': 'Unsupported barcode type',
                    'details': f'Barcode type {barcode_type} is not supported',
                    'supported_types': list(api_handlers.keys()),
                    'barcode': barcode
                }
            
            # Get the appropriate handler
            handler = api_handlers.get(barcode_type, self._handle_unknown)
            logger.debug(f"Using handler: {handler.__name__}")
            
            result = handler(barcode)
            logger.info(f"Successfully retrieved product info for {barcode_type} barcode: {barcode}")
            return result
            
        except Exception as e:
            error_details = {
                'error': str(e),
                'type': type(e).__name__,
                'barcode': barcode,
                'barcode_type': barcode_type,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            logger.error(f"Error in product info retrieval: {error_details}")
            return {
                'error': 'Failed to retrieve product information',
                'details': error_details
            }

    def _determine_barcode_type(self, barcode):
        """Determine barcode type based on format and length"""
        if len(barcode) == 13 and barcode.isdigit():
            return 'EAN13'
        elif len(barcode) == 12 and barcode.isdigit():
            return 'UPC_A'
        elif len(barcode) > 0 and all(c in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. $/+%' for c in barcode):
            return 'CODE39'
        elif len(barcode) > 0:  # Default to CODE128 for other cases
            return 'CODE128'
        return 'UNKNOWN'

    def _handle_ean13(self, barcode):
        """Handle EAN-13 barcodes with Open Food Facts API"""
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        return self._make_api_request(url, 'EAN-13')

    def _handle_upc_a(self, barcode):
        """Handle UPC-A barcodes by converting to EAN-13"""
        # Convert UPC-A to EAN-13 by adding '0' prefix
        ean13_barcode = '0' + barcode
        return self._handle_ean13(ean13_barcode)

    def _handle_code128(self, barcode):
        """Handle CODE128 barcodes with enhanced error handling and logging"""
        logger.info(f"Processing CODE128 barcode: {barcode}")
        
        endpoints = [
            {
                'url': f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json",
                'name': 'Open Food Facts'
            },
            {
                'url': f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}",
                'name': 'UPC Item DB'
            }
        ]
        
        for endpoint in endpoints:
            logger.info(f"Trying {endpoint['name']} API")
            result = self._make_api_request(endpoint['url'], 'CODE128')
            
            if result.get('error') != 'Product not found':
                logger.info(f"Successfully found product in {endpoint['name']}")
                return result
            
            logger.warning(f"Product not found in {endpoint['name']}")
        
        error_msg = 'Product not found in any database'
        logger.error(error_msg)
        return {
            'error': error_msg,
            'details': {
                'barcode': barcode,
                'type': 'CODE128',
                'attempted_apis': [e['name'] for e in endpoints]
            }
        }

    def _handle_qrcode(self, barcode):
        """Handle QR codes with enhanced validation and logging"""
        logger.info(f"Processing QR code: {barcode}")
        
        try:
            if barcode.startswith(('http://', 'https://')):
                logger.info("QR code contains URL")
                return {
                    'type': 'URL',
                    'url': barcode,
                    'message': 'QR code contains a URL',
                    'validation': {
                        'is_valid_url': True,
                        'protocol': barcode.split('://')[0]
                    }
                }
            else:
                logger.info("QR code contains text content")
                return {
                    'type': 'TEXT',
                    'content': barcode,
                    'message': 'QR code contains text content',
                    'validation': {
                        'length': len(barcode),
                        'is_printable': all(c.isprintable() for c in barcode)
                    }
                }
        except Exception as e:
            error_msg = f"Error processing QR code: {str(e)}"
            logger.error(error_msg)
            return {
                'error': error_msg,
                'details': {
                    'barcode': barcode,
                    'type': 'QRCODE'
                }
            }

    def _handle_code39(self, barcode):
        """Handle CODE39 barcodes with inventory lookup"""
        # Example implementation for inventory system
        return {
            'type': 'CODE39',
            'barcode': barcode,
            'message': 'CODE39 barcode detected',
            'inventory_info': self._lookup_inventory(barcode)
        }

    def _handle_unknown(self, barcode):
        """Handle unknown barcode formats"""
        return {
            'error': f'Unsupported barcode format: {barcode}',
            'suggestion': 'Please use EAN-13, UPC-A, CODE128, or QR code'
        }

    def _make_api_request(self, url, barcode_type):
        """Make API request with enhanced retry mechanism and detailed logging"""
        request_details = {
            'url': url,
            'barcode_type': barcode_type,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        logger.info(f"Starting API request: {request_details}")
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.max_retries}")
                response = requests.get(url, timeout=self.api_timeout)
                
                # Log response details
                response_details = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'attempt': attempt + 1
                }
                logger.debug(f"API response details: {response_details}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"API response data: {data}")
                    
                    if 'product' in data:
                        product = data['product']
                        result = {
                            'type': barcode_type,
                            'company': product.get('brands', 'Unknown'),
                            'product_name': product.get('product_name', 'Unknown'),
                            'category': product.get('categories', 'Unknown'),
                            'image_url': product.get('image_url', None)
                        }
                        logger.info(f"Successfully processed API response: {result}")
                        return result
                    else:
                        error_msg = 'Product not found in database'
                        logger.warning(f"{error_msg}. Response: {data}")
                        return {'error': error_msg}
                    
                elif response.status_code == 404:
                    error_msg = 'Product not found in database'
                    logger.warning(f"{error_msg}. Status code: 404")
                    return {'error': error_msg}
                
                elif response.status_code == 429:  # Rate limiting
                    retry_after = response.headers.get('Retry-After', self.retry_delay)
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds")
                    time.sleep(float(retry_after))
                    continue
                
                else:
                    error_msg = f'Unexpected status code: {response.status_code}'
                    logger.error(f"{error_msg}. Response: {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return {'error': error_msg}
                
            except requests.exceptions.Timeout:
                error_msg = f"API request timed out (attempt {attempt + 1})"
                logger.warning(error_msg)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return {'error': 'API request timed out'}
            
            except requests.exceptions.ConnectionError:
                error_msg = f"Connection error (attempt {attempt + 1})"
                logger.error(error_msg)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return {'error': 'Connection error'}
            
            except requests.exceptions.RequestException as e:
                error_msg = f"Request error: {str(e)}"
                logger.error(error_msg)
                return {'error': error_msg}
            
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(error_msg)
                return {'error': error_msg}
        
        error_msg = 'Failed to retrieve product information after multiple attempts'
        logger.error(error_msg)
        return {'error': error_msg}

    def _lookup_inventory(self, barcode):
        """Look up product in inventory system (placeholder implementation)"""
        # This is a placeholder for inventory system integration
        return {
            'status': 'Not implemented',
            'message': 'Inventory lookup system not integrated'
        }

    def has_barcode_pattern(self, image):
        """Check if the image contains a barcode-like pattern"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Sobel edge detection
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate gradient magnitude
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            
            # Normalize
            magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            
            # Apply threshold
            _, binary = cv2.threshold(magnitude, 50, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Check for barcode-like patterns (rectangular shapes with high aspect ratio)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Barcode-like patterns typically have high aspect ratios
                if aspect_ratio > 2.0 and w > 100 and h > 20:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error in barcode pattern detection: {str(e)}")
            return False

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
                
                # Check scan interval and barcode pattern
                current_time = time.time()
                if current_time - self.last_scan_time >= self.scan_interval:
                    if self.has_barcode_pattern(frame):
                        status_placeholder.info("Barcode detected. Scanning...")
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
                            status_placeholder.warning("Could not decode barcode. Try adjusting the angle or lighting.")
                    else:
                        status_placeholder.info("No barcode detected in frame. Hold a barcode in front of the camera.")
                
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
    st.write("Upload images or use your webcam to scan barcodes")
    
    scanner = BarcodeScanner()
    
    mode = st.sidebar.radio("Select Input Mode:", ["Upload Images", "Webcam"])
    
    if mode == "Upload Images":
        # Allow multiple file uploads
        uploaded_files = st.file_uploader("Choose images...", 
                                        type=["jpg", "jpeg", "png"],
                                        accept_multiple_files=True)
        
        if uploaded_files:
            # Add toggle for batch processing
            batch_mode = st.checkbox("Process all images at once", value=True)
            
            if batch_mode:
                # Process all images at once
                if st.button("Scan All Images"):
                    with st.spinner("Processing all images..."):
                        # Add custom CSS for uniform cards
                        st.markdown("""
                            <style>
                            .result-card {
                                padding: 20px;
                                border-radius: 10px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                background-color: #f8f9fa;
                                margin: 20px 0;
                                width: 100%;
                            }
                            .image-container {
                                width: 100%;
                                height: 200px;
                                overflow: hidden;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                background-color: #fff;
                                border-radius: 8px;
                                margin-bottom: 15px;
                            }
                            .image-container img {
                                max-width: 100%;
                                max-height: 100%;
                                object-fit: contain;
                            }
                            .product-info {
                                padding: 15px;
                                background-color: #fff;
                                border-radius: 8px;
                                margin-top: 10px;
                            }
                            .info-grid {
                                display: grid;
                                grid-template-columns: 1fr 1fr;
                                gap: 15px;
                            }
                            .info-item {
                                padding: 10px;
                                background-color: #f8f9fa;
                                border-radius: 5px;
                            }
                            .info-label {
                                font-weight: bold;
                                color: #666;
                                margin-bottom: 5px;
                            }
                            .info-value {
                                color: #333;
                            }
                            </style>
                        """, unsafe_allow_html=True)
                        
                        # Create a container for results
                        results_container = st.container()
                        
                        # Process all images
                        for uploaded_file in uploaded_files:
                            with results_container:
                                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                                
                                # Header with filename
                                st.write(f"### {uploaded_file.name}")
                                
                                # Create two columns for original and product images
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown('<div class="image-container">', unsafe_allow_html=True)
                                    image = Image.open(uploaded_file)
                                    st.image(image, 
                                           caption="Original Image",
                                           use_column_width=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Process the image
                                image_np = np.array(image)
                                barcode = scanner.scan_barcode(image_np)
                                
                                if barcode:
                                    st.success(f"Barcode detected: {barcode}")
                                    product_info = scanner.get_product_info(barcode)
                                    
                                    if 'error' in product_info:
                                        st.error(product_info['error'])
                                    else:
                                        with col2:
                                            if product_info.get('image_url'):
                                                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                                                st.image(product_info['image_url'], 
                                                       caption="Product Image",
                                                       use_column_width=True)
                                                st.markdown('</div>', unsafe_allow_html=True)
                                            else:
                                                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                                                st.write("No product image available")
                                                st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        # Product information in a grid layout
                                        st.markdown('<div class="product-info">', unsafe_allow_html=True)
                                        st.write("### Product Information")
                                        
                                        st.markdown('<div class="info-grid">', unsafe_allow_html=True)
                                        
                                        # Company and Category
                                        st.markdown('<div class="info-item">', unsafe_allow_html=True)
                                        st.markdown('<div class="info-label">Company</div>', unsafe_allow_html=True)
                                        st.markdown(f'<div class="info-value">{product_info["company"]}</div>', unsafe_allow_html=True)
                                        st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        st.markdown('<div class="info-item">', unsafe_allow_html=True)
                                        st.markdown('<div class="info-label">Category</div>', unsafe_allow_html=True)
                                        st.markdown(f'<div class="info-value">{product_info["category"]}</div>', unsafe_allow_html=True)
                                        st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)  # Close info-grid
                                        
                                        # Product Name (full width)
                                        st.markdown('<div class="info-item" style="grid-column: 1 / -1;">', unsafe_allow_html=True)
                                        st.markdown('<div class="info-label">Product Name</div>', unsafe_allow_html=True)
                                        st.markdown(f'<div class="info-value">{product_info["product_name"]}</div>', unsafe_allow_html=True)
                                        st.markdown('</div>', unsafe_allow_html=True)
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)  # Close product-info
                                else:
                                    st.error("No barcode detected in the image")
                                
                                st.markdown('</div>', unsafe_allow_html=True)  # Close result-card
                                st.markdown("---")  # Separator between cards
            else:
                # Process images independently
                # Create a grid layout for results
                cols = st.columns(2)
                col_index = 0
                
                for uploaded_file in uploaded_files:
                    # Display original image
                    image = Image.open(uploaded_file)
                    image_np = np.array(image)
                    
                    # Use alternating columns for better layout
                    with cols[col_index]:
                        st.image(image, 
                               caption=f"Original Image: {uploaded_file.name}",
                               use_column_width=True)
                        
                        if st.button(f"Scan Barcode", key=f"scan_{uploaded_file.name}"):
                            with st.spinner(f"Scanning {uploaded_file.name}..."):
                                barcode = scanner.scan_barcode(image_np)
                                
                                if barcode:
                                    st.success(f"Barcode detected: {barcode}")
                                    product_info = scanner.get_product_info(barcode)
                                    
                                    if 'error' in product_info:
                                        st.error(product_info['error'])
                                    else:
                                        # Create a beautiful card-like display
                                        st.markdown("""
                                            <style>
                                            .product-card {
                                                padding: 20px;
                                                border-radius: 10px;
                                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                                background-color: #f8f9fa;
                                                margin: 10px 0;
                                            }
                                            </style>
                                        """, unsafe_allow_html=True)
                                        
                                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                                        st.write("### Product Information")
                                        
                                        # Display product image if available
                                        if product_info.get('image_url'):
                                            st.image(product_info['image_url'], 
                                                   caption="Product Image",
                                                   use_column_width=True)
                                        
                                        # Display product details in a structured format
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write("**Company:**")
                                            st.write(product_info['company'])
                                            st.write("**Category:**")
                                            st.write(product_info['category'])
                                        with col2:
                                            st.write("**Product Name:**")
                                            st.write(product_info['product_name'])
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)
                                else:
                                    st.error("No barcode detected in the image")
                    
                    # Alternate between columns
                    col_index = (col_index + 1) % 2
                    
                    # Add a separator between images
                    if col_index == 0:
                        st.markdown("---")
    
    else:  # Webcam mode
        if st.button("Start Webcam"):
            scanner.webcam_scan()

if __name__ == "__main__":
    main() 