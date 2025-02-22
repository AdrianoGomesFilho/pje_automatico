import os
import pytesseract
from PIL import Image
import re

# Set the TESSDATA_PREFIX environment variable
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Print environment variables for debugging
print(f"TESSDATA_PREFIX is set to: {os.environ.get('TESSDATA_PREFIX')}")
print(f"Tesseract cmd is set to: {pytesseract.pytesseract.tesseract_cmd}")

# Path to the folder containing images
folder_path = r'C:\Users\fish\script_pje\teste'

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        image_path = os.path.join(folder_path, filename)

        # Open the image file
        image = Image.open(image_path)

        # Perform OCR on the image
        try:
            text = pytesseract.image_to_string(image, lang='eng')
            text = re.sub(r'[^a-z0-9]', '', text.lower())  # Remove non-alphanumeric characters and convert to lowercase
            print(f"Extracted text from {filename}: {text}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")