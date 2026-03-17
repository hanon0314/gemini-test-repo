#!/usr/bin/env python3

import subprocess
import sys
import json


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
        "gemini",
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

    issue_json = run(f"gh issue view {issue_number} --json title,body")

    issue = json.loads(issue_json)

    print(issue)

    # ---------------------------
    # repository analysis
    # ---------------------------

    repo_files = run("git ls-files")

    print("\n📂 Repository files\n")
    print(repo_files)

    # ---------------------------
    # search code
    # ---------------------------

    search = run("git grep こんにちは")

    print("\n🔎 Code search results\n")
    print(search)

    # ---------------------------
    # analysis
    # ---------------------------

    print("\n🤖 Gemini analyzing...\n")

    prompt = f"""
あなたはソフトウェアエンジニアです。

GitHub Issue を修正するために
リポジトリを解析してください。

Repository files:

{repo_files}

Code search results:

{search}

Issue:

Title: {issue['title']}
Body: {issue['body']}

以下を日本語で回答してください。

1 Issueの要約
2 原因
3 修正対象ファイル
4 修正方法

まだコードは変更しないでください。
"""

    analysis = run_gemini(prompt)

    print(analysis)

    approval = input("\nこの修正案で実装しますか？ (yes/no): ")

    if approval.lower() != "yes":
        print("❌ Cancelled")
        return

    # ---------------------------
    # implementation
    # ---------------------------

    print("\n🛠 Gemini generating patch...\n")

    implement_prompt = f"""
次のIssueを修正してください。

Repository files:

{repo_files}

Code search results:

{search}

Issue:

Title: {issue['title']}
Body: {issue['body']}

git diff形式で修正を出力してください。

例:

diff --git a/file.py b/file.py
-print("こんにちは")
+print("こんばんわ")
"""

    diff = run_gemini(implement_prompt)

    print("\n📄 Proposed diff\n")
    print(diff)

    apply = input("\nApply this patch? (yes/no): ")

    if apply.lower() != "yes":
        print("❌ Patch cancelled")
        return

    # ---------------------------
    # apply patch
    # ---------------------------

    with open("patch.diff", "w", encoding="utf-8") as f:
        f.write(diff)

    run("git apply patch.diff")

    # ---------------------------
    # commit
    # ---------------------------

    branch = f"ai-fix-{issue_number}"

    run(f"git checkout -b {branch}")
    run("git add .")
    run(f'git commit -m "AI fix for issue #{issue_number}"')

    # ---------------------------
    # push
    # ---------------------------

    run(f"git push origin {branch}")

    # ---------------------------
    # create PR
    # ---------------------------

    run("gh pr create --fill")

    print("\n✅ Done")


if __name__ == "__main__":
    main()