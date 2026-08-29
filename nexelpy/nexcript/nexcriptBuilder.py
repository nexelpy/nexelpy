import os
import tempfile
from inspect import cleandoc
from pathlib import Path
from subprocess import PIPE, run


class Nexcript:
    def __init__(self, file: str, export_path: str = None):
        self.code_list = []
        self.file_path = Path(file).resolve()
        self.export_file = (self.file_path.parent / export_path).resolve() if export_path else self.file_path.with_suffix(".js")
        self.root_dir = Path(__file__).resolve().parent.parent
        self.node_exe = self._resolve_node_binary()
        self.rapydscript = self._resolve_rapydscript()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.export()
        return False

    def _resolve_node_binary(self) -> str:
        candidates = list(self.root_dir.glob("nodjs/**/bin/node"))
        return str(candidates[0]) if candidates else "node"

    def _resolve_rapydscript(self) -> str:
        candidates = list(self.root_dir.glob("nodjs/**/lib/node_modules/rapydscript-ng/bin/rapydscript"))
        return str(candidates[0]) if candidates else "rapydscript"

    def js(self, code: str):
        self.code_list.append({"js": cleandoc(code)})
        return self

    def ts(self, code: str):
        self.code_list.append({"ts": cleandoc(code)})
        return self

    # def py(self, code: str):
    #     self.code_list.append({"py": cleandoc(code)})
    #     return self

    def _transpile_ts(self, ts_code: str) -> str:
        js_script = "const fs=require('fs');const input=fs.readFileSync(0,'utf-8');const stripped=input.replace(/:\\s*\\b(string|number|boolean|any|void|unknown|never|object)\\b/g,'').replace(/interface\\s+[A-Za-z0-9_]+\\s*\\{[^}]*\\}/g,'').replace(/type\\s+[A-Za-z0-9_]+\\s*=[^;]+;/g,'');process.stdout.write(stripped);"
        proc = run([self.node_exe, "--experimental-strip-types", "-e", "const fs=require('fs');const Module=require('node:module');const input=fs.readFileSync(0,'utf-8');process.stdout.write(Module.stripTypeScriptTypes(input));"], input=ts_code, stdout=PIPE, stderr=PIPE, text=True)
        if proc.returncode != 0:
            fallback = run([self.node_exe, "-e", js_script], input=ts_code, stdout=PIPE, stderr=PIPE, text=True)
            return fallback.stdout.strip()
        return proc.stdout.strip()

    # def _transpile_py(self, py_code: str) -> str:
    #     with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False, encoding="utf-8") as f:
    #         f.write(py_code)
    #         temp_path = f.name
    #     try:
    #         cmd = [self.node_exe, self.rapydscript, "-m", "-b", temp_path]
    #         result = run(cmd, stdout=PIPE, stderr=PIPE, text=True)
    #         if result.returncode != 0:
    #             return f"/* RapydScript Error: {result.stderr.strip()} */"
    #         return result.stdout.strip()
    #     finally:
    #         if os.path.exists(temp_path):
    #             os.unlink(temp_path)

    def export(self):
        output_parts = []
        for item in self.code_list:
            if "js" in item:
                output_parts.append(item["js"])
            elif "ts" in item:
                output_parts.append(self._transpile_ts(item["ts"]))
            # elif "py" in item:
            #     output_parts.append(self._transpile_py(item["py"]))
        self.export_file.write_text("\n\n".join(output_parts), encoding="utf-8")
        return self
