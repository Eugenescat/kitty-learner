"""PDF parsing and text chunking module."""

import fitz  # pymupdf
from dataclasses import dataclass


@dataclass
class Chunk:
    """A chunk of text from the PDF."""
    index: int
    text: str
    page_num: int


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """
    Split text into chunks of approximately chunk_size characters.
    
    Uses paragraph boundaries when possible, falls back to sentence/word boundaries.
    """
    # Split by double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    chunks = []
    current_chunk = ""
    chunk_index = 0
    
    for para in paragraphs:
        # If adding this paragraph exceeds chunk_size, save current and start new
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(Chunk(
                index=chunk_index,
                text=current_chunk.strip(),
                page_num=0  # Simplified: not tracking page numbers in Phase 1
            ))
            chunk_index += 1
            # Keep some overlap for context
            words = current_chunk.split()
            overlap_words = words[-overlap//5:] if len(words) > overlap//5 else []
            current_chunk = ' '.join(overlap_words) + ' ' + para
        else:
            current_chunk += '\n\n' + para if current_chunk else para
    
    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(Chunk(
            index=chunk_index,
            text=current_chunk.strip(),
            page_num=0
        ))
    
    return chunks


def parse_pdf(pdf_path: str, chunk_size: int = 500) -> list[Chunk]:
    """Main entry point: PDF file -> list of text chunks."""
    text = extract_text_from_pdf(pdf_path)
    return chunk_text(text, chunk_size)


if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 1:
        chunks = parse_pdf(sys.argv[1])
        print(f"Extracted {len(chunks)} chunks")
        for chunk in chunks[:3]:
            print(f"\n--- Chunk {chunk.index} ---")
            print(chunk.text[:200] + "...")
