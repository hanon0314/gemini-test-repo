#!/usr/bin/env python3

import subprocess
import json
import sys


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

    result = subprocess.run(
        "gemini",
        input=prompt,
        shell=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )

    return result.stdout.strip()


# -----------------------------
# tools
# -----------------------------

def tool_search_code(keyword):

    print("🔎 search_code:", keyword)

    return run(f'git grep "{keyword}"')


def tool_read_file(path):

    print("📄 read_file:", path)

    return run(f"type {path}")


def tool_apply_patch(diff):

    with open("patch.diff", "w", encoding="utf-8") as f:
        f.write(diff)

    run("git apply patch.diff")

    return "patch applied"


TOOLS = {
    "search_code": tool_search_code,
    "read_file": tool_read_file,
    "apply_patch": tool_apply_patch
}


def main():

    if len(sys.argv) < 2:
        print("Usage: gemini-fix <issue_number>")
        return

    issue_number = sys.argv[1]

    issue_json = run(f"gh issue view {issue_number} --json title,body")
    issue = json.loads(issue_json)

    print(issue)

    repo_files = run("git ls-files")

    conversation = f"""
You are an autonomous coding agent.

Repository files:

{repo_files}

Issue:

Title: {issue['title']}
Body: {issue['body']}

Available tools:

search_code(keyword)
read_file(path)
apply_patch(diff)

Respond only in JSON format.

Example:

{{
  "action": "search_code",
  "input": "hello"
}}

If the fix is ready:

{{
  "action": "apply_patch",
  "input": "diff --git ..."
}}

Begin solving the issue.
"""

    for step in range(10):

        print("\n🤖 Agent thinking...\n")

        response = run_gemini(conversation)

        print(response)

        try:
            action = json.loads(response)
        except:
            print("Invalid response")
            return

        tool = action["action"]
        inp = action["input"]

        if tool not in TOOLS:
            print("Unknown tool:", tool)
            return

        result = TOOLS[tool](inp)

        conversation += f"\nTool result:\n{result}\n"

        if tool == "apply_patch":
            break

    print("\n🌿 Creating branch\n")

    branch = f"ai-fix-{issue_number}"

    run(f"git checkout -b {branch}")

    run("git add .")

    run(f'git commit -m "AI fix for issue #{issue_number}"')

    run(f"git push origin {branch}")

    run("gh pr create --fill")

    print("\n✅ Done")


if __name__ == "__main__":
    main()