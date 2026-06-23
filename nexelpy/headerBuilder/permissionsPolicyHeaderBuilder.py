# class PermissionsPolicyHeaderBuilder:
#     header_name = "Permissions-Policy"

#     __slots__ = ("_directives",)

#     def __init__(self, *directives: str):
#         self._directives = directives

#     def build(self):
#         if not self._directives:
#             return None
#         return ", ".join(self._directives)


class PermissionsPolicyHeaderBuilder:
    __slots__ = ['policies']
    
    def __init__(self):
        self.policies = {}
    
    def add(self, feature, allow_list=None):
        if allow_list is None:
            self.policies[feature] = []
        elif isinstance(allow_list, list):
            self.policies[feature] = allow_list
        else:
            self.policies[feature] = [allow_list]
        return self
    
    def build_header(self):
        if not self.policies:
            return {}
        
        parts = []
        for feature, allow_list in self.policies.items():
            if not allow_list:
                parts.append(f"{feature}=()")
            elif allow_list == ["*"]:
                parts.append(f"{feature}=*")
            else:
                parts.append(f"{feature}=({ ' '.join(allow_list) })")
        
        return {"Permissions-Policy": ", ".join(parts)}