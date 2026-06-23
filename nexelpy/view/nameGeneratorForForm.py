from flask import g

class NameGeneratorByg:
    def __init__(self):
        if not hasattr(g, "pfi_counters"):
            g.pfi_counters = {"p": 0, "f": 0, "i": 0}
        if not hasattr(g, "forms"):
            g.forms = {}
        if not hasattr(g, "inputs"):
            g.inputs = {}

    def generate_plugin(self):
        g.pfi_counters["p"] += 1
        return self

    def generate_form(self, method: str = "POST"):
        g.pfi_counters["f"] += 1
        f_name = f"p{g.pfi_counters['p']}f{g.pfi_counters['f']}"  # p1f1
        g.forms[f_name] = method   # {"p1f1": "POST"}
        return f_name

    def generate_input(self):
        g.pfi_counters["i"] += 1
        pname = g.pfi_counters["p"]
        fname = g.pfi_counters["f"]
        i_name = f"i{g.pfi_counters['i']}"  # i1
        g.inputs[i_name] = f"p{pname}f{fname}"  # {"i1": "p1f1"}
        return i_name

    def generate_handly_input(self,namefromuser):
        pname = g.pfi_counters["p"]
        fname = g.pfi_counters["f"]
        g.inputs[namefromuser] = f"p{pname}f{fname}" # {"mahziar": "p1f1"}
        return namefromuser
    
    def get_method(self, name):
        fname = g.inputs[name]          # "p1f1"
        return g.forms[fname]           #  "POST"