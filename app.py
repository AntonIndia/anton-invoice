import streamlit as st
import pandas as pd
from PIL import Image
import easyocr
import numpy as np
from datetime import datetime

# Initialize EasyOCR reader
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

# Process image with OCR
def extract_text_from_image(image):
    reader = load_ocr()
    # Convert PIL Image to numpy array
    image_np = np.array(image)
    results = reader.readtext(image_np)
    return [text[1] for text in results]

def parse_dc_content(text_list):
    """Parse the extracted text to find relevant information"""
    dc_data = {
        'items': []
    }
    
    current_item = {}
    for text in text_list:
        # Look for DC number
        if 'DC' in text.upper():
            dc_data['dc_number'] = text
            
        # Look for numbers that could be weights or rates
        numbers = [float(s) for s in text.split() if s.replace('.', '').isdigit()]
        if len(numbers) >= 2:  # Possible weight and rate
            current_item = {
                'fabric_type': 'Fabric',  # Default value
                'weight_kg': numbers[0],
                'rate': numbers[1],
                'amount': numbers[0] * numbers[1]
            }
            dc_data['items'].append(current_item)
    
    return dc_data

# Page config
st.set_page_config(
    page_title="Anton Clothing - DC to Invoice",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Title and description
st.title("Anton Clothing - DC to Invoice")
st.write("Upload DC image or capture using camera to generate invoice")

# File upload or camera input
uploaded_file = st.camera_input("Capture DC")
if not uploaded_file:
    uploaded_file = st.file_uploader("Or upload DC image", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='DC Image', use_column_width=True)
    
    # Process button
    if st.button('Generate Invoice'):
        with st.spinner('Processing DC image...'):
            try:
                # Extract text from image
                extracted_text = extract_text_from_image(image)
                st.write("Extracted Text:")
                st.write(extracted_text)  # Display extracted text for debugging
                
                # Parse DC content
                dc_data = parse_dc_content(extracted_text)
                
                if dc_data['items']:
                    # Create DataFrame for display
                    df = pd.DataFrame(dc_data['items'])
                    
                    # Display invoice
                    st.subheader("Generated Invoice")
                    st.dataframe(df)
                    
                    # Calculate totals
                    subtotal = df['amount'].sum()
                    gst = subtotal * 0.18
                    total = subtotal + gst
                    
                    # Display totals
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Subtotal", f"₹{subtotal:.2f}")
                    with col2:
                        st.metric("GST (18%)", f"₹{gst:.2f}")
                    with col3:
                        st.metric("Total", f"₹{total:.2f}")
                    
                    # Add download button
                    st.download_button(
                        "Download Invoice",
                        df.to_csv(index=False),
                        "invoice.csv",
                        "text/csv",
                        key='download-csv'
                    )
                else:
                    st.error("Could not find any items in the DC. Please ensure the image is clear and contains proper data.")
            
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                st.write("Please make sure the image is clear and contains readable text.")