import fitz
import re

class PDFParserAgent:
    """Hybrid Symbolic + Neural extraction for Objectives"""

    def __init__(self):
        self.patterns = [
            r'(?:(?:^|\n)\s*\d+\.*\s*)?(Objectives\s+and\s+Endpoints)(.+?)(?=\n\s*\d+\.*\s*(Study\s+Design|Methods|Eligibility|Overview)|\Z)',
            r'(?:(?:^|\n)\s*\d+\.*\s*)?(Study\s+Objectives)(.+?)(?=\n\s*\d+\.*\s*(Study\s+Design|Methods|Eligibility|Overview)|\Z)',
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Reads text from a PDF, preserving table-like layout"""
        doc = fitz.open(pdf_path)
        text_blocks = []
        for page in doc:
            blocks = page.get_text("blocks")
            blocks = sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))
            for b in blocks:
                block_text = b[4].strip()
                if block_text:
                    text_blocks.append(block_text)
        doc.close()
        return "\n".join(text_blocks)

    def extract_sections(self, pdf_path: str) -> dict:
        """Main method used by Streamlit app"""
        text = self.extract_text_from_pdf(pdf_path)
        extracted = {"objectives_section_raw": ""}

        for pattern in self.patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                extracted["objectives_section_raw"] = f"{match.group(1)}\n{match.group(2).strip()}"
                break

        if not extracted["objectives_section_raw"] or len(extracted["objectives_section_raw"]) < 300:
            extracted["objectives_section_raw"] = text

        return extracted
