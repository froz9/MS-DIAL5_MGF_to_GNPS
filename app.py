# app.py

import streamlit as st
import pandas as pd
# Import the functions you created in the other file
from mgf_processor import parse_mgf_to_dataframe, filter_dataframe, generate_output_files

# --- 1. SET UP THE PAGE ---
st.set_page_config(
    page_title="MS-DIAL 5 MGF Formatter for GNPS & SIRIUS",
    page_icon="🧪",
    layout="centered"
)

st.title("Metabolomics MGF File Processor")
st.write(
    "Effortlessly reformat your MGF output files from MS-DIAL 5 to ensure full compatibility with GNPS and SIRIUS. This tool cleans and standardizes your data, preparing it for advanced analysis."
    "Upload your file to get started."
    )


st.write(
    "Upload your file to begin."
    )
# --- 2. FILE UPLOADER ---
# Create the widget that allows users to upload a file
uploaded_file = st.file_uploader(
    "Choose an MGF file", 
    type=['mgf'] # Restrict to .mgf files
)

# --- 3. PROCESSING LOGIC ---
# This code will only run if a user has uploaded a file
if uploaded_file is not None:
    
    # Show a "spinner" message while the functions are running
    with st.spinner('Processing your file... this might take a moment.'):
        
        # Step 1: Parse the uploaded file into a DataFrame
        df = parse_mgf_to_dataframe(uploaded_file)

        # Check if parsing was successful
        if df is None or df.empty:
            st.error("Error: Could not parse the MGF file. Please check the file format and content.")
        else:
            # Step 2: Filter the DataFrame to remove zero-peak spectra
            df_filtered = filter_dataframe(df)

            if df_filtered.empty:
                st.warning("Warning: After filtering, no spectra with peaks were found.")
            else:
                # Step 3: Generate the final MGF file content in memory
                output_files = generate_output_files(df_filtered)

                st.success("✅ Processing complete! Your files are ready for download.")
                
                # --- 4. DOWNLOAD BUTTONS ---
                # Create two columns for the download buttons to sit side-by-side
                col1, col2 = st.columns(2)

                with col1:
                    st.download_button(
                        label="Download for SIRIUS (.mgf)",
                        data=output_files["MGF_FINAL_SIRIUS.mgf"],
                        file_name="MGF_FINAL_SIRIUS.mgf",
                        mime="text/plain"
                    )

                with col2:
                    st.download_button(
                        label="Download for GNPS (.mgf)",
                        data=output_files["MGF_FINAL_GNPS.mgf"],
                        file_name="MGF_FINAL_GNPS.mgf",
                        mime="text/plain"
                    )


# LAB LOGO --- 🎨
# Create three columns with a ratio that centers the middle one
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Add your logo to the middle column.
    # ⚠️ Make sure 'my_logo.png' is the correct name of your file.
    st.image("logo_L125.png")



