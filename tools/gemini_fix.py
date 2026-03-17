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


def run_gemini(prompt):

    result = subprocess.run(
        ["gemini"],
        input=prompt,
        shell=True,
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
    次のGitHub Issueを修正してください。

    必ず次の形式で出力してください。

    diff形式で変更内容を提示してください。

    例:

    diff --git a/file.py b/file.py
    -print("こんにちは")
    +print("こんばんわ")

    Issue:
    {issue}
    """

    fix = run_gemini(implement_prompt)

    print("\nAI proposed diff:\n")
    print(fix)

    apply = input("\nApply this patch? (yes/no): ")

    if apply.lower() != "yes":
        print("Patch cancelled")
        return

    with open("patch.diff", "w", encoding="utf-8") as f:
        f.write(fix)

    run("git apply patch.diff")

    run("git add .")
    run('git commit -m "AI fix"')

    print("\n📤 Creating Pull Request...\n")

    run("gh pr create --fill")

    print("\n✅ Done")

if __name__ == "__main__":
    main()