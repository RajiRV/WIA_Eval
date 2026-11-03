# WIA Eval: Evaluating AI Systems

Materials for the Women in AI Hackathon webinar *How do you know your AI actually works?*

The webinar follows one example chatbot, **Maple**, a help bot for a fictional college. It covers success metrics, testing with Promptfoo, monitoring with Langfuse, and spotting failures such as hallucinations, prompt leaks and bias.

## What's in this repo

| Path | What it is |
|---|---|
| [`campus-bot-eval-demo/`](campus-bot-eval-demo/) | The demo: the Maple chatbot, Promptfoo test suite, Langfuse tracing and a traffic simulator |
| [`campus-bot-eval-demo/README.md`](campus-bot-eval-demo/README.md) | Setup (about 15 minutes) and how to run each part |
| [`campus-bot-eval-demo/DEMO_SCRIPT.md`](campus-bot-eval-demo/DEMO_SCRIPT.md) | Minute-by-minute run of show |

The slide deck is not stored in this repo.

## Quick start

```bash
cd campus-bot-eval-demo
cp .env.example .env          # add your Gemini and Langfuse keys
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python app/chat.py            # talk to Maple (add --prompt v1 for the naive prompt)
npx promptfoo@latest eval --no-cache && npx promptfoo@latest view
```

You need Node.js 20+, Python 3.10+, a free [Gemini API key](https://aistudio.google.com) and a free [Langfuse](https://cloud.langfuse.com) account. Full instructions are in the demo README.

## Notes

- `.env` holds your API keys and is git-ignored. Never commit it.
- The Gemini free tier allows 15 requests per minute. When running `app/simulate_traffic.py`, pass `--delay 6` to avoid rate-limit errors.
