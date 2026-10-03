"""Ingest layer: validation boundary + pipeline entry point (Phase 2)."""
from nyaysaakshya.ingest.validate import (
    validate_capture, CaptureValidation, ValidationResult,
)
from nyaysaakshya.ingest.pipeline import analyze_capture

__all__ = ["validate_capture", "CaptureValidation", "ValidationResult", "analyze_capture"]
