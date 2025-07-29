# 🔥 git-smart-commit

**AI-powered Git commit assistant powered by Ollama (local LLMs)**

`git-smart-commit` helps developers write clear, concise, and contextual commit messages using AI — right from your terminal. It runs entirely offline by leveraging [Ollama](https://ollama.com) to use local large language models like `phi3`, `mistral`, etc.

---

## 🚀 Why Use This?

Writing high-quality Git commit messages is crucial for:

- Understanding **why** a change was made (not just what changed)
- Keeping a **clean, readable Git history**
- Making **code reviews** easier and faster
- Improving **team collaboration** and onboarding

But let’s be honest:  
Most of us settle for “fix”, “update”, or “final changes 😬”.

### 🤖 Enter `git-smart-commit`

This tool scans your staged Git diff and uses a local AI model to generate a meaningful commit message — helping you follow best practices with minimal effort.

---

## 🧠 How It Works

1. You stage changes using `git add`
2. Run `git-smart-commit`
3. It extracts your `git diff --cached`
4. Sends the diff to a local LLM via [Ollama](https://ollama.com)
5. Generates a clear, short commit message
6. You review it:
    - ✅ Accept it
    - ❌ Provide feedback and regenerate
7. It commits using your selected message

---

## 🖥️ Installation

> **Requires Python 3.7+ and [Ollama](https://ollama.com) installed**

### 1. Install the CLI

```bash
pip install git-smart-commit