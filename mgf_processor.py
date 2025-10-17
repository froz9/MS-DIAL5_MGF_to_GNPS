# mgf_processor.py


import pandas as pd
import numpy as np
import re
import io  # <--- ADD THIS LINE
from pyteomics import mgf

# mgf_processor.py

# --- (Keep imports and other functions the same) ---

# --- FUNCTION 1: Load and Parse MGF file (UPDATED VERSION) ---
def parse_mgf_to_dataframe(uploaded_file):
    """
    Reads an uploaded MGF file, cleans it, and parses it into a pandas DataFrame.
    
    Args:
        uploaded_file: A file-like object from a web uploader (e.g., Streamlit).

    Returns:
        A pandas DataFrame with the parsed spectral data, or None if parsing fails.
    """
    try:
        mgf_content = uploaded_file.getvalue().decode('utf-8')
        
        filtered_lines = []
        for line in mgf_content.splitlines():
            if not line.strip().startswith('Num Peaks:'):
                filtered_lines.append(line)
        
        cleaned_content = "\n".join(filtered_lines)
        string_buffer = io.StringIO(cleaned_content)
        
        spectra = []
        # THIS IS THE ONLY LINE THAT CHANGED
        with mgf.read(string_buffer, use_index=False, encoding='utf-8') as reader:
            spectra = list(reader)

        if not spectra:
            print("Warning: No spectra found in the file after cleaning.")
            return None

        metadata = []
        for i, spec in enumerate(spectra):
            params = spec.get('params', {})
            
            title_str = params.get('title', '')
            match = re.search(r'ID=(\d+)\|', title_str)
            scan_id = int(match.group(1)) if match else i
            
            pepmass_val = params.get('pepmass', [0])[0]
            rt_min_val = params.get('rtinminutes', [0.0])[0]

            row = {
                'scans': scan_id,
                'pepmass': float(pepmass_val),
                'rt_in_minutes': float(rt_min_val),
                'charge': params.get('charge'),
                'ion': params.get('ion', ''),
                'm_z_array': spec.get('m/z array', np.array([])),
                'intensity_array': spec.get('intensity array', np.array([])),
            }
            metadata.append(row)

        df_spectra = pd.DataFrame(metadata)
        df_spectra['num_peaks'] = df_spectra['m_z_array'].apply(len)
        df_spectra.set_index('scans', inplace=True)
        
        print(f"✅ Successfully parsed {len(df_spectra)} spectra into a DataFrame.")
        return df_spectra

    except Exception as e:
        print(f"❌ ERROR during parsing: {e}")
        return None

# --- FUNCTION 2: Filter DataFrame ---
def filter_dataframe(df):
    """
    Filters out spectra with zero peaks.

    Args:
        df (pd.DataFrame): The input DataFrame of spectra.

    Returns:
        A new DataFrame with zero-peak spectra removed.
    """
    if df is None or df.empty:
        return pd.DataFrame() # Return an empty frame if input is bad
        
    initial_count = len(df)
    df_filtered = df[df['num_peaks'] > 0].copy()
    final_count = len(df_filtered)
    removed_count = initial_count - final_count
    
    print(f"✅ Filtered {removed_count} zero-peak spectra. Final count: {final_count}")
    return df_filtered

# --- FUNCTION 3: Generate Output MGF Files ---
def generate_output_files(df_data):
    """
    Generates MGF content for SIRIUS and GNPS formats from a DataFrame.
    This function contains your original 'write_custom_mgf' logic.

    Args:
        df_data (pd.DataFrame): The final, filtered DataFrame.

    Returns:
        A dictionary containing the filenames and string content for each MGF file.
    """
    
    # Helper function nested inside, as it's only used here
    def _write_mgf_to_string(file_type):
        output = io.StringIO() # Writes to an in-memory string
        PEAK_FORMAT = "%.6f %.0f\n"

        for scan_id, row in df_data.iterrows():
            output.write("BEGIN IONS\n")

            if file_type == "SIRIUS":
                output.write(f"FEATURE_ID={scan_id}\n")
            elif file_type == "GNPS":
                output.write(f"SCANS={scan_id}\n")

            output.write(f"PEPMASS={row['pepmass']}\n")
            output.write("MSLEVEL=2\n")

            if file_type == "SIRIUS":
                output.write(f"RTINSECONDS={row['rt_in_minutes'] * 60:.4f}\n")
            elif file_type == "GNPS":
                output.write(f"RTINMINUTES={row['rt_in_minutes']:.4f}\n")
                if row['ion']:
                    output.write(f"ION={row['ion']}\n")
            
            charge_list = row['charge']
            if charge_list and isinstance(charge_list, list):
                charge_str = str(charge_list[0])
                if charge_str.endswith(('+', '-')):
                    output.write(f"CHARGE={charge_str}\n")
                else:
                    output.write(f"CHARGE={charge_str}+\n")

            for mz, intensity in zip(row['m_z_array'], row['intensity_array']):
                output.write(PEAK_FORMAT % (mz, intensity))

            output.write("END IONS\n\n")

        return output.getvalue() # Return the complete string

    sirius_content = _write_mgf_to_string("SIRIUS")
    gnps_content = _write_mgf_to_string("GNPS")
    
    print("✅ Generated MGF content for SIRIUS and GNPS.")
    
    return {
        "MGF_FINAL_SIRIUS.mgf": sirius_content,
        "MGF_FINAL_GNPS.mgf": gnps_content

    }

# --- For process_area_file ---
def process_area_file_python(uploaded_file):
    """
    Now returns a detailed error if something goes wrong.
    """
    try:
        # Read the file without headers
        df = pd.read_csv(uploaded_file, sep='\t', header=None)

        # 1. Identify and remove 'Average' and 'Stdev' columns based on row 4 (index 3)
        cols_to_remove = df.iloc[3][df.iloc[3].isin(["Average", "Stdev"])].index
        df_modified = df.drop(columns=cols_to_remove)

        # 2. Remove the original header row (now at index 3)
        df_modified = df_modified.drop(index=3).reset_index(drop=True)

        # 3. Define the new GNPS headers
        gnps_cols = ["Alignment ID", "Average Rt(min)", "Average Mz", "Metabolite name",
                     "Adduct ion name", "Post curation result", "Fill %", "MS/MS included",
                     "Formula", "Ontology", "INCHIKEY", "SMILES",
                     "Comment", "Isotope tracking parent ID", "Isotope tracking weight number", "Dot product",
                     "Reverse dot product", "Fragment presence %", "S/N average", "Spectrum reference file name",
                     "MS1 isotopic spectrum"]

        # 4. Remove other unnecessary columns by their integer position
        cols_to_drop_by_index = [8, 9, 14, 15, 16, 17, 19, 20, 23, 24, 25, 26, 27]
        df_modified = df_modified.drop(columns=df_modified.columns[cols_to_drop_by_index])
        
        # 5. Assign the new headers to the correct row (now at index 3) and promote them
        df_modified.iloc[3] = gnps_cols
        df_modified.columns = df_modified.iloc[3]
        
        # 6. Remove features without an MS2 scan
        df_final = df_modified[df_modified["MS/MS included"] != "null"].copy()
        
        # Convert the final DataFrame to a tab-separated string for download
        output_string = df_final.to_csv(sep='\t', header=False, index=False)
        
        # On success, return a tuple: (True, and the data)
        return (True, output_string)

    except Exception as e:
        # On failure, return a tuple: (False, and the specific error message)
        error_message = f"Processing failed. The file structure may be different than expected. **Specific error: {e}**"
        print(error_message) # This prints to the server log
        return (False, error_message)