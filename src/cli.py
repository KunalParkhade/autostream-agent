from __future__ import annotations

from src.service import service


def run_cli() -> None:
    session_id = "cli-session"
    print("AutoStream Agent CLI. Type 'exit' to quit.")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Agent: Bye.")
            break

        result = service.chat(session_id=session_id, text=user_input)
        print(f"Agent: {result.get('response', '')}")


if __name__ == "__main__":
    run_cli()
