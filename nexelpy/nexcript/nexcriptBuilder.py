import inspect
import os
import re
import subprocess
from pathlib import Path
from ..sharedClasses.nextyle_nexcript_path_control import NexetyleNexcriptPathControl
from .code_transformer import CodeTransformer

class Nexcript(NexetyleNexcriptPathControl):
    def __init__(self, file: str | Path, export_path: str | Path | None = None):
        super().__init__(file)
        self.export_file = self._resolve_export_path(export_path)
        self.code_list: list[dict[str, str]] = []
        self.node_exe = self._resolve_node_binary()
        self.rapydscript = self._resolve_rapydscript()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.export()
        return False

    def js(self, code: str):
        self.code_list.append({"lang": "js", "code": inspect.cleandoc(code)})
        return self

    def ts(self, code: str):
        self.code_list.append({"lang": "ts", "code": inspect.cleandoc(code)})
        return self

    def _resolve_export_path(self, export_path: str | Path | None) -> Path:
        if export_path is None:
            return (self.current_dir / f"{self.file_path.stem}.js").resolve()
        return self._resolve_file_path(export_path)

    def _resolve_node_binary(self) -> str:
        pattern = "nodjs/**/node.exe" if os.name == "nt" else "nodjs/**/bin/node"
        candidates = sorted(self.project_root.glob(pattern))
        return str(candidates[0]) if candidates else "node"

    def _resolve_rapydscript(self) -> str:
        pattern = "nodjs/**/rapydscript.cmd" if os.name == "nt" else "nodjs/**/lib/node_modules/rapydscript-ng/bin/rapydscript"
        candidates = sorted(self.project_root.glob(pattern))
        return str(candidates[0]) if candidates else "rapydscript"

    def _transpile_ts(self, ts_code: str) -> str:
        try:
            proc = subprocess.run([self.node_exe, "--experimental-strip-types", "-e", f"console.log(require('module').stripTypeScriptTypes({ts_code!r}))"], capture_output=True, text=True, check=True)
            return proc.stdout.strip()
        except Exception:
            return re.sub(r":\s*(string|number|boolean|any)(\[\])?", "", ts_code)

    def render(self) -> str:
        processed_blocks = []
        for item in self.code_list:
            raw_code = item["code"]
            if item["lang"] == "ts":
                raw_code = self._transpile_ts(raw_code)
            transformer = CodeTransformer(code=raw_code, path_control=self, scope_token=self.scoping_token)
            processed_blocks.append(transformer.transform())
        return "\n\n".join(processed_blocks)

    def export(self):
        output_content = self.render()
        self.export_file.parent.mkdir(parents=True, exist_ok=True)
        self.export_file.write_text(output_content, encoding="utf-8")
