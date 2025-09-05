#!/usr/bin/env python3
# intelligent_file_agent.py
# Purpose: Copy matching files (images) from one or more roots to a destination,
#          preserving original folder structure under a per-rule bucket,
#          and write an audit CSV with hashes and metadata.

from __future__ import annotations
import argparse, csv, hashlib, json, logging, os, shutil, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

# ---- DEFAULT (for UNC paths) ----
DEFAULT_ROOTS = [Path(r"C:\Users\Finn\OneDrive\Documents\Masters\Module 4 - IA\Drive")]           # DEFAULT SOURCE FOLDER THAT AGENT WILL CHECK
DEFAULT_DEST  = Path(r"C:\Users\Finn\OneDrive\Documents\Masters\Module 4 - IA\IA_Copy")           # DEFAULT DESTINATION FOR COPIED FILES
DEFAULT_TYPES = "images"                                                                          # IMAGE RULE DEFINED FOR THIS SCENARIO


# ---- Type identification ----
try:
    import magic  # from python-magic or python-magic-bin, uses SHA-256
    HAVE_MAGIC = True
except Exception:
    import mimetypes
    HAVE_MAGIC = False  # fallback option using file extensions


# ---- Optional parsers ----
META_PARSERS: Dict[str, callable] = {}

def register_parser(mime_prefix: str):
    """Decorator to register a metadata parser for a MIME prefix ('image/')."""
    def deco(fn):
        META_PARSERS[mime_prefix] = fn
        return fn
    return deco

# Try to import exifread once, at module level, so it's not a local in the function
try:
    import exifread as _exifread
    HAVE_EXIFREAD = True
except Exception:
    _exifread = None
    HAVE_EXIFREAD = False


@register_parser("image/")
def parse_image_meta(path: Path) -> Dict:
    """ Image metadata parser:
        Extract a few basic image properties and EXIF highlights if present.
      - Always report width/height (via Pillow)
      - Suppress exifread warnings
      - Only attempt EXIF on JPEG/TIFF (where EXIF is expected)
      - Optionally surface PNG info (commented out below)
        """
    try:
        from PIL import Image # pillow to get width/height of image
        import logging

        # If exifread exists, quiet its warnings
        if HAVE_EXIFREAD:
        # this supresses the 'WARNING: PNG file does not have exif data' error message in the terminal.
            logging.getLogger("exifread").setLevel(logging.ERROR)

        with Image.open(path) as im:
            w, h = im.size
            fmt = (im.format or "").upper()  # JPEG, TIFF
            info_dict = dict(im.info) if im.info else {} # PNG as exifread does not support PNG
            
        exif = {}
        if fmt in {"JPEG", "TIFF"} and HAVE_EXIFREAD:
            # Only attempt EXIF on formats that actually carry EXIF
            with open(path, "rb") as fh:
                tags = _exifread.process_file(fh, details=False)
            for k in ("EXIF DateTimeOriginal", "Image Make", "Image Model",
                      "GPS GPSLatitude", "GPS GPSLongitude"):
                if k in tags:
                    exif[k] = str(tags[k])

        # For non-JPEG/TIFF formats, record Pillow info as "extra_info"
        extra_info = {}
        if fmt not in {"JPEG", "TIFF"} and info_dict:
            extra_info = {k: (str(v) if not isinstance(v, (str, int, float, bool)) else v)
                          for k, v in info_dict.items()}

        return {"width": w, "height": h, "format": fmt, "exif": exif, "extra_info": extra_info}

    except Exception as e:
        return {"_parser_error": f"{type(e).__name__}: {e}"}


