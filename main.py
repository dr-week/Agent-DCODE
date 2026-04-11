import sys
from ollama_client import ask_llm
from parser import extract_json
from executor import execute_actions

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your instruction\"")
        return

    user_input = sys.argv[1]
    print(f"\n[INPUT]: {user_input}")

    # 🔁 Retry loop (max 3 tries)
    for attempt in range(3):
        print(f"\n[ATTEMPT {attempt+1}]")

        response = ask_llm(user_input)
        print(f"\n[RAW]:\n{response}")

        data = extract_json(response)

        if data:
            actions = data.get("actions", [])
            print(f"\n[ACTIONS]: {actions}")
            execute_actions(actions)
            return

        print("[RETRYING...]")

    print("[FAILED] Could not get valid JSON")

if __name__ == "__main__":
    main()