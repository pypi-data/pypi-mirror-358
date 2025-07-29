#!/usr/bin/env python3
import subprocess
import os

OLLAMA_MODEL = "phi3"  # You can change to mistral, gemma, etc.

def get_git_diff():
    try:
        return subprocess.check_output(["git", "diff", "--cached"], stderr=subprocess.DEVNULL).decode("utf-8")
    except subprocess.CalledProcessError:
        print("❌ Error getting git diff.")
        return ""

def run_ollama(prompt):
    try:
        process = subprocess.Popen(
            ["ollama", "run", OLLAMA_MODEL],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(prompt)
        if stderr:
            print(f"⚠️ Ollama error: {stderr.strip()}")
        return stdout.strip()
    except FileNotFoundError:
        print("❌ Ollama not found. Please install it from https://ollama.com")
        return None

def suggest_commit_message(diff, user_hint=None):
    base_prompt = "You are an AI assistant that writes concise Git commit messages."
    if user_hint:
        base_prompt += f"\nThe user wants to focus on: {user_hint}"
    full_prompt = f"""{base_prompt}

Generate a short Git commit message for the following diff:

{diff}

Return only the commit message title (no explanation):"""

    return run_ollama(full_prompt)

def commit_with_message(message):
    subprocess.run(["git", "commit", "-m", message])

def main():
    diff = get_git_diff()
    if not diff.strip():
        print("⚠️ No staged changes found. Use `git add` to stage changes.")
        return

    msg = suggest_commit_message(diff)
    if not msg:
        print("⚠️ Could not generate a commit message.")
        return

    while True:
        print(f"\n💬 Suggested commit message:\n\"{msg}\"\n")
        user_input = input("Use this message? (yes/no): ").strip().lower()
        if user_input in ("yes", "y"):
            commit_with_message(msg)
            print("✅ Commit completed.")
            break
        elif user_input in ("no", "n"):
            hint = input("🔁 Provide a short hint to refine the commit message: ").strip()
            msg = suggest_commit_message(diff, user_hint=hint)
            if not msg:
                print("⚠️ Could not regenerate commit message. Try again.")
                break
        else:
            print("❓ Please respond with 'yes' or 'no'.")

if __name__ == "__main__":
    main()