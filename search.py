from __future__ import annotations

import zipfile
from pathlib import Path
import requests

from minsearch import Index

ZIP_URL = "https://github.com/jlowin/fastmcp/archive/refs/heads/main.zip"

DATA_DIR = Path("data")
MAIN_ZIP = DATA_DIR / "fastmcp-main.zip"


def download_zip_if_needed() -> None:
    """Download the FastMCP repo zip once (skip if already present)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if MAIN_ZIP.exists() and MAIN_ZIP.stat().st_size > 0:
        return

    resp = requests.get(ZIP_URL, timeout=60)
    resp.raise_for_status()
    MAIN_ZIP.write_bytes(resp.content)


def iter_markdown_docs_from_all_zips(zip_dir: Path) -> list[dict]:
    """
    Iterate over all .zip files in zip_dir and load only .md/.mdx files.
    Normalize filenames by dropping the first path component:
      fastmcp-main/docs/getting-started/welcome.mdx -> docs/getting-started/welcome.mdx
    """
    docs: list[dict] = []

    for zip_path in sorted(zip_dir.glob("*.zip")):
        with zipfile.ZipFile(zip_path) as z:
            for name in z.namelist():
                if name.endswith("/"):
                    continue

                lower = name.lower()
                if not (lower.endswith(".md") or lower.endswith(".mdx")):
                    continue

                # Drop the first path component (e.g. "fastmcp-main/")
                parts = name.split("/", 1)
                if len(parts) != 2:
                    continue

                filename = parts[1]
                content = z.read(name).decode("utf-8", errors="ignore")

                docs.append({"filename": filename, "content": content})

    return docs


def build_index(docs: list[dict]) -> Index:
    """
    Build a minsearch index:
      - searchable text: content
      - metadata/keyword: filename
    """
    idx = Index(text_fields=["content"], keyword_fields=["filename"])
    idx.fit(docs)
    return idx


def search(idx: Index, query: str, k: int = 5) -> list[dict]:
    """
    Search wrapper compatible with multiple minsearch versions.

    Common signatures seen:
      search(query, filter_dict=None, boost_dict=None)
      search(query, filter_dict=None, boost_dict=None, num_results=10)
    """
    # First try the newer/extended style (if supported)
    try:
        return idx.search(query, {}, {}, num_results=k)  # type: ignore[arg-type]
    except TypeError:
        # Fallback to positional 4th argument
        try:
            return idx.search(query, {}, {}, k)  # type: ignore[arg-type]
        except TypeError:
            # Oldest style: only (query, filter_dict, boost_dict) => returns default count
            results = idx.search(query, {}, {})  # type: ignore[arg-type]
            return results[:k]


def main() -> None:
    download_zip_if_needed()

    docs = iter_markdown_docs_from_all_zips(DATA_DIR)
    print(f"Loaded {len(docs)} .md/.mdx documents")

    idx = build_index(docs)

    results = search(idx, "demo", k=5)

    print("\nTop 5 results for query='demo':")
    for r in results:
        print("-", r["filename"])

    if results:
        print("\nFIRST:", results[0]["filename"])


if __name__ == "__main__":
    main()
