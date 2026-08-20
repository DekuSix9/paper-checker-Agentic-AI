import os
import re
from typing import Dict, Any, List


def extract_pdf_data(pdf_path: str) -> Dict[str, Any]:
    """Extract raw text and structured sections from a PDF or text file."""
    raw_text = ""
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Paper file not found at path: {pdf_path}")

    # Support txt / md files directly
    if pdf_path.endswith(".txt") or pdf_path.endswith(".md"):
        with open(pdf_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
    else:
        # Extract via PyMuPDF (fitz)
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            pages_text = []
            for page in doc:
                pages_text.append(page.get_text())
            raw_text = "\n\n".join(pages_text)
        except Exception as e:
            # Fallback to pdfplumber or basic reading
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    pages = [p.extract_text() or "" for p in pdf.pages]
                    raw_text = "\n\n".join(pages)
            except Exception as e2:
                raise RuntimeError(f"Failed to parse PDF with fitz and pdfplumber: {e2}")

    structured = parse_structured_sections(raw_text)
    return {
        "paper_raw_text": raw_text,
        "paper_structured": structured
    }


def parse_structured_sections(text: str) -> Dict[str, Any]:
    """Parse text into sections using regex pattern matching for academic headings."""
    lines = text.split("\n")
    
    # Extract Title (usually first non-empty lines)
    non_empty_lines = [l.strip() for l in lines if l.strip()]
    title = non_empty_lines[0] if non_empty_lines else "Untitled Research Paper"
    
    section_patterns = {
        "abstract": r"(?i)^(?:1\.?\s*)?abstract",
        "introduction": r"(?i)^(?:1\.?\s*|2\.?\s*)?introduction",
        "related_work": r"(?i)^(?:2\.?\s*|3\.?\s*)?(related work|background|literature review)",
        "method": r"(?i)^(?:3\.?\s*|4\.?\s*)?(method|methodology|proposed approach|system architecture|model)",
        "results": r"(?i)^(?:4\.?\s*|5\.?\s*)?(results|experiments|evaluation|experimental results)",
        "discussion": r"(?i)^(?:5\.?\s*|6\.?\s*)?(discussion|analysis|limitations)",
        "conclusion": r"(?i)^(?:6\.?\s*|7\.?\s*)?(conclusion|concluding remarks)",
        "references": r"(?i)^(?:7\.?\s*|8\.?\s*)?(references|bibliography)"
    }
    
    sections = {
        "abstract": "",
        "introduction": "",
        "related_work": "",
        "method": "",
        "results": "",
        "discussion": "",
        "conclusion": "",
        "references": ""
    }
    
    current_section = "introduction"
    section_buffers: Dict[str, List[str]] = {k: [] for k in sections.keys()}
    
    for line in lines:
        stripped = line.strip()
        matched = False
        for sec_name, pattern in section_patterns.items():
            if re.match(pattern, stripped):
                current_section = sec_name
                matched = True
                break
        if not matched and current_section:
            section_buffers[current_section].append(line)
            
    for sec_name in sections.keys():
        sections[sec_name] = "\n".join(section_buffers[sec_name]).strip()

    # Extract captions (Figure X / Table Y)
    captions = re.findall(r"(?i)(?:Figure|Fig\.|Table)\s+\d+[:\.]?\s*[^\n]+", text)
    references = re.findall(r"\[\d+\]\s+[^\n]+", sections["references"]) if sections["references"] else []

    # If abstract was empty, extract paragraph around "Abstract" keyword
    if not sections["abstract"]:
        abs_match = re.search(r"(?i)abstract[:\s]+([\s\S]{100,1000}?)(?=\n\n|\n[A-Z0-9])", text)
        if abs_match:
            sections["abstract"] = abs_match.group(1).strip()
        else:
            sections["abstract"] = "\n".join(non_empty_lines[1:5])

    return {
        "title": title,
        "abstract": sections["abstract"],
        "sections": sections,
        "captions": captions,
        "references": references
    }
