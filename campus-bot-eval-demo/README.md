# Maple: AI Evaluation Demo (Promptfoo + Langfuse + Gemini)

Demo for the Women in AI Hackathon webinar on evaluating AI systems.

**Maple** is a help chatbot for a fictional college. The demo shows the full loop:

| Webinar section | Tool | What the audience sees |
|---|---|---|
| Defining success metrics | `promptfooconfig.yaml` | Metrics written as tests: Accuracy, Grounding, Safety, Fairness, Concise, Latency |
| Testing outputs | Promptfoo | v1 (naive prompt) vs v2 (grounded prompt) side by side, red/green results |
| Monitoring behaviour | Langfuse | Live traces, cost, latency, user feedback, automatic checks, dashboards |
| Identifying failures | Both | Hallucinations, prompt leaks, a fairness check, and drift (new topic the bot can't answer) |

```
campus-bot-eval-demo/
├── knowledge/campus_faq.md     # the ONLY facts the bot may use
├── prompts/v1_naive.txt        # weak prompt (fails tests on purpose)
├── prompts/v2_grounded.txt     # improved prompt
├── promptfooconfig.yaml        # 13 test cases + metrics
├── redteam.yaml                # optional: auto-generated attacks
├── app/maple.py                # the chatbot, instrumented with Langfuse
├── app/chat.py                 # interactive chat for the live demo
├── app/simulate_traffic.py     # fills Langfuse with realistic traffic
├── DEMO_SCRIPT.md              # minute-by-minute run of show
└── .env.example
```

## Setup (about 15 minutes, do it the day before)

**You need:** Node.js 20+ and Python 3.10+.

1. **Gemini key.** Go to [Google AI Studio](https://aistudio.google.com), click *Get API key*, create one.
2. **Langfuse account.** Sign up free at [cloud.langfuse.com](https://cloud.langfuse.com), create a project, then *Settings → API Keys → Create*. (Self-hosting with Docker also works, but Cloud is much less to manage for a webinar.)
3. **Keys file.**
   ```bash
   cp .env.example .env    # then paste in your keys
   ```
   If you use an older Langfuse SDK that expects `LANGFUSE_HOST`, add that line too with the same URL.
4. **Python packages.**
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. **Check Promptfoo runs.**
   ```bash
   npx promptfoo@latest eval --no-cache
   npx promptfoo@latest view
   ```
   The viewer opens at http://localhost:15500.
6. **Check Langfuse receives traces.**
   ```bash
   python app/chat.py
   ```
   Ask one question, quit, and confirm a trace appears under *Tracing* in Langfuse.

## Running the demo

```bash
# Testing (Promptfoo)
npx promptfoo@latest eval --no-cache      # run all tests on v1 and v2
npx promptfoo@latest view                 # open the results grid

# Monitoring (Langfuse) - run these BEFORE going live so the dashboard has data
python app/simulate_traffic.py --prompt v1
python app/simulate_traffic.py --prompt v2 --drift

# Live chat on stage
python app/chat.py
python app/chat.py --prompt v1            # show the weak bot failing

# Optional red teaming (run beforehand, show the report live)
npx promptfoo@latest redteam run -c redteam.yaml
npx promptfoo@latest redteam report
```

## Langfuse dashboard to build before the webinar

In Langfuse go to *Dashboards → New dashboard* and add widgets for:

- **Traces over time**, split by tag (`prompt-v1` vs `prompt-v2`)
- **Average `user_feedback`** score, split by tag
- **Average `said_dont_know`** score over time (this spikes when the shuttle drift traffic arrives)
- **Count of `prompt_leak` = 1** (should be 0 for v2)
- **Latency p95** and **total cost**

Optional: under *Evaluators* set up an LLM-as-a-judge evaluator (for example "hallucination") on new traces. It runs on live traffic automatically. It needs a model connection configured in Langfuse, so set it up a day early.

## Changing the model

- Promptfoo: change `google:gemini-3.8-flash` in `promptfooconfig.yaml` and `redteam.yaml`.
- Python app: set `GEMINI_MODEL` in `.env`.

If you hit `Resource has been exhausted`, the free tier rate limit was reached. Raise `delay` in `promptfooconfig.yaml`, use `--delay 4` with the simulator, or switch to `gemini-3.5-flash-lite`.

## Notes

- The college and all facts are made up, so the bot can't "accidentally" be right from training data. That makes hallucinations easy to spot.
- `CANARY-7741` is a fake secret planted in both prompts. Any answer containing it is a prompt leak. This turns a fuzzy security question into a simple yes/no check.
- LLM answers vary between runs. Run the eval 2 or 3 times beforehand and keep screenshots of a good run as a backup.
