# import importlib
# from . import _Global_nexelpy_var

# class ModuleRunHasDecorator:
#     @staticmethod
#     def run():
#         for module in _Global_nexelpy_var.inspect_python_file:
#             try:
#                 importlib.import_module(module)
#             except Exception as e:
#                 from datetime import datetime
#                 now = datetime.now()
#                 date = now.strftime("%Y-%m-%d")
#                 time = now.strftime("%H:%M:%S")
#                 _Global_nexelpy_var.erorr.append({"class":"ModuleRunHasDecorator","date":date,"time":time,"e":e})



import importlib,traceback,sys
from rich.console import Console
from .. import _Global_nexelpy_var

console = Console()

class ModuleRunHasDecorator:
    @staticmethod
    def run():
        for module in _Global_nexelpy_var.inspect_python_file:
            try:
                importlib.import_module(module)

            except Exception as e:
                from datetime import datetime
                tb = traceback.extract_tb(e.__traceback__)
                last = tb[-1]
                filename = last.filename
                lineno = last.lineno
                code = last.line
                console.print(f"\n[yellow]{datetime.now().strftime('%H:%M:%S')}[/yellow] [bold red](nexelpy RunHasDecorator):[/bold red]")
                console.print(f"         [blue]module:[/blue] {module}")
                console.print(f"         [blue]file:[/blue] {filename}")
                console.print(f"         [blue]type:[/blue]{type(e).__name__}")
                console.print(f"         [blue]erorr:[/blue] {e}")
                console.print(f"         [blue]line:[/blue] {lineno}")
                console.print(f"         [blue]code:[/blue] {code}\n")
                sys.exit(1)