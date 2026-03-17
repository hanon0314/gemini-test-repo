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

    issue = run(f"gh issue view {issue_number} --json title,body")

    print(issue)

    print("\n🤖 Gemini analyzing...\n")

    prompt = f"""
    あなたはソフトウェアエンジニアです。

    以下のGitHub Issueを読み取り、
    必ず日本語で次の内容を出力してください。

    1. Issueの内容の要約
    2. 問題の原因または要求内容
    3. 修正方法の提案
    4. 変更する可能性があるファイル
    5. 具体的な修正内容

    まだコードは変更しないでください。
    最後に「この修正で実装しますか？」と確認してください。

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