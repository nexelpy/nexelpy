# import ast
# from pathlib import Path
# from . import _Global_nexelpy_var

# class ModuleInspector:
#     @staticmethod
#     def run():  
#         root = Path(_Global_nexelpy_var.root_progect).resolve().parent
#         _Global_nexelpy_var.inspect_python_file = []

#         for module_name in _Global_nexelpy_var.scan_python_file:
#             file_path = root / (module_name.replace(".", "/") + ".py")
            
#             if not file_path.exists():
#                 file_path = root / module_name.replace(".", "/") / "__init__.py"
            
#             if not file_path.exists():
#                 continue

#             try:
#                 tree = ast.parse(file_path.read_text(encoding="utf-8"))
#                 for node in tree.body:
#                     if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
#                         continue

#                     for dec in node.decorator_list:
#                         decorator_name = ""
#                         if isinstance(dec, ast.Call):
#                             if isinstance(dec.func, ast.Name):
#                                 decorator_name = dec.func.id
#                             elif isinstance(dec.func, ast.Attribute):
#                                 decorator_name = dec.func.attr
#                         elif isinstance(dec, ast.Name):
#                             decorator_name = dec.id
                        
#                         if decorator_name == "AutoRegister":
#                             if module_name not in _Global_nexelpy_var.inspect_python_file:
#                                 _Global_nexelpy_var.inspect_python_file.append(module_name)
#                             break

#             except Exception as e:
#                 from datetime import datetime
#                 now = datetime.now()
#                 date = now.strftime("%Y-%m-%d")
#                 time = now.strftime("%H:%M:%S")
#                 _Global_nexelpy_var.erorr.append({"class":"ModuleInspector","date":date,"time":time,"e":e})



import ast
import sys
from pathlib import Path
from .. import _Global_nexelpy_var
from rich.console import Console

console = Console()

class ModuleInspector:
    @staticmethod
    def run():
        root = Path(_Global_nexelpy_var.root_progect).resolve().parent
        _Global_nexelpy_var.inspect_python_file = []

        for module_name in _Global_nexelpy_var.scan_python_file:
            file_path = root / (module_name.replace(".", "/") + ".py")

            if not file_path.exists():
                file_path = root / module_name.replace(".", "/") / "__init__.py"

            if not file_path.exists():
                continue

            try:
                source = file_path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(file_path))

            except SyntaxError as e:
                from datetime import datetime
                console.print(f"\n[yellow]{datetime.now().strftime('%H:%M:%S')}[/yellow] [bold red](nexelpy Inspector Error):[/bold red]")
                console.print(f"         [blue]module:[/blue] {module_name}")
                console.print(f"         [blue]file:[/blue] {file_path}")
                console.print(f"         [blue]type:[/blue]{e.msg}")
                console.print(f"         [blue]line:[/blue] {e.lineno}")
                line = f"{e.text.strip()}" if e.text else ""
                console.print(f"         [blue]code:[/blue] {line}\n")
                sys.exit(1)

            for node in tree.body:
                if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue

                for dec in node.decorator_list:
                    decorator_name = ""

                    if isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Name):
                            decorator_name = dec.func.id
                        elif isinstance(dec.func, ast.Attribute):
                            decorator_name = dec.func.attr

                    elif isinstance(dec, ast.Name):
                        decorator_name = dec.id

                    if decorator_name == "AutoRegister":
                        if module_name not in _Global_nexelpy_var.inspect_python_file:
                            _Global_nexelpy_var.inspect_python_file.append(module_name)
                        break
