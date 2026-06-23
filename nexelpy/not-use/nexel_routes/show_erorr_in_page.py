from ..view import pageBuilder
from datetime import datetime


async def show_errrr(errrr):
    x = pageBuilder.PageBilder()
    x.BODY.attribute["style"]="background-color:rgb(20, 20, 20);color:white;"
    x.h2("nexelpy erorr",style="background-color:red;color:white;padding:1.5rem;margin:1rem 2rem;")
    for i in errrr:
        x.h3(f"{i} : {errrr[i]}",style="margin:1rem 2rem;")

    
    return x.RESPONSE()