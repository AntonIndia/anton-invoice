import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Anton Clothing - DC to Invoice",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def extract_text_from_image(image):
    """Extract text from image using Tesseract OCR"""
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error in OCR processing: {str(e)}")
        return None

def parse_text(text):
    """Parse the extracted text to find items"""
    lines = text.split('\n')
    items = []
    
    for line in lines:
        # Split line into words
        words = line.split()
        # Look for patterns of numbers (weight and rate)
        numbers = []
        for word in words:
            try:
                num = float(word.replace('kg', '').replace('rs', '').strip())
                numbers.append(num)
            except ValueError:
                continue
        
        if len(numbers) >= 2:  # We found potential weight and rate
            items.append({
                'fabric_type': 'Fabric',
                'weight_kg': numbers[0],
                'rate': numbers[1],
                'amount': numbers[0] * numbers[1]
            })
    
    return items

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
        with st.spinner('Processing...'):
            # Extract text
            extracted_text = extract_text_from_image(image)
            
            if extracted_text:
                # Show extracted text for debugging
                st.subheader("Extracted Text")
                st.text(extracted_text)
                
                # Parse items
                items = parse_text(extracted_text)
                
                if items:
                    # Create DataFrame
                    df = pd.DataFrame(items)
                    
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
                    
                    # Add edit capability
                    st.subheader("Edit Invoice")
                    edited_df = st.data_editor(df)
                    
                    # Download button
                    st.download_button(
                        "Download Invoice",
                        edited_df.to_csv(index=False),
                        "invoice.csv",
                        "text/csv",
                        key='download-csv'
                    )
                else:
                    st.warning("No items found in the text. Please check the image clarity.")
            else:
                st.error("Failed to extract text from image. Please ensure the image is clear.")