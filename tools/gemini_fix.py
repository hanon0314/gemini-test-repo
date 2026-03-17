#!/usr/bin/env python3

import subprocess
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
    return result.stdout.strip() if result.stdout else ""

def main():

    if len(sys.argv) < 2:
        print("Usage: gemini-fix <issue_number>")
        return

    issue_number = sys.argv[1]

    print(f"\n📥 Fetching Issue #{issue_number}\n")

    issue = run(f"gh issue view {issue_number}")

    print(issue)

    print("\n🤖 Gemini analyzing...\n")

    prompt = f"""
Read the GitHub issue.

1. Explain requirement
2. Identify root cause
3. Propose fix
4. Ask for approval
Do NOT implement yet.

Issue:

{issue}
"""

    analysis = run(f'gemini "{prompt}"')

    print(analysis)

    approval = input("\nApprove implementation? (yes/no): ")

    if approval.lower() != "yes":
        print("Cancelled")
        return

    print("\n🛠 Implementing fix...\n")

    implement_prompt = f"""
Implement the fix.

Steps:
1. Create branch
2. Implement change
3. Commit changes
"""

    run(f'gemini "{implement_prompt}"')

    print("\n📤 Creating Pull Request...\n")

    run("gh pr create --fill")

    print("\n✅ Done")

if __name__ == "__main__":
    main()