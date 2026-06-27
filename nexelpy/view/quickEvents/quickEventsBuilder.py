class Block:
    def __init__(self, prefix="", parent_block=None, quick_event=None, is_function=False):
        self.prefix = prefix
        self.parent_block = parent_block
        self._statements = []
        self._quick_event = quick_event
        self.is_function = is_function

    def add_statement(self, code):
        self._statements.append(code)

    def __enter__(self):
        if self._quick_event:
            self._quick_event._current_block = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._quick_event:
            self._quick_event._current_block = self.parent_block

    def export(self, indent=0):
        space = "  " * indent
        if self.prefix:
            result = f"{space}{self.prefix} {{\n"
            for stmt in self._statements:
                if isinstance(stmt, Block):
                    result += stmt.export(indent + 1)
                else:
                    result += f"{space}  {stmt}\n"
            if self.is_function:
                result += f"{space}}})"
            else:
                result += f"{space}}}"
            return result
        else:
            result = ""
            for stmt in self._statements:
                if isinstance(stmt, Block):
                    result += stmt.export(indent)
                else:
                    result += f"{stmt}\n"
            return result


class Condition:
    def __init__(self, *exprs):
        self.groups = []
        if exprs:
            self.groups.append([str(e) for e in exprs])

    def Or(self, *exprs):
        if exprs:
            self.groups.append([str(e) for e in exprs])
        else:
            self.groups.append([])
        return self

    def __str__(self):
        group_strs = []
        for group in self.groups:
            if group:
                group_strs.append(" && ".join(group))
        if not group_strs:
            return ""
        if len(group_strs) == 1:
            return group_strs[0]
        else:
            return "(" + ") || (".join(group_strs) + ")"


class IfBuilder:
    def __init__(self, quick_event, *conditions):
        self.quick_event = quick_event
        self.condition = Condition(*conditions)
        self.block = None

    def Or(self, *conditions):
        self.condition.Or(*conditions)
        return self

    def __enter__(self):
        cond_str = str(self.condition)
        self.block = Block(f"if ({cond_str})", self.quick_event._current_block, self.quick_event)
        self.quick_event._current_block.add_statement(self.block)
        self.quick_event._current_block = self.block
        return self.block

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quick_event._current_block = self.block.parent_block


class ElifBuilder:
    def __init__(self, quick_event, *conditions):
        self.quick_event = quick_event
        self.condition = Condition(*conditions)
        self.block = None

    def Or(self, *conditions):
        self.condition.Or(*conditions)
        return self

    def __enter__(self):
        cond_str = str(self.condition)
        self.block = Block(f"else if ({cond_str})", self.quick_event._current_block, self.quick_event)
        self.quick_event._current_block.add_statement(self.block)
        self.quick_event._current_block = self.block
        return self.block

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quick_event._current_block = self.block.parent_block


class SelectById:
    def __init__(self, const_name, quick_event):
        self.const_name = const_name
        self._quick_event = quick_event

    def _add_statement(self, code):
        self._quick_event._current_block.add_statement(code)

    def addEventListener(self, event):
        new_block = Block(
            prefix=f"{self.const_name}.addEventListener('{event}', function()",
            parent_block=self._quick_event._current_block,
            quick_event=self._quick_event,
            is_function=True
        )
        self._quick_event._current_block.add_statement(new_block)
        return new_block

    def innerText(self, text):
        self._add_statement(f"{self.const_name}.innerText = '{text}';")
        return self

    def addClass(self, class_name):
        self._add_statement(f"{self.const_name}.classList.add('{class_name}');")
        return self

    def removeClass(self, class_name):
        self._add_statement(f"{self.const_name}.classList.remove('{class_name}');")
        return self

    def setAttribute(self, attr, value):
        self._add_statement(f"{self.const_name}.setAttribute('{attr}', '{value}');")
        return self

    def style(self, prop, value):
        self._add_statement(f"{self.const_name}.style.{prop} = '{value}';")
        return self

    def hasClass(self, class_name):
        return f"{self.const_name}.hasClass('{class_name}')"

    def isText(self, text):
        return f"{self.const_name}.isText('{text}')"

    def isVisible(self):
        return f"{self.const_name}.isVisible()"

    def hasAttribute(self, attr):
        return f"{self.const_name}.hasAttribute('{attr}')"


class QuickEvents:
    def __init__(self):
        self._root_block = Block()
        self._current_block = self._root_block
        self._counter = 0

    def _next_const(self):
        self._counter += 1
        return f"el{self._counter}"

    def if_(self, *conditions):
        return IfBuilder(self, *conditions)

    def elif_(self, *conditions):
        return ElifBuilder(self, *conditions)

    def else_(self):
        new_block = Block("else", self._current_block, self)
        self._current_block.add_statement(new_block)
        return new_block

    def selectById(self, id):
        const_name = self._next_const()
        self._current_block.add_statement(f"const {const_name} = document.getElementById('{id}');")
        return SelectById(const_name, self)

    def row_JS(self, code):
        self._current_block.add_statement(code)
        return self

    @property
    def export(self):
        return self._root_block.export(indent=0)



# x = QuickEvent()

# el1 = x.selectById("1")
# el2 = x.selectById("2")


# with x.if_(el1.hasClass("bg-red"), el1.isText("text")).Or(el1.hasClass("bg-blue"), el1.isText("text2")):
#     el2.addClass("active").innerText("Condition met")
# with x.elif_(el1.hasClass("bg-red"), el1.isText("text")).Or(el1.hasClass("bg-blue"), el1.isText("text2")):
#     el2.addClass("active").innerText("Condition met")
# with x.else_():
#     el2.addClass("inactive").innerText("Condition not met")


# with el1.addEventListener("click"):
#     el2.addClass("clicked").innerText("Clicked!")

# print(x.export)