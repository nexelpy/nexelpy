class ParentResolverBase:
    def __init__(self):
        super().__init__()
        self._parent_stack = []

    def get_current_parent(self):
        return self._parent_stack[-1] if self._parent_stack else None

    def default_parent(self):
        return self.elementsContainer

    def setParent(self, parent):
        return parent or self.get_current_parent() or self.default_parent()