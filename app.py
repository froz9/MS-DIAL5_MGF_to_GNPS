# app.py

import streamlit as st
import pandas as pd
from mgf_processor import (
    parse_mgf_to_dataframe,
    filter_dataframe,
    generate_output_files,
    process_area_file_python
)

st.set_page_config(
    page_title="Metabolomics File Processor",
    page_icon="🧪",
    layout="centered",
    menu_items={
    'Report a bug': "mailto:f9.alan@gmail.com",
    'About': "# This app was developed for those who are interested in processing their *MS-DIAL 5* output files to be suitable for *GNPS1*!"
    }
)

st.title("Metabolomics Files Processor")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo_L125.png")

st.markdown("---")
st.write("Lab 125, Chemistry Faculty, UNAM, MX")

tab1, tab2 = st.tabs(["MGF Processor", "Area/Height File Formatter"])

# --- TAB 1: MGF PROCESSOR ---
with tab1:
    st.header("MS-DIAL MGF Converter for GNPS1 & SIRIUS")
    st.write("This app reformats MGF output files from MS-DIAL 5 for full compatibility with GNPS1 and SIRIUS.",
        "Upload your file to get started.")
    mgf_uploaded_file = st.file_uploader(
        "Choose an MGF file",
        type=['mgf'],
        key="mgf_uploader"  # <-- Key 1
    )

    if mgf_uploaded_file:
        with st.spinner('Processing MGF file...'):
            df = parse_mgf_to_dataframe(mgf_uploaded_file)
            if df is None or df.empty:
                st.error("Error: Could not parse the MGF file.")
            else:
                df_filtered = filter_dataframe(df)
                if df_filtered.empty:
                    st.warning("Warning: No spectra with peaks were found after filtering.")
                else:
                    output_files = generate_output_files(df_filtered)
                    st.success("✅ MGF processing complete!")
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        st.download_button("Download for SIRIUS (.mgf)", output_files["MGF_FINAL_SIRIUS.mgf"], "MGF_FINAL_SIRIUS.mgf")
                    with dl_col2:
                        st.download_button("Download for GNPS1 (.mgf)", output_files["MGF_FINAL_GNPS.mgf"], "MGF_FINAL_GNPS.mgf")

# --- TAB 2: AREA FILE FORMATTER (WITH BETTER ERROR HANDLING) ---
with tab2:
    st.header("MS-DIAL Area/Height File Formatter")
    st.write("Reformats Area or Height text files from MS-DIAL 5 for use in GNPS1.")
    txt_uploaded_file = st.file_uploader(
        "Choose an Area or Height .txt file",
        type=['txt'],
        key="txt_uploader"
    )

    if txt_uploaded_file:
        with st.spinner("Processing your text file..."):
            # The function now returns a success status and the result (data or error message)
            success, result = process_area_file_python(txt_uploaded_file)
            
            if success:
                st.success("✅ File formatting complete!")
                st.download_button(
                    label="Download Formatted File (.txt)",
                    data=result, # result is the processed data string
                    file_name="txt_GNPS.txt",
                    mime="text/plain"
                )
            else:
                # If it failed, result is the specific error message
                st.error(result)