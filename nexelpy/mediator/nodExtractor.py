import platform
import tarfile
import zipfile
from pathlib import Path


class NodeExtractor:
    def __init__(self, path=None):
        self.path = Path(path).resolve() if path else Path(__file__).resolve().parent.parent / "nodjs"

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
        if any(item.is_dir() for item in self.path.iterdir()):
            return
        target_file = self._get_target_file()
        if not target_file:
            return
        if target_file.name.endswith(".zip"):
            with zipfile.ZipFile(target_file, "r") as archive:
                archive.extractall(self.path)
        elif target_file.name.endswith((".tar.gz", ".tar.xz")):
            with tarfile.open(target_file, "r:*") as archive:
                archive.extractall(self.path)
