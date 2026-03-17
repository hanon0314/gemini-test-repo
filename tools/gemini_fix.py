#!/usr/bin/env python3

import subprocess
import sys

def run_gemini(prompt):

    result = subprocess.run(
        ["gemini"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )

    return result.stdout.strip()

def main():

    if len(sys.argv) < 2:
        print("Usage: gemini-fix <issue_number>")
        return

    issue_number = sys.argv[1]

    print(f"\n📥 Fetching Issue #{issue_number}\n")

    issue = run(f"gh issue view {issue_number} --json title,body")

    print(issue)

    print("\n🤖 Gemini analyzing...\n")

    prompt = f"""
    あなたはソフトウェアエンジニアです。

    次のGitHub Issueを解析してください。
    必ず日本語で次を説明してください。

    1. Issueの要約
    2. 修正が必要な理由
    3. 修正するファイル
    4. 修正内容の具体例

    コード変更はまだ行わないでください。

    Issue:
    {issue}
    """

    analysis = run_gemini(prompt)

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