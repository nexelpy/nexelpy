class HeadTagAnalyzer:
    def __init__(self, head):
        self.head = head
        self.result = {}
        self._META_PRIORITY = ["charset", "name", "property", "http-equiv"]
        self._META_STATIC_KEYS = {"charset": "charset"}

        self.dispatcher = {
            "title": self._process_title,
            "meta": self._process_meta,
            "script": self._process_script,
            "link": self._process_link,
        }
        self._default_processor = self._process_unknown

    def _process_title(self, tag):
        self.result["title"] = tag

    def _process_meta(self, tag):
        for attr in self._META_PRIORITY:
            if attr in tag.attribute:
                key = self._META_STATIC_KEYS.get(attr, tag.attribute[attr])
                self.result[key] = tag
                return

    def _process_script(self, tag):
        if "src" in tag.attribute:
            key = tag.attribute["src"]
        else:
            key = tag.text.strip() if tag.text else f"inline_script_{id(tag)}"
        self.result[key] = tag

    def _process_link(self, tag):
        if "href" in tag.attribute:
            self.result[tag.attribute["href"]] = tag

    def _process_unknown(self, tag):
        self.result[f"unknown_{id(tag)}"] = tag

    def analyze(self):
        for child in self.head.children:
            processor = self.dispatcher.get(child.tagName, self._default_processor)
            processor(child)
        self.head.children[:] = list(self.result.values())