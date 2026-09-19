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
        self._export_file = self._resolve_export_path(export_path)
        self._code_list: list[dict[str, str]] = []
        self._node_exe = self._resolve_node_binary()
        self.src = f"/{self._export_file.relative_to(self.project_root).as_posix()}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._export()
        return False

    def raw_script(self, code: str):
        self._code_list.append({"lang": "ts", "code": inspect.cleandoc(code)})
        return self

    def _resolve_export_path(self, export_path: str | Path | None) -> Path:
        if export_path is None:
            return (self.current_dir / f"{self.file_path.stem}.js").resolve()
        return self._resolve_file_path(export_path)

    def _resolve_node_binary(self) -> str:
        nodjs_dir = Path(__file__).resolve().parent.parent / "nodjs"
        pattern = "**/node.exe" if os.name == "nt" else "**/bin/node"
        candidates = sorted(nodjs_dir.glob(pattern))
        return str(candidates[0]) if candidates else "node"



    def _transpile_ts(self, ts_code: str) -> str:
        try:
            proc = subprocess.run([self._node_exe, "--experimental-strip-types", "-e", f"console.log(require('module').stripTypeScriptTypes({ts_code!r}))"], capture_output=True, text=True, check=True)
            return proc.stdout.strip()
        except Exception:
            return re.sub(r":\s*(string|number|boolean|any)(\[\])?", "", ts_code)

    def _render(self) -> str:
        processed_blocks = []
        for item in self._code_list:
            raw_code = item["code"]
            if item["lang"] == "ts":
                raw_code = self._transpile_ts(raw_code)
            transformer = CodeTransformer(code=raw_code, path_control=self, scope_token=self.scoping_token)
            processed_blocks.append(transformer.transform())
        return "\n\n".join(processed_blocks)

    def _export(self):
        output_content = self._render()
        self._export_file.parent.mkdir(parents=True, exist_ok=True)
        self._export_file.write_text(output_content, encoding="utf-8")
