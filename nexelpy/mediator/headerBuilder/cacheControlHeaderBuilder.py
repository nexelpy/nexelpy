# class CacheControlHeaderBuilder:

#     header_name = "Cache-Control"

#     def __init__(self,cache_control="no-cache",max_age=31536000,s_maxage=None,stale_while_revalidate=None,stale_if_error=None,extra=""):
#         parts = [
#             cache_control,
#             f"max-age={max_age}",
#             f"s-maxage={s_maxage}" if s_maxage else "",
#             f"stale-while-revalidate={stale_while_revalidate}" if stale_while_revalidate else "",
#             f"stale-if-error={stale_if_error}" if stale_if_error else "",
#             extra
#         ]

#         self._value = ", ".join(p for p in parts if p)

#     def build(self):
#         return self._value
    

class CacheControlHeaderBuilder:
    __slots__ = ['parts'] 
    
    def __init__(self, cache_control="no-cache", max_age=31536000, s_maxage="", stale_while_revalidate="", stale_if_error="", extra=""):
        self.parts = list(filter(None, [ cache_control,
            f"max-age={max_age}" if max_age else "",
            f"s-maxage={s_maxage}" if s_maxage else "",
            f"stale-while-revalidate={stale_while_revalidate}" if stale_while_revalidate else "",
            f"stale-if-error={stale_if_error}" if stale_if_error else "",
            extra ]))

    def build_header(self):
        return {"Cache-Control": ", ".join(self.parts) if self.parts else "no-cache"}
    


