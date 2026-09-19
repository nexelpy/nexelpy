import platform
import tarfile
import zipfile
from pathlib import Path


class NodeExtractor:
    def __init__(self, path=None):
        self.path = Path(__file__).resolve().parent.parent / "criptyle" / "nodjs"

    def _get_target_file(self):
        os_name = platform.system().lower()
        if "linux" in os_name:
            matches = list(self.path.glob("*linux*.tar.xz"))
            return matches[0] if matches else None
        elif "darwin" in os_name:
            matches = list(self.path.glob("*darwin*.tar.gz"))
            return matches[0] if matches else None
        elif "windows" in os_name:
            matches = list(self.path.glob("*win*.zip"))
            return matches[0] if matches else None
        return None

    def extract_if_needed(self):
        if not self.path.exists():
            return
        if any(item.is_dir() for item in self.path.iterdir()):
            return
        archive_files = [f for f in self.path.iterdir() if f.name.endswith((".tar.xz", ".tar.gz", ".zip"))]
        for archive in archive_files:
            if archive.name.endswith((".tar.xz", ".tar.gz")):
                with tarfile.open(archive, "r:*") as tar:
                    tar.extractall(path=self.path)
            elif archive.name.endswith(".zip"):
                with zipfile.ZipFile(archive, "r") as zip_ref:
                    zip_ref.extractall(path=self.path)