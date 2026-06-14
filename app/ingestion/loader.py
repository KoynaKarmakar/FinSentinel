# app/ingestion/loader.py
import fitz  # PyMuPDF
from typing import List
from langchain_core.documents import Document
from app.core.logger import get_logger

logger = get_logger(__name__)

def load_pdf(file_path: str, doc_type: str) -> List[Document]:
    """
    Loads a compliance PDF and formats legal headings so the chunker
    can identify structural section boundaries.
    """
    logger.info(f"Loading regulatory PDF: {file_path} for domain: {doc_type}")
    doc = fitz.open(file_path)
    documents = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        
        # Formatted lines processing to map legal headers into Markdown tags
        processed_lines = []
        for line in text.split("\n"):
            stripped = line.strip()
            
            # Identify Chapters (e.g., "CHAPTER II", "CHAPTER V")
            if stripped.upper().startswith("CHAPTER ") or stripped.upper().startswith("CHPT "):
                processed_lines.append(f"\n# {stripped}\n")
            
            # Identify Sections (e.g., "Section 12:", "Section 3 -")
            elif stripped.upper().startswith("SECTION ") and len(stripped) < 40:
                processed_lines.append(f"\n## {stripped}\n")
                
            # Identify explicit Sub-rules or Key Circular subheadings (e.g., "3. Obligations of...")
            elif stripped and stripped[0].isdigit() and ("." in stripped[:3] or ")" in stripped[:3]) and len(stripped) < 60:
                processed_lines.append(f"\n### {stripped}\n")
                
            else:
                processed_lines.append(line)

        page_content = "\n".join(processed_lines)
        
        # Keep track of essential tracking metadata for compliance citation requirements
        metadata = {
            "source": file_path,
            "doc_type": doc_type,
            "page": page_num + 1
        }
        documents.append(Document(page_content=page_content, metadata=metadata))

    logger.info(f"Successfully loaded {len(documents)} pages from {file_path}")
    return documents