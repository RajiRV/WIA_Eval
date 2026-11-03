"""
Maple: the campus help chatbot, instrumented with Langfuse.

The bot uses the SAME prompt files and facts as the Promptfoo tests, so what you
test before launch is exactly what you monitor after launch.

Every call to ask() creates one Langfuse trace containing:
  - the Gemini call (model, tokens, cost, latency) via OpenTelemetry instrumentation
  - user id, session id, prompt version and tags
  - automatic quality checks attached as scores
"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from langfuse import get_client, observe, propagate_attributes
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
PROMPT_FILES = {
    "v1": ROOT / "prompts" / "v1_naive.txt",
    "v2": ROOT / "prompts" / "v2_grounded.txt",
}
KNOWLEDGE = (ROOT / "knowledge" / "campus_faq.md").read_text(encoding="utf-8")
CANARY = "CANARY-7741"

# Phrases that mean the bot admitted it didn't know (used as a monitoring signal)
DONT_KNOW_PATTERN = re.compile(
    r"(don't|do not|doesn't|does not) have (that|this|any)? ?(information|info|details)"
    r"|not (sure|able to find)|front desk|555-0100",
    re.IGNORECASE,
)

# Send Gemini calls to Langfuse automatically (must run before the client is used)
GoogleGenAIInstrumentor().instrument()
langfuse = get_client()
gemini = genai.Client()  # reads GOOGLE_API_KEY


def build_prompt(question: str, version: str) -> str:
    template = PROMPT_FILES[version].read_text(encoding="utf-8")
    return template.replace("{{knowledge}}", KNOWLEDGE).replace("{{question}}", question)


def run_checks(answer: str) -> dict:
    """Cheap, deterministic checks that run on every live answer."""
    return {
        "prompt_leak": 1 if CANARY.lower() in answer.lower() else 0,
        "said_dont_know": 1 if DONT_KNOW_PATTERN.search(answer) else 0,
        "word_count": len(answer.split()),
    }


@observe(name="maple-chat")
def ask(question: str, version: str = "v2", user_id: str = "demo-user",
        session_id: str = "demo-session", feedback: int | None = None) -> tuple[str, str]:
    """Answer one student question and log everything to Langfuse.

    Returns (answer, trace_id). Keep the trace_id if you want to attach
    user feedback later with add_feedback().
    """
    with propagate_attributes(
        user_id=user_id,
        session_id=session_id,
        version=version,
        tags=["campus-bot", f"prompt-{version}"],
        metadata={"model": MODEL},
    ):
        response = gemini.models.generate_content(
            model=MODEL,
            contents=build_prompt(question, version),
        )
        answer = (response.text or "").strip()

        # Automatic checks become scores you can chart and filter on
        checks = run_checks(answer)
        langfuse.score_current_trace(name="prompt_leak", value=float(checks["prompt_leak"]),
                                     data_type="BOOLEAN")
        langfuse.score_current_trace(name="said_dont_know", value=float(checks["said_dont_know"]),
                                     data_type="BOOLEAN")
        langfuse.score_current_trace(name="word_count", value=float(checks["word_count"]),
                                     data_type="NUMERIC")

        # Thumbs up (1) / thumbs down (0) from the user, if we have it
        if feedback is not None:
            langfuse.score_current_trace(name="user_feedback", value=float(feedback),
                                         data_type="BOOLEAN")
        return answer, langfuse.get_current_trace_id()


def add_feedback(trace_id: str, rating: int, comment: str | None = None):
    """Attach a thumbs up (1) or thumbs down (0) to an earlier answer."""
    langfuse.create_score(name="user_feedback", value=float(rating), trace_id=trace_id,
                          data_type="BOOLEAN", comment=comment)


def flush():
    """Short scripts must flush so traces are sent before the program exits."""
    langfuse.flush()
