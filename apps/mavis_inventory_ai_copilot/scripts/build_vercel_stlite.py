"""Build the Stlite browser bundle for Vercel static hosting."""

from __future__ import annotations

import re
from pathlib import Path

from stlitepack import pack

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
INDEX_PATH = PUBLIC_DIR / "index.html"


def _collect_embed_files() -> list[str]:
    files: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(("src/", "data/sample/")) and path.suffix in {".py", ".csv"}:
            files.append(rel)
        if rel in {".streamlit/config.toml", ".streamlit/secrets.toml"}:
            files.append(rel)
    return files


def _escape_embedded_python_templates(text: str) -> str:
    """Escape embedded Python blocks so JS template literals preserve source exactly."""

    def _escape_block(match: re.Match[str]) -> str:
        prefix, body, suffix = match.groups()
        body = body.replace("\\", "\\\\")
        body = body.replace("${", "\\${")
        body = body.replace("`", "\\`")
        return prefix + body + suffix

    return re.sub(
        r'("(?:[^"]+\.(?:py|csv|toml))": `\n)([\s\S]*?)(\n            `)',
        _escape_block,
        text,
    )


def _validate_embedded_python(text: str) -> None:
    """Simulate browser JS template evaluation and verify embedded Python compiles."""
    import re as re_mod
    import subprocess
    import tempfile

    pattern = re_mod.compile(r'"(?P<name>[^"]+\.py)": `\n(?P<body>[\s\S]*?)\n            `')
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for match in pattern.finditer(text):
            name = match.group("name")
            raw = match.group("body")
            (tmp_path / "raw.txt").write_text(raw, encoding="utf-8")
            js = """
const fs = require("fs");
const raw = fs.readFileSync("raw.txt", "utf8");
fs.writeFileSync("out.py", `${raw}`);
"""
            (tmp_path / "eval.js").write_text(js, encoding="utf-8")
            subprocess.run(["node", str(tmp_path / "eval.js")], cwd=tmp, check=True, capture_output=True)
            out_file = tmp_path / "out.py"
            result = subprocess.run(
                ["python3", "-m", "py_compile", str(out_file)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"Embedded file failed JS simulation compile: {name}\n{result.stderr}")


def _validate_browser_http_bundle(text: str) -> None:
    """Ensure embedded browser HTTP code cannot call asyncio-based Pyodide networking."""
    match = re.search(r'"src/utils/browser_http.py": `\n([\s\S]*?)\n            `', text)
    if not match:
        raise RuntimeError("Embedded browser_http.py block not found in Stlite bundle.")
    body = match.group(1)
    if "_use_sync_browser_http()" not in body:
        raise RuntimeError("Embedded browser_http.py must route via _use_sync_browser_http().")
    if "_resolve_browser_url" not in body:
        raise RuntimeError("Embedded browser_http.py must resolve relative API URLs.")
    pyodide_match = re.search(r"def _post_json_pyodide[\s\S]*?(?=\n\S|\Z)", body)
    if not pyodide_match:
        raise RuntimeError("Embedded browser_http.py missing _post_json_pyodide().")
    pyodide_body = pyodide_match.group(0)
    forbidden = (
        "asyncio",
        "pyfetch",
        "pyxhr",
        "urlopen",
        "urllib",
    )
    for token in forbidden:
        if token in pyodide_body:
            raise RuntimeError(f"Forbidden token {token!r} in embedded _post_json_pyodide()")


def _patch_loading_screen(text: str) -> str:
    return text.replace(
        '<div id="root"></div>',
        """<div id="root">
      <div style="padding:3rem 1.5rem;font-family:Inter,system-ui,sans-serif;max-width:720px;margin:0 auto;text-align:center;color:#0f172a;">
        <h2 style="margin-bottom:0.75rem;">Loading Inventory Optimization AI Co-Pilot</h2>
        <p style="color:#64748b;line-height:1.6;">Starting the in-browser analytics engine. First load can take 30–60 seconds while Python packages download.</p>
      </div>
    </div>""",
    )


def _patch_mount_error_handler(text: str) -> str:
    marker = 'import { mount } from "https://cdn.jsdelivr.net/npm/@stlite/browser@0.80.5/build/stlite.js";'
    if marker not in text:
        return text
    replacement = marker + """

      function showMountError(error) {
        const root = document.getElementById("root");
        root.innerHTML = [
          '<div style="padding:2rem;font-family:Inter,sans-serif;max-width:960px;margin:0 auto;">',
          '<h2 style="color:#991b1b;">App failed to load</h2>',
          '<p style="color:#475569;">The Streamlit bundle hit a startup error. Details:</p>',
          '<pre style="white-space:pre-wrap;background:#fef2f2;border:1px solid #fecaca;padding:1rem;border-radius:8px;">' + error + '</pre>',
          '</div>',
        ].join('');
        console.error(error);
      }"""
    text = text.replace(marker, replacement, 1)

    old_tail = """document.getElementById("root")
      ).catch((error) => {
        const root = document.getElementById("root");
        root.innerHTML = [
          '<div style="padding:2rem;font-family:Inter,sans-serif;max-width:960px;margin:0 auto;">',
          '<h2 style="color:#991b1b;">App failed to load</h2>',
          '<p style="color:#475569;">The Streamlit bundle hit a startup error. Details:</p>',
          `<pre style="white-space:pre-wrap;background:#fef2f2;border:1px solid #fecaca;padding:1rem;border-radius:8px;">${error}</pre>`,
          '</div>',
        ].join('');
        console.error(error);
      });"""

    new_tail = """document.getElementById("root")
      ).then(
        () => {},
        (error) => showMountError(String(error))
      );"""

    if old_tail in text:
        return text.replace(old_tail, new_tail)

    generic = 'document.getElementById("root")\n      );'
    if generic in text:
        return text.replace(
            generic,
            """document.getElementById("root")
      ).then(
        () => {},
        (error) => showMountError(String(error))
      );""",
        )
    return text


def main() -> None:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    pack(
        "streamlit_app.py",
        extra_files_to_embed=_collect_embed_files(),
        requirements=str(ROOT / "requirements-stlite.txt"),
        title="Inventory Optimization AI Co-Pilot",
        output_dir=str(PUBLIC_DIR),
        output_file="index.html",
        replace_df_with_table=False,
        automated_stlite_fixes=False,
        print_preview_message=False,
        run_preview_server=False,
    )
    text = INDEX_PATH.read_text(encoding="utf-8")
    text = _escape_embedded_python_templates(text)
    _validate_embedded_python(text)
    _validate_browser_http_bundle(text)
    text = _patch_loading_screen(text)
    text = _patch_mount_error_handler(text)
    INDEX_PATH.write_text(text, encoding="utf-8")
    print(f"Stlite app built at {INDEX_PATH}")


if __name__ == "__main__":
    main()
