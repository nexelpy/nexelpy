
class Importer:

    def __init__(self):
        super().__init__()
        self._css_files: dict[str, dict] = {}
        self._js_files: dict[str, dict] = {}
        self._QE_objects = []
        self._plugin_return_func_data = None


    def import_CSS(self, href, **attr):
        attr["rel"] = "stylesheet"
        self._css_files[href] = attr

    def import_JS(self, src, **attr):
        self._js_files[src] = attr

    def import_style_CDN(self, href, **attr):
        self._css_files[href] = attr

    def import_script_CDN(self, src, **attr):
        self._js_files[src] = attr

    def importPlugin(self, plugin, parent=None):
        PARENT = self.setParent(parent)
        PARENT.children.extend(plugin.elementsContainer.children)
        self._css_files.update(plugin._css_files)
        self._js_files.update(plugin._js_files)
        self._cookies_list.extend(plugin._cookies_list)
        self._QE_objects.append(plugin.QuickEvents)
        return plugin._plugin_return_func_data[0] if len(plugin._plugin_return_func_data) ==1 else plugin._plugin_return_func_data 
    
    def exportAsHTML(self,file):
        content=self.elementsContainer.content
        newfile = file.replace(".py","")
        with open(f"{newfile}.html", "w") as f:
            f.write(content)