# app/ingestion/chunker.py
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from app.core.logger import get_logger

logger = get_logger(__name__)

def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Splits documents along legal structural headers, safely falling back onto a text 
    splitter if an individual clause is extraordinarily long, ensuring a flat list of 
    Document objects is returned.
    """
    # 1. Define the structural tags injected by the loader
    headers_to_split_on = [
        ("#", "chapter"),
        ("##", "section"),
        ("###", "subsection"),
    ]
    
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
    
    # 2. Fallback splitter just in case a single legal appendix text is massive
    fallback_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, 
        chunk_overlap=100
    )
    
    final_chunks = []
    
    for doc in documents:
        # Split text strictly using structural markdown markers
        header_chunks = header_splitter.split_text(doc.page_content)
        
        for chunk in header_chunks:
            # Explicitly carry forward original page-level and file-level tracking metadata
            chunk.metadata.update(doc.metadata)
            
            # If a structural section is small and self-contained, keep it complete
            if len(chunk.page_content) <= 1500:
                final_chunks.append(chunk)
            else:
                # If an appendix or definition list is too long, subdivide it
                # Using split_text preserves precise character segmentation control
                sub_strings = fallback_text_splitter.split_text(chunk.page_content)
                
                # Re-wrap each sub-string explicitly into a clean, flat LangChain Document object
                for text_segment in sub_strings:
                    new_sub_chunk = Document(
                        page_content=text_segment,
                        metadata=chunk.metadata.copy()  # Ensure metadata duplicates correctly
                    )
                    final_chunks.append(new_sub_chunk)
                
    logger.info(f"Created {len(final_chunks)} clean structural chunks based on heading hierarchies.")
    return final_chunks