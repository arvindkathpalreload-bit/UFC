import streamlit as st
import os
import tempfile
import pdfplumber
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

# --- Helper 1: Size Formatter ---
def format_file_size(size_in_bytes):
    """Converts bytes to readable KB or MB"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} TB"

# --- Helper 2: Conversion Logic ---
def convert_file(file_path, file_extension):
    """
    Uses MarkItDown as the primary engine.
    If it fails on a PDF, falls back to pdfplumber.
    """
    try:
        # PRIMARY ENGINE: MarkItDown
        md = MarkItDown()
        result = md.convert(file_path)
        
        # If result is empty and it's a PDF, force an error to trigger fallback
        if not result.text_content.strip() and file_extension == '.pdf':
            raise ValueError("Empty result from MarkItDown")
            
        return result.text_content

    except Exception as e:
        # FALLBACK ENGINE: pdfplumber (Only for PDFs)
        if file_extension == '.pdf':
            try:
                text_content = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                return "\n\n---\n\n".join(text_content)
            except Exception as fallback_e:
                raise e
        else:
            raise e

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
        with st.expander(f"File: {uploaded_file.name}", expanded=True):
            
            filename, file_extension = os.path.splitext(uploaded_file.name)
            file_extension = file_extension.lower()

            try:
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                # Convert
                with st.spinner(f"Converting {uploaded_file.name}..."):
                    converted_text = convert_file(tmp_file_path, file_extension)

                # --- NEW: Calculate Sizes ---
                original_size_bytes = uploaded_file.size
                # Calculate size of the resulting string in bytes (assuming utf-8)
                converted_size_bytes = len(converted_text.encode('utf-8'))
                
                # Calculate Percentage Reduction
                if original_size_bytes > 0:
                    reduction_pct = ((original_size_bytes - converted_size_bytes) / original_size_bytes) * 100
                else:
                    reduction_pct = 0

                # --- NEW: Tabs Interface ---
                tab_preview, tab_stats = st.tabs(["📄 Preview", "📊 File Size Comparison"])

                with tab_preview:
                    st.text_area("Preview content:", value=converted_text, height=300)

                with tab_stats:
                    # Metrics Display
                    st.success(f"**Text version is {reduction_pct:.1f}% smaller.**")
                    
                    # Create a clean data dictionary for the table
                    stats_data = [
                        {"Metric": "Original file size", "Size": format_file_size(original_size_bytes)},
                        {"Metric": "Converted .txt file size", "Size": format_file_size(converted_size_bytes)}
                    ]
                    st.table(stats_data)

                # Download Buttons
                md_filename = f"{filename}_converted.md"
                txt_filename = f"{filename}_converted.txt"
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button("⬇️ Download as Markdown (.md)", converted_text, md_filename, "text/markdown")
                with col2:
                    st.download_button("⬇️ Download as Text (.txt)", converted_text, txt_filename, "text/plain")

            except Exception as e:
                st.error(f"⚠️ Could not read **{uploaded_file.name}**. Please check the format.")
                with st.expander("See technical error details"):
                    st.write(e)

            finally:
                if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                    try: os.remove(tmp_file_path)
                    except: pass
