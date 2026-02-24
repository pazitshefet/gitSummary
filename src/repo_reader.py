import os
import fnmatch

TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".ini", ".cfg",
    ".js", ".ts", ".tsx", ".jsx", ".sh", ".bat", ".ps1", ".dockerfile"
}

IMPORTANT_GLOBS = [
    "README*", "LICENSE*", "pyproject.toml", "requirements*.txt", "Pipfile*",
    "setup.py", "Dockerfile", "docker-compose.yml", ".env.example",
    "package.json", "Makefile"
]

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "venv", ".venv", "__pycache__",
    "dist", "build", ".tox", ".mypy_cache", ".pytest_cache", ".idea", ".vscode"
}

SKIP_FILE_GLOBS = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.pdf", "*.zip", "*.exe", "*.bin"]

def is_text_file(path: str) -> bool:
    _, ext = os.path.splitext(path.lower())
    if ext in TEXT_EXTENSIONS:
        return True
    # Allow extensionless important files like Dockerfile/Makefile
    base = os.path.basename(path)
    return base in {"Dockerfile", "Makefile"}

def should_skip(path: str) -> bool:
    base = os.path.basename(path)
    for g in SKIP_FILE_GLOBS:
        if fnmatch.fnmatch(base.lower(), g):
            return True
    return False

def collect_files(repo_dir: str):
    important = []
    rest = []

    # First collect root important files (fast win)
    for name in os.listdir(repo_dir):
        p = os.path.join(repo_dir, name)
        if os.path.isfile(p):
            for g in IMPORTANT_GLOBS:
                if fnmatch.fnmatch(name, g):
                    important.append(p)

    # Walk repo
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = os.path.join(root, f)
            if should_skip(p):
                continue
            if not is_text_file(p):
                continue
            if p in important:
                continue
            rest.append(p)

    # Prioritize source folders - lower score is better (earlier)
    def score(p: str) -> int:
        rel = os.path.relpath(p, repo_dir).lower()
        s = 0
        if rel.startswith(("src/", "app/")):
            s += 5
        if "main.py" in rel or "cli" in rel:
            s += 3
        if rel.endswith(".py"):
            s += 2
        return -s

    rest.sort(key=score)
    return important + rest

def read_files(repo_dir: str, files, max_chars_per_file: int, max_total_chars: int):
    collected = []
    total = 0

    for path in files:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(max_chars_per_file)
        except Exception:
            continue

        rel = os.path.relpath(path, repo_dir)
        block = f"\n\n### FILE: {rel}\n{content}\n"
        if total + len(block) > max_total_chars:
            break

        collected.append(block)
        total += len(block)

    return "".join(collected)