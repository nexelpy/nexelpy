import json, os, platform, shutil, stat, subprocess, sys, tarfile, tempfile, urllib.request, urllib.error, socket, zipfile
from pathlib import Path
from rich.console import Console
from rich.live import Live

console = Console()

class NodeDownloadManager:
    def __init__(self, caller_file: str = __file__):
        self.package_dir = Path(__file__).resolve().parent.parent
        self.base_dir = self.package_dir / "criptyle" / "nodjs"
        self.node_bin = None

    def _detect_platform(self):
        sysname, machine = platform.system(), platform.machine()
        if sysname == "Linux":
            plat = "linux-x64" if machine in ("x86_64", "AMD64") else "linux-arm64" if machine in ("aarch64", "arm64") else None
            ext = "tar.gz"
        elif sysname == "Darwin":
            plat = "darwin-x64" if machine in ("x86_64", "AMD64") else "darwin-arm64" if machine in ("arm64", "aarch64") else None
            ext = "tar.gz"
        elif sysname == "Windows":
            plat = "win-x64" if machine in ("AMD64", "x86_64") else "win-arm64" if machine in ("ARM64", "arm64") else None
            ext = "zip"
        else:
            plat, ext = None, None
        if not plat:
            raise RuntimeError(f"unsupported OS/architecture: {sysname} {machine}")
        return plat, ext

    def _fetch_latest_version(self):
        req = urllib.request.Request("https://nodejs.org/dist/index.json", headers={"User-Agent": "Nexelpy"})
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read().decode())[0]["version"]

    def _find_isolated_binary(self):
        if not self.base_dir.exists():
            return None
        patterns = ["node-v*-*/bin/node", "node-v*-*/node.exe", "bin/node", "node.exe"]
        for pattern in patterns:
            found = list(self.base_dir.glob(pattern))
            if found and os.access(found[0], os.X_OK):
                return str(found[0])
        return None

    def _download_archive(self, url: str, dest: Path, live: Live):
        def hook(blocks, block_size, total_size):
            downloaded = blocks * block_size
            percent = f"{(downloaded / total_size * 100):.1f}%" if total_size > 0 else f"{downloaded / (1024 * 1024):.1f}MB"
            live.update(f"[bold][NexelPy nodjs manager][/bold] [blue]downloading nodjs... {percent}[/blue]")
        urllib.request.urlretrieve(url, dest, reporthook=hook)

    def _extract_archive(self, archive_path: Path):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        if str(archive_path).endswith(".zip"):
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(self.base_dir)
        else:
            with tarfile.open(archive_path, "r:*") as tf:
                tf.extractall(self.base_dir)

    def _test_binary(self, bin_path: str):
        ts_code = "const greet = (name: string): string => `hello ${name}`; console.log(greet('nexelpy'));"
        test_script = (
            "try {"
            "  const ts = require('typescript');"
            "  const out = ts.transpileModule(process.argv[1], { compilerOptions: { module: ts.ModuleKind.CommonJS } });"
            "  console.log(out.outputText.trim());"
            "} catch (e) {"
            "  const stripped = process.argv[1].replace(/:\s*[a-zA-Z0-9_<>[\]]+/g, '');"
            "  console.log(stripped.trim());"
            "}"
        )
        test_cmd = [bin_path, "-e", test_script, ts_code]
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0 or "nexelpy" not in result.stdout or ": string" in result.stdout:
            raise RuntimeError(result.stderr.strip() or "typescript compilation test failed")

    def _format_error(self, e: Exception) -> str:
        if isinstance(e, urllib.error.URLError):
            if isinstance(e.reason, socket.gaierror):
                return "connection failed: no internet connection or DNS error"
            if isinstance(e.reason, socket.timeout) or isinstance(e.reason, TimeoutError):
                return "connection timed out"
            return f"network error: {e.reason}"
        if isinstance(e, socket.timeout) or isinstance(e, TimeoutError):
            return "connection timed out"
        return str(e)

    def ensure_node(self) -> str:
        existing_bin = self._find_isolated_binary()
        if existing_bin:
            self._test_binary(existing_bin)
            console.print("[bold][NexelPy nodjs manager][/bold] [blue] nodjs ready to use[/blue]")
            self.node_bin = existing_bin
            return self.node_bin
        temp_archive = None
        with Live(console=console, refresh_per_second=10) as live:
            try:
                live.update("[bold][NexelPy nodjs manager][/bold] [blue]resolving node version ...[/blue]")
                plat, ext = self._detect_platform()
                version = self._fetch_latest_version()
                url = f"https://nodejs.org/dist/{version}/node-{version}-{plat}.{ext}"
                temp_archive = Path(tempfile.gettempdir()) / f"nexel_node_{version}_{plat}.{ext}"
                live.update(f"[bold][NexelPy nodjs manager][/bold] [blue]downloading {version} ...[/blue]")
                self._download_archive(url, temp_archive, live)
                live.update("[bold][NexelPy nodjs manager][/bold] [blue]extracting archive ...[/blue]")
                self._extract_archive(temp_archive)
                extracted_bin = self._find_isolated_binary()
                if not extracted_bin:
                    raise RuntimeError("node binary not found after extraction")
                os.chmod(extracted_bin, os.stat(extracted_bin).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                live.update("[bold][NexelPy nodjs manager][/bold] [blue]testing extracted binary ...[/blue]")
                self._test_binary(extracted_bin)
                live.update(f"[bold][NexelPy nodjs manager][/bold] [green] nodjs ready to use version({version}) ✓[/green]")
                self.node_bin = extracted_bin
                return self.node_bin
            except Exception as e:
                err_msg = self._format_error(e)
                live.update(f"[bold][NexelPy nodjs manager][/bold] [red] ({err_msg})[/red]")
                sys.exit(1)
            finally:
                if temp_archive and temp_archive.exists():
                    temp_archive.unlink(missing_ok=True)
