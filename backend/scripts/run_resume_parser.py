"""Local runner for testing the ResumeParser service.

Usage examples:
  # Parse a local PDF/DOCX/TXT file
  python backend/scripts/run_resume_parser.py --file path/to/resume.pdf

  # Parse from raw text
  python backend/scripts/run_resume_parser.py --text "First line\nExperience: ..."

  # Parse from URL
  python backend/scripts/run_resume_parser.py --url https://example.com/resume.pdf

This script calls the existing ResumeParser implementation in
`backend/app/services/resume_parser.py` and prints a JSON representation
of the parsed result.
"""

import argparse
import asyncio
import json
import logging
from dataclasses import asdict
from pathlib import Path

import sys

# Make sure project root is on sys.path when run from repository root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "app"))

try:
    # Imported using module path relative to backend/app
    from services.resume_parser import ResumeParser
    from services.llm_postprocess import postprocess
except Exception:
    # Fallback: try package import
    from services.resume_parser import ResumeParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def serialize(obj):
    """Serialize dataclasses / complex objects to JSON-safe types."""
    try:
        return json.loads(json.dumps(asdict(obj), default=str))
    except Exception:
        # Fallback generic serializer
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)


async def run_file(file_path: str, use_llm: bool = False):
    parser = ResumeParser()
    result = await parser.parse_resume(file_path)
    serialized = serialize(result)
    if use_llm:
        try:
            serialized = postprocess(serialized, serialized.get("raw_text", ""), mode="mock")
        except Exception as e:
            logger.error(f"LLM postprocess failed: {e}")
    print(json.dumps(serialized, indent=2, ensure_ascii=False))


async def run_text(text: str):
    # Write to a temporary file and call parse_resume to reuse extraction logic
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
        tmp.write(text)
        tmp_path = tmp.name

    try:
        await run_file(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


async def run_url(url: str, use_llm: bool = False):
    parser = ResumeParser()
    result = await parser.parse_resume_from_url(url)
    serialized = serialize(result)
    if use_llm:
        try:
            serialized = postprocess(serialized, serialized.get("raw_text", ""), mode="mock")
        except Exception as e:
            logger.error(f"LLM postprocess failed: {e}")
    print(json.dumps(serialized, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="Run resume parser locally")
    ap.add_argument("--file", help="Path to resume file (pdf/docx/txt)")
    ap.add_argument("--text", help="Raw resume text to parse")
    ap.add_argument("--url", help="URL to resume or profile to parse")
    ap.add_argument("--llm", action="store_true", help="Run post-processing via LLM (mock mode)")
    ap.add_argument("--llm-provider", choices=["mock", "bedrock"], default="mock", help="LLM provider to use for postprocessing")

    args = ap.parse_args()

    if not (args.file or args.text or args.url):
        ap.print_help()
        return

    try:
        if args.file:
            asyncio.run(run_file(args.file, use_llm=args.llm))
        elif args.text:
            asyncio.run(run_text(args.text))
        elif args.url:
            asyncio.run(run_url(args.url, use_llm=args.llm))
        # Note: provider is read inside postprocess via environment or can be extended here
    except Exception as e:
        logger.error(f"Error while parsing: {e}")


if __name__ == "__main__":
    main()
