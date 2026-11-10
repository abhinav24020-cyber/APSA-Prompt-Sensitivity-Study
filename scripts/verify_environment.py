"""Pre-flight environment verification script.

Checks that all required packages are importable, API keys are set,
and system resources (GPU, disk) are adequate before a long run.

Usage:
    python scripts/verify_environment.py
"""

import importlib
import os
import shutil
import sys
from pathlib import Path

# Load .env file manually (python-dotenv may not be installed)
def _load_dotenv() -> None:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    if key.strip() and key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()


REQUIRED_PACKAGES = [
    ("pydantic", "pydantic"),
    ("yaml", "pyyaml"),
    ("datasets", "datasets"),
    ("click", "click"),
    ("tenacity", "tenacity"),
    ("Levenshtein", "python-Levenshtein"),
    ("nltk", "nltk"),
    ("spacy", "spacy"),
    ("sentence_transformers", "sentence-transformers"),
    ("bert_score", "bert-score"),
    ("rouge_score", "rouge-score"),
    ("scipy", "scipy"),
    ("statsmodels", "statsmodels"),
    ("matplotlib", "matplotlib"),
    ("seaborn", "seaborn"),
    ("plotly", "plotly"),
    ("jinja2", "jinja2"),
    ("rich", "rich"),
]

OPTIONAL_PACKAGES = [
    ("google.generativeai", "google-generativeai", "GEMINI_API_KEY"),
    ("groq", "groq", "GROQ_API_KEY"),
    ("transformers", "transformers", None),
    ("torch", "torch", None),
]

API_KEYS = [
    ("GEMINI_API_KEY", "Google Gemini (free at aistudio.google.com)"),
    ("GROQ_API_KEY", "Groq Cloud (free at console.groq.com)"),
    ("OPENAI_API_KEY", "OpenAI (optional, paid)"),
]

MIN_DISK_GB = 5.0


def check_python_version() -> bool:
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 11)
    status = "[OK]" if ok else "[FAIL]"
    print(f"  {status} Python {major}.{minor} {'(OK)' if ok else '(requires >= 3.11)'}")
    return ok


def check_packages() -> bool:
    all_ok = True
    print("\n[Core packages]")
    for module, pip_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(module)
            print(f"  [OK]   {pip_name}")
        except ImportError:
            print(f"  [MISS] {pip_name}  ->  pip install {pip_name}")
            all_ok = False
    return all_ok


def check_optional_packages() -> None:
    print("\n[Optional packages]")
    for module, pip_name, key in OPTIONAL_PACKAGES:
        try:
            importlib.import_module(module)
            print(f"  [OK]   {pip_name}")
        except ImportError:
            note = f"(needed for {key})" if key else "(for local HuggingFace models)"
            print(f"  [WARN] {pip_name} not installed  {note}")


def check_api_keys() -> bool:
    print("\n[API keys (.env)]")
    any_key = False
    for key, label in API_KEYS:
        value = os.environ.get(key, "")
        if value:
            masked = value[:6] + "..." + value[-4:]
            print(f"  [SET]  {key} = {masked}  ({label})")
            any_key = True
        else:
            optional = "(optional)" if "OPENAI" in key else ""
            print(f"  [WARN] {key} not set  {optional} -- {label}")
    return any_key


def check_disk() -> bool:
    project_root = Path(__file__).parent.parent
    usage = shutil.disk_usage(project_root)
    free_gb = usage.free / (1024 ** 3)
    ok = free_gb >= MIN_DISK_GB
    status = "[OK]  " if ok else "[WARN]"
    print(f"\n[Disk space] {status} {free_gb:.1f} GB free (minimum {MIN_DISK_GB} GB recommended)")
    return ok


def check_gpu() -> None:
    print("\n[GPU]")
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            print(f"  [OK]  CUDA GPU detected: {name} ({vram:.1f} GB VRAM)")
        else:
            print("  [INFO] No CUDA GPU -- will use CPU / API-based models (Gemini, Groq)")
    except ImportError:
        print("  [INFO] torch not installed -- GPU check skipped")


def main() -> None:
    """Run all pre-flight checks and report results."""
    _load_dotenv()

    print("=" * 60)
    print("  APSA - Pre-flight Environment Verification")
    print("=" * 60)

    print("\n[Python version]")
    py_ok = check_python_version()
    pkg_ok = check_packages()
    check_optional_packages()
    key_ok = check_api_keys()
    disk_ok = check_disk()
    check_gpu()

    print("\n" + "=" * 60)
    if py_ok and pkg_ok and key_ok and disk_ok:
        print("ALL CHECKS PASSED -- ready to run experiments!")
    else:
        issues = []
        if not py_ok:
            issues.append("Python version too old")
        if not pkg_ok:
            issues.append("Missing required packages (run pip install -e '.[huggingface,gemini,dev]')")
        if not key_ok:
            issues.append("No API keys set -- edit .env and add GEMINI_API_KEY or GROQ_API_KEY")
        if not disk_ok:
            issues.append(f"Low disk space (< {MIN_DISK_GB} GB free)")
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"   * {issue}")
    print("=" * 60)


if __name__ == "__main__":
    main()

