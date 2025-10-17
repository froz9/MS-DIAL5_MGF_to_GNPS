# app.py

import streamlit as st
import pandas as pd
import subprocess
import tempfile
import os

# Import the functions from your first script
from mgf_processor import parse_mgf_to_dataframe, filter_dataframe, generate_output_files

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Metabolomics Files Processor from MS-DIAL to GNPS1",
    page_icon="🧪",
    layout="centered",
    menu_items={
    'Report a bug': "mailto:f9.alan@gmail.com",
    'About': "# This app was developed for those who are interested in processing their *MS-DIAL 5* output files to be suitable for *GNPS1*!"
    }
)

# --- HEADER AND LOGO ---
st.title("Metabolomics Files Processor")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Make sure 'logo_L125.png' is the correct name of your file.
    st.image("logo_L125.png")

st.markdown("---")
st.write("Lab 125, Chemistry Faculty, UNAM, MX")

# --- CREATE TABS FOR THE TWO MODULES ---
tab1, tab2 = st.tabs(["MGF Processor (Python)", "TXT File Formatter (R)"])

# --- TAB 1: MGF PROCESSOR ---
with tab1:
    st.header("MS-DIAL MGF Converter for GNPS & SIRIUS")
    st.write(
        "This tool reformats MGF output files from MS-DIAL 5 for full compatibility with GNPS1 and SIRIUS.",
        "Upload your file to get started."
    )

    mgf_uploaded_file = st.file_uploader(
        "Choose an MGF file",
        type=['mgf'],
        key="mgf_uploader" # Unique key for this uploader
    )

    if mgf_uploaded_file is not None:
        with st.spinner('Processing your MGF file...'):
            df = parse_mgf_to_dataframe(mgf_uploaded_file)
            if df is None or df.empty:
                st.error("Error: Could not parse the MGF file. Please check the file format.")
            else:
                df_filtered = filter_dataframe(df)
                if df_filtered.empty:
                    st.warning("Warning: After filtering, no spectra with peaks were found.")
                else:
                    output_files = generate_output_files(df_filtered)
                    st.success("✅ MGF processing complete! Your files are ready for download.")
                    
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        st.download_button(
                            label="Download for SIRIUS (.mgf)",
                            data=output_files["MGF_FINAL_SIRIUS.mgf"],
                            file_name="MGF_FINAL_SIRIUS.mgf",
                            mime="text/plain"
                        )
                    with dl_col2:
                        st.download_button(
                            label="Download for GNPS (.mgf)",
                            data=output_files["MGF_FINAL_GNPS.mgf"],
                            file_name="MGF_FINAL_GNPS.mgf",
                            mime="text/plain"
                        )

# --- TAB 2: AREA FILE FORMATTER ---
with tab2:
    st.header("MS-DIAL Area/Height File Formatter")
    st.write(
        "This tool uses an R script to reformat Area or Height text files from MS-DIAL for use in GNPS1."
    )
    
    txt_uploaded_file = st.file_uploader(
        "Choose your Area or Height .txt file",
        type=['txt'],
        key="txt_uploader" # Unique key for this uploader
    )

    if txt_uploaded_file is not None:
        with st.spinner("Running R script... this may take a moment."):
            # Create a temporary file to store the upload
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_in:
                tmp_in.write(txt_uploaded_file.getvalue())
                input_path = tmp_in.name
            
            output_path = input_path.replace(".txt", "_gnps.txt")

            try:
                # Construct and run the command to execute the R script
                command = ["Rscript", "process_txt_file.R", input_path, output_path]
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                
                # If the script ran successfully, provide the output for download
                st.success("✅ R script executed successfully!")
                
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="Download Formatted File (.txt)",
                        data=f,
                        file_name="gnps_ready.txt",
                        mime="text/plain"
                    )

            except FileNotFoundError:
                st.error("Error: 'Rscript' command not found. This indicates R is not installed on the server.")
            except subprocess.CalledProcessError as e:
                # If the R script itself returns an error, display it
                st.error("An error occurred while running the R script:")
                st.code(e.stderr, language="text")
            finally:
                # Clean up the temporary files from the server
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
