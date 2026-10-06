"""Runtime-only font portability; no production/reference discovery."""
from pathlib import Path
import hashlib
import os
import shutil


def cleared_font():
    """Return an explicitly licensed font and its redistribution notice.

    Overrides must supply both files. A bad override fails rather than silently
    selecting another face. The default is the installed unmodified DejaVu font.
    """
    font = os.environ.get("MOTIF_FONT_PATH")
    license_path = os.environ.get("MOTIF_FONT_LICENSE_PATH")
    if bool(font) != bool(license_path):
        raise ValueError("MOTIF_FONT_PATH and MOTIF_FONT_LICENSE_PATH must be supplied together")
    if font:
        paths = Path(font), Path(license_path)
    else:
        paths = (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
                 Path("/usr/share/doc/fonts-dejavu-core/copyright"))
    if not all(p.is_file() for p in paths):
        raise ValueError("cleared font or license missing; supply both explicit MOTIF_FONT_* paths")
    return paths


def copy_cleared_font(destination):
    destination = Path(destination)
    font, license_path = cleared_font()
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(font, destination)
    notice = destination.with_name(destination.name + ".LICENSE.txt")
    shutil.copyfile(license_path, notice)
    return {"source_font": str(font), "font_sha256": hashlib.sha256(font.read_bytes()).hexdigest(),
            "source_license": str(license_path), "license_sha256": hashlib.sha256(license_path.read_bytes()).hexdigest(),
            "destination_font": str(destination), "destination_license": str(notice)}
