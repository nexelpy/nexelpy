from ..view import pageBuilder
from ..mediator import _Global_nexelpy_var


async def nexelpy_home():
    x = pageBuilder.PageBilder()
    x.p(f"root_progect : {_Global_nexelpy_var.root_progect}")
    x.p(f"dev_Mode : {_Global_nexelpy_var.dev_Mode}")
    x.p(f"python file in your project : {len(_Global_nexelpy_var.scan_python_file)}")
    x.p(f"inspect : {_Global_nexelpy_var.inspect_python_file}")

    
    for i in _Global_nexelpy_var.AutoRegister_list:
        with x.ul(style="border-style:solid;border-color:blue;display:inline-block;padding-right:1rem;border-radius:1rem;color:blue;margin:1rem;",text="route"):
            for j in i:
                x.li(f"{j} : {i[j]}",style="color:black;")

    x.br()
    for erorrs in _Global_nexelpy_var.erorr:
        with x.ul(style="border-style:solid;border-color:red;display:inline-block;padding-right:1rem;border-radius:1rem;color:red;margin:1rem;",text="erorr"):
            for erorr in erorrs:
                x.li(f"{erorr} : {erorrs[erorr]}",style="color:black;")
    return x.RESPONSE()