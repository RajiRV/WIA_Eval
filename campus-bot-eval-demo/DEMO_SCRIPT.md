# Demo Run of Show (45 minutes)

Have these open before going live:
- **Tab 1:** the slide deck
- **Tab 2:** Promptfoo viewer (http://localhost:15500) with a finished eval loaded
- **Tab 3:** Langfuse project with the dashboard already built and traffic already simulated
- **Terminal:** in the project folder, virtual env active, font size large (18pt+)

---

## 0:00 to 0:03  Hook (slides 1 to 2)
Terminal: `python app/chat.py --prompt v1`

Type: **What's on the cafeteria menu this Friday?**

The v1 bot will usually invent a menu. Read it out. Ask the audience in chat: *"Would you ship this?"* Point out that the facts file has nothing about food, so every dish is made up.

Backup if it happens to answer correctly: ask **Who is the dean of engineering?**

## 0:03 to 0:08  Why evaluation matters (slides 3 to 4)
Slides only. Keep the terminal hidden.

## 0:08 to 0:15  Success metrics (slides 5 to 7)
Switch to `promptfooconfig.yaml` in an editor. Scroll slowly and show:
1. `defaultTest` assertions: **Concise**, **Latency**, **No prompt leak**. "These run on every single answer."
2. One accuracy test (wifi): "A deterministic check. Either the word is there or it isn't."
3. One `llm-rubric` test (cafeteria): "Here another model acts as the judge, using a plain-English rubric."

Poll during slide 7: *"Which metric matters most for a campus chatbot?"*

## 0:15 to 0:24  Testing outputs (slides 8 to 11)
Terminal:
```
npx promptfoo@latest eval --no-cache
```
While it runs (about 1 to 2 minutes), talk through what a test set is. If it is slow or rate limited, stop it and switch to Tab 2 where a finished run is loaded.

In the Promptfoo viewer:
- Point at the **pass rate per column**: v1 vs v2.
- Click a red v1 cell on a Grounding test and show the invented answer plus the judge's reason.
- Use the **metric filter** to show scores per category (Accuracy, Grounding, Safety, Fairness).
- Chat prompt: *"Drop a weird question you'd ask this bot."* Pick one, add it to `promptfooconfig.yaml` live, rerun with `npx promptfoo@latest eval --no-cache --filter-pattern "Your test name"` or simply rerun all if time allows.

Message: *"Every time you change the prompt, rerun this. That's regression testing."*

## 0:24 to 0:31  Monitoring (slides 12 to 14)
Terminal: `python app/chat.py` (v2). Ask two questions, rate one **n**.

Switch to Langfuse:
1. **Tracing** page: open the trace you just made. Show input, output, model, tokens, cost, latency.
2. Show the scores attached automatically: `prompt_leak`, `said_dont_know`, `word_count`, `user_feedback`.
3. **Dashboard**: feedback by prompt version, latency, cost, traces over time.
4. Filter traces by tag `prompt-v1` and score `prompt_leak = 1` if any leaked.

## 0:31 to 0:38  Identifying failures (slides 15 to 17)
Langfuse dashboard: point at the **said_dont_know** spike. Filter traces to see what students asked: all about the new shuttle bus.

Message: *"Monitoring told us what our tests didn't know to ask. Fix: add shuttle info to the facts AND add shuttle questions to the test set."*

Then the fairness slide. Back in the Promptfoo viewer, show the paired Engineering/Nursing tests and the scholarship test side by side.

Optional (if time): show the saved red team report from `npx promptfoo@latest redteam report`.

## 0:38 to 0:43  Q&A
Seed questions if chat is quiet:
- "Can I trust an AI to grade another AI?"
- "How many test cases is enough for a hackathon project?"

## 0:43 to 0:45  Checklist and close (slides 18 to 19)
Share the repo link in chat.

---

## If something breaks
| Problem | Fix |
|---|---|
| `Resource has been exhausted` | Free tier limit hit. Switch to the pre-loaded viewer tab and screenshots. |
| No traces in Langfuse | Check `.env` keys and region URL. Set `LANGFUSE_DEBUG=True` and rerun. |
| v1 bot answers correctly on stage | Normal, LLMs vary. Say so out loud: "this is exactly why one test proves nothing," then show the eval results. |
| Wi-Fi drops | Everything in tabs 2 and 3 is already loaded. Talk through screenshots. |
