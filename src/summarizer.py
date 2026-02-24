import os
import shutil
import tempfile
import subprocess
from openai import OpenAI
from config import settings
from repo_reader import collect_files, read_files

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY", default="")
client = OpenAI(api_key=NEBIUS_API_KEY, base_url="https://api.tokenfactory.nebius.com/v1")

SYSTEM_PROMPT = """You are a senior software engineer.
Summarize the given GitHub repository from the provided files.
Return ONLY valid JSON (no markdown, no code fences, no extra text) with exactly this schema:
{
  "summary": "string",
  "technologies": ["string"],
  "structure": "string"
}
Field requirements:
- "summary": Human-readable summary of what the project does (2-5 sentences, clear and concise).
- "technologies": List the main languages, frameworks, libraries, and tools inferred from the files.
- "structure": Brief human-readable description of the project layout (main folders/files and their roles).
Rules:
- Do not include any keys other than summary, technologies, structure.
- If uncertain, make a reasonable inference from the provided files.
- The JSON must be parseable by json.loads().
"""

def summarize_repo(repo_text: str) -> str:
    resp = client.chat.completions.create(
        model=settings.model,
        temperature=settings.temperature,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": repo_text},
        ],
    )
    return resp.choices[0].message.content

def short_git_error(text: str) -> str:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    if not lines:
        return "git clone failed"

    # Prefer most relevant git lines
    fatal_lines = [l for l in lines if l.lower().startswith("fatal:")]
    if fatal_lines:
        return fatal_lines[-1]

    error_lines = [l for l in lines if l.lower().startswith("error:")]
    if error_lines:
        return error_lines[-1]

    return lines[-1]

def clone_repo(repo_url: str, dest_dir: str):
    # shallow clone
    #Repo.clone_from(repo_url, dest_dir, depth=1)
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"  # fail instead of prompting
    env["GCM_INTERACTIVE"] = "Never"  # helps on Windows Git Credential Manager

    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, dest_dir],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            check=True,
        )
        return True, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Clone timed out (possible auth prompt or network issue)."
    except subprocess.CalledProcessError as e:
        msg = short_git_error((e.stderr or e.stdout or str(e)).strip())
        return False, f"Failed to clone repository {repo_url}. \n System error message: {msg}"

def summarize_url(repo_url: str):
    tmpdir = tempfile.mkdtemp(prefix="repo_sum_")
    repo_dir = os.path.join(tmpdir, "repo")

    try:
        ok, msg = clone_repo(repo_url, repo_dir)
        if not ok:
            raise RuntimeError(msg)

        files = collect_files(repo_dir)
        repo_text = read_files(
            repo_dir,
            files,
            max_chars_per_file=settings.max_chars_per_file,
            max_total_chars=settings.max_total_chars
        )

        summary = summarize_repo(repo_text)
        return summary

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
