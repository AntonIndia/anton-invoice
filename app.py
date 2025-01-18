import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime

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
        with st.spinner('Processing...'):
            # For now, let's create a sample invoice
            sample_data = {
                'fabric_type': ['Cotton', 'Polyester'],
                'weight_kg': [10.5, 8.2],
                'rate': [200, 150],
                'amount': [2100, 1230]
            }
            
            df = pd.DataFrame(sample_data)
            
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