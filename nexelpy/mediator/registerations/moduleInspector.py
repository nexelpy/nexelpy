import ast
import sys
from pathlib import Path
from rich.console import Console
from datetime import datetime

console = Console()


class ModuleInspector:
    def __init__(self, file: Path, scan_python_file: list):
        self._file = file.resolve() if file else None
        self._root = self._file.parent if self._file else None
        self._scan_python_file = scan_python_file
        self._inspect_python_file = []

    def run(self) -> list:
        self._inspect_python_file = []

        if not self._root:
            console.print("[red]Error: root project not set.[/red]")
            return self._inspect_python_file

        for module_name in self._scan_python_file:
            file_path = self._root / (module_name.replace('.', '/') + '.py')

            if not file_path.exists():
                file_path = self._root / module_name.replace('.', '/') / '__init__.py'

            if not file_path.exists():
                continue

            try:
                source = file_path.read_text(encoding='utf-8')
                tree = ast.parse(source, filename=str(file_path))
            except SyntaxError as e:
                console.print(f"\n[yellow]{datetime.now().strftime('%H:%M:%S')}[/yellow] [bold red](nexelpy Inspector Error):[/bold red]")
                console.print(f"         [blue]module:[/blue] {module_name}")
                console.print(f"         [blue]file:[/blue] {file_path}")
                console.print(f"         [blue]type:[/blue] {e.msg}")
                console.print(f"         [blue]line:[/blue] {e.lineno}")
                if e.text:
                    console.print(f"         [blue]code:[/blue] {e.text.strip()}")
                console.print()
                sys.exit(1)

            found = False
            for node in ast.walk(tree):
                if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue

                for dec in node.decorator_list:
                    decorator_name = self._extract_decorator_name(dec)
                    if decorator_name == 'AutoRegister':
                        self._inspect_python_file.append(module_name)
                        found = True
                        break
                if found:
                    break

        return self._inspect_python_file

    @staticmethod
    def _extract_decorator_name(dec) -> str:

        if isinstance(dec, ast.Name):
            return dec.id
        if isinstance(dec, ast.Attribute):
            return dec.attr
        if isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                return dec.func.id
            if isinstance(dec.func, ast.Attribute):
                return dec.func.attr
        return ''