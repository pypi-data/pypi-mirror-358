import subprocess
import pathlib
import textwrap
import os

def is_ignored(path: str) -> bool:
    """if git already ignores <path> then return true"""
    out = subprocess.run(
        ['git', 'check-ignore', path],
        cwd=pathlib.Path.cwd(),
        capture_output=True
    )
    return out.returncode == 0

def ensure_ignored(path: str) -> None:
    """Append <path> to .gitignore if it is not already ignored."""
    if is_ignored(path):
        return

    gitignore = pathlib.Path('.gitignore')
    if not gitignore.exists():
        gitignore.touch()

    with gitignore.open('a', encoding='utf-8') as gi:
        gi.write(f"\n# secrets - auto-added by lykos\n{path}\n")

    print(f'🔒  Added {path} to .gitignore')

def ensure_report_ignored(report_path: str = ".secrets_report.json") -> None:
    ensure_ignored(report_path) 
