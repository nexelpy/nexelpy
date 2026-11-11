import inspect
import subprocess
from pathlib import Path
from ..sharedClasses import BasePathControl
from .code_transformer import CodeTransformer
from .runtime_info import RuntimeInfo
from .detector import is_typescript


class Nexcript(BasePathControl):
    def __init__(self, file: str | Path, export_path: str | Path | None = None):
        super().__init__(file)
        self._info = RuntimeInfo()
        self._export_file = self._resolve_export_path(export_path)
        self._code_list: list[dict[str, str]] = []
        self.src = f"/{self._export_file.relative_to(self.project_root).as_posix()}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._export()
        return False

    def raw_script(self, code: str, lang: str | None = None):
        code = inspect.cleandoc(code)
        if lang is None:
            lang = "ts" if is_typescript(code) else "js"
        self._code_list.append({"lang": lang, "code": code})
        return self

    def _resolve_export_path(self, export_path: str | Path | None) -> Path:
        if export_path is None:
            return (self.current_dir / f"{self.file_path.stem}.js").resolve()
        return self._resolve_file_path(export_path)

    def _transpile_ts(self, ts_code: str) -> str:
        if not self._info.can_transpile_ts:
            if not self._info.has_node:
                raise RuntimeError(
                    "Nexcript requires Node.js >= 22.6.0 to compile TypeScript. "
                    "Please install Node.js from nodejs.org."
                )
            else:
                raise RuntimeError(
                    f"Nexcript requires Node.js >= 22.6.0 (found {self._info.node_version}). "
                    "Please upgrade Node.js."
                )

        try:
            proc = subprocess.run(
                [
                    "node",
                    "--experimental-strip-types",
                    "-e",
                    f"console.log(require('module').stripTypeScriptTypes({ts_code!r}))",
                ],
                capture_output=True, text=True, check=True, timeout=10,
            )
            return proc.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"TypeScript compilation failed: {e.stderr.strip() or e.stdout.strip()}"
            )
        except Exception as e:
            raise RuntimeError(f"TypeScript compilation failed: {e}")

    def _render(self) -> str:
        processed_blocks = []
        for item in self._code_list:
            raw_code = item["code"]
            if item["lang"] == "ts":
                raw_code = self._transpile_ts(raw_code)
            transformer = CodeTransformer(
                code=raw_code,
                path_control=self,
                scope_token=self.scope_token,
            )
            processed_blocks.append(transformer.transform())
        return "\n\n".join(processed_blocks)

    def _export(self):
        output_content = self._render()
        self._export_file.parent.mkdir(parents=True, exist_ok=True)
        self._export_file.write_text(output_content, encoding="utf-8")