# ---- Utilities ----
def sha256_file(path: Path, bufsize: int = 1024 * 1024) -> str: # computes SHA-256 hash of the file’s contents in chunks, avoids memory spikes
    """Stream a file and return its SHA-256 hex digest."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(bufsize)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def guess_mime(path: Path) -> Tuple[str, str]:
    """Return (mime, extension) using libmagic if present, else extension guess."""
    if HAVE_MAGIC:
        try:
            m = magic.Magic(mime=True)
            mime = m.from_file(str(path))
            return (mime or "application/octet-stream", path.suffix.lower())
        except Exception:
            pass
    # Fallback to extension-based guess
    mime, _ = mimetypes.guess_type(str(path))
    return (mime or "application/octet-stream", path.suffix.lower())


# ---- Rules (customise here) ----
@dataclass
class RetrievalRule:
    name: str
    mime_startswith: Optional[str] = None       # Using image/ in this scenario
    extensions: Tuple[str, ...] = ()            # safety net alongside MIME
    metadata_contains: Optional[Dict[str, str]] = None  # simple substring checks

    def matches(self, mime: str, ext: str, metadata: Dict) -> bool:
        if self.mime_startswith and not mime.startswith(self.mime_startswith): # if MIME starts with 'image/' it is a match
            return False
        if self.extensions and ext not in self.extensions:  # if file extension is an accepted type
            return False
        if self.metadata_contains:
            blob = json.dumps(metadata, ensure_ascii=False).lower()
            for _, v in self.metadata_contains.items():
                if v.lower() not in blob:
                    return False
        return True

# Image-only rules (MIME and extensions backup)
DEFAULT_RULES = [
    RetrievalRule(
        name="All images",
        mime_startswith="image/", 
        extensions=(
            ".jpg", ".jpeg", ".png", ".PNG", ".gif", ".bmp",
            ".tif", ".tiff", ".webp", ".heic", ".heif"
        ),
    )
]


# ---- Agent ----
@dataclass
class AgentConfig:
    roots: Tuple[Path, ...]
    dest: Path
    rules: Tuple[RetrievalRule, ...] = tuple(DEFAULT_RULES)
    max_workers: int = 8
    dry_run: bool = False
    follow_symlinks: bool = False
    ignore_dirs: Tuple[str, ...] = (
        ".git", "__pycache__", "node_modules",
        "$Recycle.Bin", "System Volume Information"
    )

class FileIntelAgent:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg
        self.dest = cfg.dest
        self.dest.mkdir(parents=True, exist_ok=True)
        self.audit_path = self.dest / f"audit_{int(time.time())}.csv"
        self._setup_audit()

    def _setup_audit(self):
        self.audit_fh = open(self.audit_path, "w", newline="", encoding="utf-8")
        self.audit_csv = csv.DictWriter(self.audit_fh, fieldnames=[
            "time", "rule", "src", "mime", "ext", "sha256", "size", "copied_to", "metadata"
        ])
        self.audit_csv.writeheader()

    def close(self):
        try:
            self.audit_fh.close()
        except Exception:
            pass

    def _iter_files(self):
        for root in self.cfg.roots:
            root = root.resolve()
            for dirpath, dirnames, filenames in os.walk(root, followlinks=self.cfg.follow_symlinks):
                # prune noisy/system dirs
                dirnames[:] = [d for d in dirnames if d not in self.cfg.ignore_dirs]
                for name in filenames:
                    p = Path(dirpath) / name
                    if not p.is_file():
                        continue
                    yield p

    def _process_file(self, path: Path) -> Optional[Dict]: # file walker that steps through the root directory
        try:
            mime, ext = guess_mime(path)

            # parse lightweight metadata if we have a matching parser
            metadata = {}
            for prefix, parser in META_PARSERS.items():
                if mime.startswith(prefix):
                    metadata = parser(path)
                    break

            # hash & size
            sha = sha256_file(path)
            size = path.stat().st_size

            # this is where the agent checks and applies the rules defined earlier on
            for rule in self.cfg.rules:
                if rule.matches(mime, ext, metadata):
                    # preserve original tree under the rule bucket for provenance
                    anchor = path.anchor.strip("\\/") or "ROOT"
                    rel_from_anchor = path.relative_to(path.anchor) if path.anchor else path
                    rel_dest = self.dest / rule.name / anchor / rel_from_anchor

                    copied_to = ""
                    if not self.cfg.dry_run:
                        rel_dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(path, rel_dest)
                        copied_to = str(rel_dest)

                    # audit
                    self.audit_csv.writerow({
                        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "rule": rule.name,
                        "src": str(path),
                        "mime": mime,
                        "ext": ext,
                        "sha256": sha,
                        "size": size,
                        "copied_to": copied_to if not self.cfg.dry_run else "(dry-run)",
                        "metadata": json.dumps(metadata, ensure_ascii=False),
                    })
                    return {"path": str(path), "rule": rule.name, "mime": mime}
            return None
        except Exception as e:
            logging.exception("Error on %s: %s", path, e)
            return None

    def run(self):
        with ThreadPoolExecutor(max_workers=self.cfg.max_workers) as ex:
            futures = [ex.submit(self._process_file, p) for p in self._iter_files()]
            for _ in as_completed(futures):
                pass
        self.close()
        return self.audit_path


# ---- CLI ----
def main():
    ap = argparse.ArgumentParser(description="Intelligent file retrieval agent (images only)")
    ap.add_argument("roots", nargs="+", help="Root directories to scan")
    ap.add_argument("--dest", required=True, help="Destination directory for copied files & audit log")
    ap.add_argument("--dry-run", action="store_true", help="Do not copy, just log decisions")
    ap.add_argument("--workers", type=int, default=8, help="Thread workers (I/O bound)")
    ap.add_argument("--follow-symlinks", action="store_true", help="Follow symlinks/junctions")
    args = ap.parse_args()

    cfg = AgentConfig(
        roots=tuple(Path(r) for r in args.roots),
        dest=Path(args.dest),
        max_workers=args.workers,
        dry_run=args.dry_run,
        follow_symlinks=args.follow_symlinks,
    )
    agent = FileIntelAgent(cfg)
    try:
        audit = agent.run()
        print(f"Audit written to: {audit}")
    finally:
        agent.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())

