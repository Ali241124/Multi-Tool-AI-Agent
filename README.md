
# Multi-Tool AI Agent

A Python-based AI agent designed to use multiple tools
to answer questions and perform tasks.

## Current Features

- Calculator tool
- Basic mathematical operations
- Division-by-zero error handling
- Local development with Python

## Technology Stack

- Python
- Ollama (planned LLM integration)
- FastAPI (planned backend)
- Streamlit (planned interface)

## Project Structure

```text
Multi-Tool-AI-Agent/
├── agent/
├── tools/
│   └── calculator.py
├── tests/
├── test_calculator.py
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Multi-Tool-AI-Agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it on Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Run the calculator test

```bash
python test_calculator.py
```

## Roadmap

- [x] Calculator tool
- [ ] Date and time tool
- [ ] Web search tool
- [ ] Weather tool
- [ ] LLM-based tool selection
- [ ] FastAPI backend
- [ ] Chat interface
- [ ] Testing and deployment

## License

MIT
```

We'll update the README as we build the features. The MIT license is currently just a proposed choice; before treating the project as MIT-licensed, create a `LICENSE` file containing the actual MIT license text. If you prefer another license, we can change this later.

## Step 4 — Check that Git is installed

Run this in your VS Code terminal:

```powershell
git --version
```

If you see a version such as `git version 2.x.x`, you're ready.

Next, configure your Git identity if you haven't already:

```powershell
git config --global user.name "Your GitHub Name"
git config --global user.email "YOUR_GITHUB_EMAIL"
```

Replace the placeholders with your preferred commit name and email. You can use GitHub's private `noreply` email if you don't want to expose your personal email in commits.

## Step 5 — Initialize the repository

Run the following commands one at a time:

```powershell
git init
git add .gitignore README.md tools/calculator.py test_calculator.py
git status
```

What they do:

- `git init` creates a local Git repository.
- `git add` stages the selected project files for the first commit.
- `git status` lets you inspect which files are staged.

We're deliberately staging specific files instead of using `git add .` for the first commit. That gives us more control over what gets uploaded.

Check the status carefully. You should see your `.gitignore`, `README.md`, `tools/calculator.py`, and `test_calculator.py` listed as staged files. If a file is missing, check its name and location before proceeding.

## Step 6 — Create the GitHub repository

Open <Link url="https://github.com/new" title="GitHub — Create a new repository"/>.

<box gap={3}>
  <row align="start" gap={3}>
    <AsyncImage query="GitHub new repository create repository form repository name visibility public private screenshot" aspectRatio="4:3" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **Repository name**

      `Multi-Tool-AI-Agent`
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <AsyncImage query="GitHub create a new repository public private repository visibility selection screenshot" aspectRatio="4:3" maxWidth="112px"/>
    <box flex="1" gap={1}>
      **Visibility**

      Choose **Public** if you want recruiters to view the project, or **Private** if you'd prefer to keep it private for now.
    </box>
  </row>
</box>

**Important:** Do not select the options to initialize the repository with a README, `.gitignore`, or license. We've already created our local README and `.gitignore`.

Click **Create repository**. Keep the resulting GitHub page open because we'll need the repository URL.

## Step 7 — Commit your code

Return to PowerShell:

```powershell
git commit -m "Initial commit: calculator tool"
```

A commit is a snapshot of your staged files. As the project develops, we'll make more commits to record meaningful changes.

## Step 8 — Push your project to GitHub

On the new GitHub repository page, copy the HTTPS repository URL. It should look like this:

`https://github.com/YOUR_USERNAME/Multi-Tool-AI-Agent.git`

Then run the following commands, replacing the example URL with your actual URL:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Multi-Tool-AI-Agent.git
git push -u origin main
```

If GitHub requests authentication, follow its browser sign-in flow or use GitHub's supported authentication method. Your normal GitHub account password is not accepted as a Git HTTPS password.

After the push succeeds, refresh the repository page. Your files should appear there.

---

## Buddy, let's do this together

Start with Steps 1–5, then send me the output of:

```powershell
git status
```

I'll check that your files are staged correctly before we commit and upload them. We'll avoid accidentally uploading `.venv` or any secrets.

