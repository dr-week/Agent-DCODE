import json
import re

def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None

        content = match.group(0)

        # 🔥 Fix Windows backslashes properly
        content = content.replace("\\", "\\\\")

        return json.loads(content)

    except Exception as e:
        print("[PARSER ERROR]", e)
        return None