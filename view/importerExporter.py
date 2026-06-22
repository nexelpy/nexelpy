
class Importer:

    def __init__(self):
        super().__init__()
        self._css_files = []
        self._js_files = []
        self._plugin_return_func_data = None


    def import_CSS(self, href, **attr):
        attr["rel"] = "stylesheet"
        self._css_files.append((href, attr))

    def import_JS(self, src, **attr):
        self._js_files.append((src, attr))

    def import_style_CDN(self, href, **attr):
        self._css_files.append((href, attr))

    def import_script_CDN(self, src, **attr):
        self._js_files.append((src, attr))

    def importPlugin(self, plugin, parent=None):
        PARENT = self.setParent(parent)
        PARENT.children.extend(plugin.elementsContainer.children)
        self._css_files.extend(plugin._css_files)
        self._js_files.extend(plugin._js_files)
        self._cookies_list.extend(plugin._cookies_list)
        return plugin._plugin_return_func_data[0] if len(plugin._plugin_return_func_data) ==1 else plugin._plugin_return_func_data 