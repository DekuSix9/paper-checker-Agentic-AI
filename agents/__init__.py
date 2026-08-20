"""Agents package initialization."""
from .ingestor import run as run_ingestor
from .novelty import run as run_novelty
from .methodology import run as run_methodology
from .stats_rigor import run as run_stats_rigor
from .writing_quality import run as run_writing_quality
from .ethics import run as run_ethics
from .ai_detector import run as run_ai_detector
from .area_chair import run as run_area_chair, finalize as finalize_area_chair

__all__ = [
    "run_ingestor",
    "run_novelty",
    "run_methodology",
    "run_stats_rigor",
    "run_writing_quality",
    "run_ethics",
    "run_ai_detector",
    "run_area_chair",
    "finalize_area_chair"
]
