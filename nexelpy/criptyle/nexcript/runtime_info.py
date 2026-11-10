import shutil
import subprocess


class RuntimeInfo:
    """Singleton that detects runtime capabilities (Node.js availability, version)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._detect_node()

    def _detect_node(self) -> None:
        self.has_node = shutil.which("node") is not None
        self.node_version = None
        self.node_version_ok = False

        if not self.has_node:
            return

        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.node_version = result.stdout.strip()  # e.g. "v22.6.0"
            parts = self.node_version.lstrip("v").split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            self.node_version_ok = (major > 22) or (major == 22 and minor >= 6)
        except Exception:
            self.node_version_ok = False

    @property
    def can_transpile_ts(self) -> bool:
        """True if Node.js is available and version >= 22.6."""
        return self.has_node and self.node_version_ok