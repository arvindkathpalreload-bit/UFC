import streamlit as st
import os
import tempfile
from markitdown import MarkItDown

# --- Page Configuration ---
st.set_page_config(
    page_title="Universal File-to-Text Converter",
    page_icon="📄",
    layout="centered"
)

# --- Title & Description ---
st.title("📄 Universal File-to-Text Converter")
st.markdown("""
    Upload your **Word, Excel, PowerPoint, PDF, or HTML** files below. 
    The tool will extract the content and convert it into clean **Markdown** format.
""")

# --- Helper Function: Conversion Logic ---
def convert_file(file_path):
    """
    Uses MarkItDown to process the file. 
    Returns the text content or raises an error.
    """
    # Initialize MarkItDown
    # Note: MarkItDown handles requests internally, but for local files,
    # we rely on its file parsing capabilities.
    md = MarkItDown()
    
    # Perform conversion
    result = md.convert(file_path)
    return result.text_content

# --- Main Application Logic ---

# 1. Upload Area
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    accept_multiple_files=True,
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'zip', 'txt', 'csv']
)

if uploaded_files:
    st.write("---")
    st.subheader("📝 Processed Files")

    for uploaded_file in uploaded_files:
        # Create a container for each file to keep the UI clean
        with st.expander(f"File: {uploaded_file.name}", expanded=True):
            
            # Create a temporary file to save the uploaded bytes
            # MarkItDown requires a file path to process
            try:
                # Determine file extension to help MarkItDown (though it usually auto-detects)
                suffix = os.path.splitext(uploaded_file.name)[1]
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                # Attempt Conversion
                with st.spinner(f"Converting {uploaded_file.name}..."):
                    converted_text = convert_file(tmp_file_path)

                # 2. Instant Preview
                st.success("Conversion Successful!")
                st.text_area("Preview content:", value=converted_text, height=300)

                # Prepare filenames for download
                base_name = os.path.splitext(uploaded_file.name)[0]
                md_filename = f"{base_name}_converted.md"
                txt_filename = f"{base_name}_converted.txt"

                # 3. Download Options (Columns for side-by-side buttons)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="⬇️ Download as Markdown (.md)",
                        data=converted_text,
                        file_name=md_filename,
                        mime="text/markdown"
                    )
                
                with col2:
                    st.download_button(
                        label="⬇️ Download as Text (.txt)",
                        data=converted_text,
                        file_name=txt_filename,
                        mime="text/plain"
                    )

            except Exception as e:
                # 3. Resilience: Graceful error handling
                st.error(f"⚠️ Could not read **{uploaded_file.name}**. Please check the format.")
                # Optional: Log the specific error to console for debugging if needed
                print(f"Error processing {uploaded_file.name}: {e}")

            finally:
                # Cleanup: Remove the temporary file to save space
                if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
