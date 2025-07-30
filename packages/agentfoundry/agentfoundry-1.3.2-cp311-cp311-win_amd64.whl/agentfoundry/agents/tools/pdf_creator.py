import markdown
import pdfkit
import tempfile
import os
from langchain_core.tools import Tool


def pdf_generator(md: str) -> str:
    try:
        html = markdown.markdown(md, extensions=['tables'])
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdfkit.from_string(
                html,
                tmp.name,
                options={"enable-local-file-access": None}
            )
            temp_pdf_path = tmp.name
        return f"{temp_pdf_path}"
    except Exception as e:
        return f"Error executing query: {e}"


# Wrap the function as a LangChain Tool.
pdf_creator_tool = Tool(
    name="pdf_file_creator",
    func=pdf_generator,
    description=(
        "Creates a PDF file using a string input containing markdown style text format. The function returns the "
        "PDF file's temporary file path."
    )
)

