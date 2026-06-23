class select:
    pass
class event:
    pass
def addClass():
    pass
class check:
    pass
def hassClass():
    pass
def hassAttr():
    pass
class listener:
    pass
class OR:
    pass


s1="div > p.bg-red"
with select(s1):
    with event("click"):
        addClass(s1,"p-5")


s2= "div > p > ul > li"
with check( hasattr(s2,"name"),hassClass(s2,"bg-red")):
    with listener(s2,"click"):
        addClass(s2,"p-5",500,500,"easy","linear")


"""
setText
toggleText
appendText
dependText
getText
isText


getValue

addStyle
removeStyle
toggleStyle
hasStyle

addClass
setClass
toggleClass
removeClass
hasClass

setAttr
toggleAttr
hasAttr
removeAttr

setProp
toggleProp
hasProp
removeProp

appendHtml
dependHtml
setHtml


ajax(url,method,sendData=[],succes=[],error=[])

select("#btn") 
event("click") 
Listener("#btn","click") 
removeListener


check()
"""


