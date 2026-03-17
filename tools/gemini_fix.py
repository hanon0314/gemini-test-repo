#!/usr/bin/env python3

import subprocess
import json
import sys
import re


# -----------------------------
# utility
# -----------------------------

def run(cmd):

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    return result.stdout.strip()


def run_gemini(prompt):

    cmd = f'gemini "{prompt}"'

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    return result.stdout.strip()


def extract_json(text):

    match = re.search(r"\{.*?\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except:
            return None

    return None


# -----------------------------
# tools
# -----------------------------

def search_code(keyword):

    print("🔎 search_code:", keyword)

    return run(f'git grep "{keyword}"')


def read_file(path):

    print("📄 read_file:", path)

    return run(f"type {path}")


def apply_patch(diff):

    print("🛠 applying patch")

    with open("patch.diff", "w", encoding="utf-8") as f:
        f.write(diff)

    run("git apply patch.diff")

    return "patch applied"


TOOLS = {
    "search_code": search_code,
    "read_file": read_file,
    "apply_patch": apply_patch
}


# -----------------------------
# main agent
# -----------------------------

def main():

    if len(sys.argv) < 2:
        print("Usage: gemini-fix <issue_number>")
        return

    issue_number = sys.argv[1]

    issue_json = run(f"gh issue view {issue_number} --json title,body")
    issue = json.loads(issue_json)

    repo_files = run("git ls-files")

    conversation = f"""
You are an autonomous coding agent.

Respond ONLY in JSON.
No explanation.

Format:

{{"action":"search_code","input":"keyword"}}

or

{{"action":"read_file","input":"path"}}

or

{{"action":"apply_patch","input":"diff"}}

Repository files:

{repo_files}

Issue:

Title: {issue['title']}
Body: {issue['body']}
"""

    for step in range(15):

        print("\n🤖 Agent thinking...\n")

        response = run_gemini(conversation)

        print(response)

        action = extract_json(response)

        if not action:
            print("⚠️ AI response not JSON, retrying...")
            continue

        tool = action.get("action")
        inp = action.get("input")

        if tool not in TOOLS:
            print("⚠️ Unknown tool:", tool)
            continue

        result = TOOLS[tool](inp)

        conversation += f"\nTool result:\n{result}\n"

        if tool == "apply_patch":
            break

    print("\n🌿 Creating branch")

    branch = f"ai-fix-{issue_number}"

    run(f"git checkout -b {branch}")

    run("git add .")

    run(f'git commit -m "AI fix for issue #{issue_number}"')

    run(f"git push origin {branch}")

    print("\n📤 Creating PR")

    run("gh pr create --fill")

    print("\n✅ Done")


if __name__ == "__main__":
    main()