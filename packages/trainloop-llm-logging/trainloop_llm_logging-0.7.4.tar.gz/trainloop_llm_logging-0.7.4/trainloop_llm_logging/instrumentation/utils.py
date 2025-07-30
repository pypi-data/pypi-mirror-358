from __future__ import annotations
import inspect
import json
import time
import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse
from ..types import ParsedRequestBody, ParsedResponseBody, LLMCallLocation
from ..logger import create_logger

_log = create_logger("trainloop-instrumentation-utils")

_MAX_BODY = 2 * 1024 * 1024  # 2 MB
DEFAULT_HOST_ALLOWLIST = ["api.openai.com", "api.anthropic.com"]
HEADER_NAME = "X-Trainloop-Tag"


def now_ms() -> int:
    return int(time.time() * 1000)


def cap(b: bytes) -> bytes:
    return b[:_MAX_BODY]


def caller_site() -> LLMCallLocation:
    st = inspect.stack()
    for fr in st[3:]:
        fn = fr.filename
        if "site-packages" in fn or "/lib/" in fn:
            continue
        return {"file": fn, "lineNumber": str(fr.lineno)}
    return {"file": "unknown", "lineNumber": "0"}


def parse_request_body(s: str) -> Optional[ParsedRequestBody]:
    """Parse a request body string into a structured format with messages array.

    Returns:
        A ParsedRequestBody or None if parsing fails
    """
    try:
        body = json.loads(s)
    except Exception:
        return None

    # Handle case where messages are directly provided with model
    if "messages" in body and "model" in body:
        messages = body.get("messages") or []
        model = body.get("model")

        # Use dict comprehension to exclude messages and model
        model_params = {k: v for k, v in body.items() if k not in ["messages", "model"]}

        return {"messages": messages, "model": model, "modelParams": model_params}
    else:
        _log.warning(f"Skipping invalid request body: {s}")
        return None


def parse_response_body(s: str) -> Optional[ParsedResponseBody]:
    """Parse a response body string into a simplified format with just content.

    Returns:
        A ParsedResponseBody or None if parsing fails
    """
    try:
        body = json.loads(s)
    except Exception:
        return None

    if not body:
        return None

    # If it already has content field, return that
    if "content" in body:
        # Just extract the string content regardless of nesting
        if isinstance(body["content"], dict) and "content" in body["content"]:
            return {"content": str(body["content"]["content"])}
        return {"content": str(body["content"])}

    _log.warning(f"Skipping invalid response body: {s}")
    return None


def build_call(**kw) -> Dict[str, Any]:
    kw.setdefault("isLLMRequest", True)
    return kw


def is_llm_call(url: str) -> bool:
    """True if the hostname is in the allow-list."""
    try:
        return urlparse(url).hostname in set(DEFAULT_HOST_ALLOWLIST)
    except Exception:  # pragma: no cover
        return False


def pop_tag(headers: dict) -> str | None:
    """Pop (case-insensitive) X-Trainloop-Tag from a mutable headers mapping."""
    for k in list(headers.keys()):
        if k.lower() == HEADER_NAME.lower():
            return headers.pop(k)
    return None


# --------------------------------------------------------------------------- #
#  Stream-response formatter (OpenAI / Anthropic)                              #
# --------------------------------------------------------------------------- #

_OPENAI_RE = re.compile(r'^data:\s*(\{.*?"choices".*?\})\s*$', re.M)
_ANTHROPIC_RE = re.compile(r'^data:\s*(\{.*?"content_block_delta".*?\})\s*$', re.M)


def format_streamed_content(raw: bytes) -> bytes:
    """
    Collapse an SSE chat stream into a single JSON blob with just the content.
    If parsing fails, return the original bytes.
    """
    text = raw.decode("utf8", errors="ignore")

    # ---- OpenAI ------------------------------------------------------------
    if '"chat.completion.chunk"' in text:
        parts: list[str] = []
        for m in _OPENAI_RE.finditer(text):
            try:
                js = json.loads(m.group(1))
                delta = js["choices"][0]["delta"]
                if "content" in delta:
                    parts.append(delta["content"])
            except Exception:
                pass
        if parts:
            out = {"content": "".join(parts)}
            return json.dumps(out, ensure_ascii=False).encode()

    # ---- Anthropic ---------------------------------------------------------
    if '"content_block_delta"' in text:
        parts: list[str] = []
        for m in _ANTHROPIC_RE.finditer(text):
            try:
                js = json.loads(m.group(1))
                if js["delta"].get("text"):
                    parts.append(js["delta"]["text"])
            except Exception:
                pass
        if parts:
            out = {"content": "".join(parts)}
            return json.dumps(out, ensure_ascii=False).encode()

    return raw  # fallback unchanged
