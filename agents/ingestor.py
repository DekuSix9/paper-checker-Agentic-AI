from datetime import datetime
from graph.state import ReviewState
from tools.pdf_tools import extract_pdf_data
from tools.rag_tools import index_paper_chunks
from logging_utils.logger import StructuredLogger


def run(state: ReviewState) -> dict:
    """Paper Ingestor Agent: Parses PDF, structures text into sections, chunks and indexes into ChromaDB."""
    agent_name = "Paper Ingestor"
    paper_path = state.get("paper_path", "")

    StructuredLogger.log(agent_name, "start_ingestion", {"paper_path": paper_path})

    try:
        extracted = extract_pdf_data(paper_path)
        raw_text = extracted["paper_raw_text"]
        structured = extracted["paper_structured"]

        # Chunk and index into ChromaDB
        chunk_count = index_paper_chunks(raw_text, paper_id=structured.get("title", "paper_1")[:30])

        trace_entry = {
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "message": f"Successfully parsed paper title '{structured.get('title')}' into {len(structured.get('sections', {}))} sections and {chunk_count} vector chunks."
        }

        StructuredLogger.log(agent_name, "finish_ingestion", {"chunk_count": chunk_count, "title": structured.get("title")})

        return {
            "paper_raw_text": raw_text,
            "paper_structured": structured,
            "agent_trace": [trace_entry]
        }
    except Exception as e:
        error_msg = f"Failed to parse PDF: {str(e)}"
        StructuredLogger.log(agent_name, "ingestion_error", {"error": error_msg}, level="ERROR")
        
        fallback_structured = {
            "title": "Fallback Paper Title",
            "abstract": "Failed to parse PDF abstract.",
            "sections": {"method": "", "results": "", "related_work": ""},
            "captions": [],
            "references": []
        }
        
        return {
            "paper_raw_text": f"Error loading PDF: {str(e)}",
            "paper_structured": fallback_structured,
            "agent_trace": [{
                "agent": agent_name,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "message": error_msg
            }],
            "errors": [{"agent": agent_name, "error": error_msg}]
        }
