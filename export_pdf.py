import streamlit as st
from fpdf import FPDF
import base64

# Function to generate PDF content
def generate_pdf(report_text, line_spacing=1.5, lines_per_paragraph=5, paragraph_spacing=4):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Split report text into paragraphs
    paragraphs = report_text.split('\n\n')  # Assuming paragraphs are separated by double newline
    for paragraph in paragraphs:
        lines = paragraph.split('\n')
        for i in range(0, len(lines), lines_per_paragraph):
            # Add line breaks to simulate line spacing
            for _ in range(lines_per_paragraph):
                pdf.multi_cell(0, paragraph_spacing, '')
            pdf.multi_cell(0, 10 * line_spacing, '\n'.join(lines[i:i+lines_per_paragraph]))
            pdf.ln()

    return pdf.output(dest="S").encode("latin-1")

# Function to create download link
def create_download_link(val, filename, file_format='pdf'):
    # Determine MIME type for different file formats
    mime_types = {
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    b64 = base64.b64encode(val)  # val looks like b'...'
    mime_type = mime_types.get(file_format, 'application/octet-stream')
    return f'<a href="data:{mime_type};base64,{b64.decode()}" download="{filename}.{file_format}">Download {file_format.upper()}</a>'

# Streamlit app
def show_pdf_export():
    st.title("PDF Export Example")
    report_text = st.text_area("Enter Report Text", height=200)
    line_spacing = st.slider("Line Spacing", min_value=0.1, max_value=2.0, step=0.1, value=1.5)
    paragraph_spacing = st.slider("Paragraph Spacing", min_value=1, max_value=8, step=1, value=4)
    lines_per_paragraph = st.slider("Lines per Paragraph", min_value=1, max_value=10, step=1, value=5)
    export_as_pdf = st.button("Export Report")

    if export_as_pdf and report_text.strip():
        try:
            pdf_content = generate_pdf(report_text, line_spacing, lines_per_paragraph, paragraph_spacing)
            html_pdf = create_download_link(pdf_content, "report", file_format='pdf')
            html_txt = create_download_link(report_text.encode("utf-8"), "report", file_format='txt')
            st.markdown(html_pdf, unsafe_allow_html=True)
            st.markdown(html_txt, unsafe_allow_html=True)
            st.success("PDF and Text files successfully generated and ready for download!")
        except Exception as e:
            st.error(f"Error generating files: {e}")

# Run the app
if __name__ == "__main__":
    show_pdf_export()
