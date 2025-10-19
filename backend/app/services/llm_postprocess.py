"""LLM postprocessing prototype for resume parsing.

Provides a mock `postprocess` function that normalizes parser output and a
placeholder hook for real LLM providers (OpenAI/Bedrock) if later desired.

This module is intentionally self-contained and safe to run offline. Use
`mode='mock'` to run the deterministic heuristic normalizer.
"""
from typing import Dict, Any
import logging
import re
import json
import os
import time

import boto3
from botocore.config import Config as BotoConfig

logger = logging.getLogger(__name__)


def _is_section_heading(text: str) -> bool:
    """Return True if the text looks like a section heading (e.g., SUMMARY)."""
    if not text:
        return False
    t = text.strip()
    # If it's short and mostly uppercase words, treat as heading
    if len(t) < 40 and t.upper() == t:
        return True
    # Common headings
    headings = ["SUMMARY", "EXPERIENCE", "EDUCATION", "CERTIFICATIONS", "PROJECTS", "SKILLS"]
    return any(h in t.upper() for h in headings)


def _normalize_experience(experiences: list) -> list:
    """Simple heuristic normalization for experience entries.

    - Remove entries that look like section headings only.
    - Trim whitespace from titles and descriptions.
    - Deduplicate by title+company signature.
    """
    seen = set()
    out = []
    for exp in experiences:
        title = (exp.get("title") or "").strip()
        company = (exp.get("company") or "").strip()
        desc = (exp.get("description") or "").strip()

        # Drop pure headings
        if _is_section_heading(title) and (not desc or len(desc) < 20):
            continue

        key = (title.lower(), company.lower())
        if key in seen:
            continue
        seen.add(key)

        exp["title"] = title
        exp["company"] = company
        exp["description"] = desc
        out.append(exp)

    return out


def _normalize_skills(skills: list) -> list:
    """Normalize skill strings: strip, title-case multi-word, deduplicate while preserving order."""
    out = []
    seen = set()
    for s in skills:
        if not s:
            continue
        s_clean = re.sub(r"\s+", " ", s).strip()
        # Normalize casing: keep as-is for common all-caps (e.g., SQL, AWS)
        if s_clean.upper() in {"SQL", "AWS", "GCP", "GPU", "CPU", "HTML", "CSS", "API", "REST", "CI/CD"}:
            label = s_clean.upper()
        else:
            # Title case for multi-word tech names, but keep common casing for languages
            label = s_clean
        key = label.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(label)
    return out


def mock_postprocess(parsed: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    """Deterministic normalization pass that mimics an LLM cleaning step.

    It does not call any external API; instead it applies a few heuristics to
    make the parser output more consistent and ready for downstream use.
    """
    try:
        result = dict(parsed)  # shallow copy

        # Normalize personal info name: prefer name if present; else try first line
        pi = result.get("personal_info") or {}
        name = (pi.get("name") or "").strip()
        if not name:
            # try to infer from raw_text first line
            first_line = (raw_text.split("\n")[0] or "").strip()
            if first_line and len(first_line) < 100 and "@" not in first_line:
                pi["name"] = first_line
        result["personal_info"] = pi

        # Normalize experiences
        exps = result.get("experience") or []
        result["experience"] = _normalize_experience(exps)

        # Normalize skills
        skills = result.get("skills") or []
        result["skills"] = _normalize_skills(skills)

        # Add metadata that LLM/postprocess ran
        result["_postprocess"] = {"provider": "mock", "normalized": True}

        return result
    except Exception as e:
        logger.error(f"Mock postprocess failed: {e}")
        # On failure, return original parsed but indicate failure
        parsed["_postprocess"] = {"provider": "mock", "normalized": False, "error": str(e)}
        return parsed


def postprocess(parsed: Dict[str, Any], raw_text: str, mode: str = "mock", **kwargs) -> Dict[str, Any]:
    """Entrypoint to postprocess parsed resume JSON.

    mode: 'mock' (default) applies deterministic heuristics.
    Future modes (e.g., 'openai', 'bedrock') may call external LLMs — not implemented here.
    """
    mode = (mode or "mock").lower()

    if mode == "mock":
        return mock_postprocess(parsed, raw_text)

    if mode == "bedrock":
        # Use AWS Bedrock via boto3. This requires AWS creds with Bedrock access.
        try:
            # Build prompt: include parsed JSON and raw text, ask for normalized JSON output
            prompt = (
                "You are a resume parsing assistant.\n"
                "Input: a partially parsed JSON and the raw resume text.\n"
                "Output: return only valid JSON that conforms to the schema:"
                " {personal_info:{name,email,phone,location,linkedin,github}, experience:[{title,company,start_date,end_date,current,description,skills}], skills:[], education:[]}\n"
                "Here is parsed_json: "
                + json.dumps(parsed)
                + "\nHere is raw_text: "
                + raw_text
                + "\nReturn the normalized JSON only."
            )

            # Configure client with a reasonable timeout
            boto_config = BotoConfig(read_timeout=20, connect_timeout=5, retries={"max_attempts": 2})
            bedrock = boto3.client("bedrock", region_name=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION"))

            model_id = os.getenv("BEDROCK_MODEL_ID") or os.getenv("BEDROCK_MODEL") or "anthropic.claude-3-sonnet-20240229-v1:0"

            # Depending on Bedrock API surface; use invoke_model (or invoke) pattern
            response = bedrock.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({"input": prompt}),
            )

            # Response body may be bytes
            body = response.get("body")
            if isinstance(body, (bytes, bytearray)):
                text = body.decode("utf-8")
            else:
                text = str(body)

            # The model may include extra text; try to extract the first JSON object in the output
            try:
                # Attempt direct load
                normalized = json.loads(text)
            except Exception:
                # Fallback: find JSON substring
                m = re.search(r"\{[\s\S]*\}", text)
                if m:
                    normalized = json.loads(m.group(0))
                else:
                    raise ValueError("No valid JSON returned from Bedrock")

            # Add metadata
            normalized["_postprocess"] = {"provider": "bedrock", "model": model_id, "time": time.time()}
            return normalized

        except Exception as e:
            logger.error(f"Bedrock postprocess failed: {e}")
            # Fallback to mock normalization but annotate the failure
            res = mock_postprocess(parsed, raw_text)
            res["_postprocess"] = {"provider": "bedrock", "normalized": False, "error": str(e)}
            return res

    # Future provider hooks (e.g., openai) go here
    logger.warning(f"LLM postprocess mode '{mode}' not implemented; falling back to mock")
    return mock_postprocess(parsed, raw_text)
