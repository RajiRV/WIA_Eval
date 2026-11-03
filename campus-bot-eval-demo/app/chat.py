"""
Interactive chat with Maple. Use this live during the webinar.

    python app/chat.py            # grounded v2 prompt (default)
    python app/chat.py --prompt v1

After each answer you can rate it: y = thumbs up, n = thumbs down, Enter = skip.
Every message shows up as a trace in Langfuse within a few seconds.
"""

import argparse
import uuid

from maple import add_feedback, ask, flush


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", choices=["v1", "v2"], default="v2")
    args = parser.parse_args()

    session_id = f"live-{uuid.uuid4().hex[:8]}"
    print(f"Maple ({args.prompt} prompt). Type 'quit' to exit. Session: {session_id}\n")

    try:
        while True:
            question = input("You: ").strip()
            if question.lower() in {"quit", "exit", "q"}:
                break
            if not question:
                continue
            answer, trace_id = ask(question, version=args.prompt, user_id="presenter",
                                   session_id=session_id)
            print(f"\nMaple: {answer}\n")
            choice = input("Helpful? [y/n/Enter to skip]: ").strip().lower()
            if choice in {"y", "n"}:
                add_feedback(trace_id, 1 if choice == "y" else 0)
            print()
    finally:
        flush()
        print("Traces sent to Langfuse.")


if __name__ == "__main__":
    main()
