from .cspHeaderBuilder import CSPHeaderBuilder
from .hstsHeaderBuilder import HSTSHeaderBuilder
from .cacheControlHeaderBuilder import CacheControlHeaderBuilder
from .xFrameOptionsHeaderBuilder import XFrameOptionsHeaderBuilder
from .xContentTypeOptionsHeaderBuilder import XContentTypeOptionsHeaderBuilder
from .referrerPolicyHeaderBuilder import ReferrerPolicyHeaderBuilder
from .permissionsPolicyHeaderBuilder import PermissionsPolicyHeaderBuilder
from .crossOriginOpenerPolicyHeaderBuilder import CrossOriginOpenerPolicyHeaderBuilder
from .crossOriginEmbedderPolicyHeaderBuilder import CrossOriginEmbedderPolicyHeaderBuilder
from .crossOriginResourcePolicyHeaderBuilder import CrossOriginResourcePolicyHeaderBuilder
from .originAgentClusterHeaderBuilder import OriginAgentClusterHeaderBuilder
from .clearSiteDataHeaderBuilder import ClearSiteDataHeaderBuilder

class HeaderBuilder:
    def __init__(self):
        self._final_header = {}
        self._obj_classes = []

        self.csp = CSPHeaderBuilder()
        self._obj_classes.append(self.csp)

        self.permissions_Policy = PermissionsPolicyHeaderBuilder()
        self._obj_classes.append(self.permissions_Policy)

        self._raw_headers = {}

    def hsts(self, max_age=31536000, include_subdomains=True, preload=False):
        hsts = HSTSHeaderBuilder(max_age, include_subdomains, preload)
        self._obj_classes.append(hsts)
        return hsts
    
    def cache(self, cache_control="no-cache", max_age=31536000, s_maxage="", stale_while_revalidate="", stale_if_error="", extra=""):
        cash = CacheControlHeaderBuilder(cache_control,max_age,s_maxage,stale_while_revalidate,stale_if_error,extra)
        self._obj_classes.append(cash)
        return cash
    
    def frame_options(self, policy="DENY"):
        frame_options = XFrameOptionsHeaderBuilder(policy)
        self._obj_classes.append(frame_options)
        return frame_options
    
    def content_type_options(self):
        content_type_options = XContentTypeOptionsHeaderBuilder()
        self._obj_classes.append(content_type_options)
        return content_type_options
    
    def referrer_Policy(self, policy="strict-origin-when-cross-origin"):
        referrerPolicy = ReferrerPolicyHeaderBuilder(policy=policy)
        self._obj_classes.append(referrerPolicy)
        return referrerPolicy

    def cross_origin_opener(self, policy="same-origin"):
        coop = CrossOriginOpenerPolicyHeaderBuilder(policy)
        self._obj_classes.append(coop)
        return coop

    def cross_origin_embedder(self, policy="require-corp"):
        coep = CrossOriginEmbedderPolicyHeaderBuilder(policy)
        self._obj_classes.append(coep)
        return coep

    def cross_origin_resource(self, policy="same-origin"):
        cor = CrossOriginResourcePolicyHeaderBuilder(policy)
        self._obj_classes.append(cor)
        return cor

    def origin_agent_cluster(self):
        oac = OriginAgentClusterHeaderBuilder()
        self._obj_classes.append(oac)
        return oac

    def clear_site_data(self, *types):
        csd = ClearSiteDataHeaderBuilder(*types)
        self._obj_classes.append(csd)
        return csd

    def add_raw_header(self, **headers):
        for key, value in headers.items():
            self._raw_headers[key.replace('_', '-').replace("__","-")] = value
        return self
    
    def build_header(self):
        self._final_header = {}
        for builder in self._obj_classes:
            self._final_header.update(builder.build_header())
        return self._final_header
    
    def set_super_strict(self):
        self.add_raw_header(
            Content_Security_Policy="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
            Strict_Transport_Security="max-age=31536000; includeSubDomains; preload",
            Cache_Control="no-store, no-cache, must-revalidate, private",
            X_Frame_Options="DENY",
            X_Content_Type_Options="nosniff",
            Referrer_Policy="no-referrer",
            Permissions_Policy="geolocation=(), camera=(), microphone=(), usb=(), payment=(), encrypted-media=(), speaker=(), autoplay=()",
            Cross_Origin_Opener_Policy="same-origin",
            Cross_Origin_Embedder_Policy="require-corp",
            Cross_Origin_Resource_Policy="same-origin",
            Origin_Agent_Cluster="?1",)
        return self

    def set_strict(self):
        self.add_raw_header(
            Content_Security_Policy="default-src 'self'; script-src 'self' https:; style-src 'self' https:; img-src 'self' data: https:; connect-src 'self' https:; frame-ancestors 'self'; base-uri 'self'; form-action 'self'",
            Strict_Transport_Security="max-age=31536000; includeSubDomains; preload",
            Cache_Control="no-cache, no-store, must-revalidate",
            X_Frame_Options="SAMEORIGIN",
            X_Content_Type_Options="nosniff",
            Referrer_Policy="strict-origin-when-cross-origin",
            Permissions_Policy="geolocation=(self), camera=(), microphone=(), usb=(), payment=(), autoplay=(self)",
            Cross_Origin_Opener_Policy="same-origin",
            Cross_Origin_Embedder_Policy="require-corp",
            Cross_Origin_Resource_Policy="same-origin",
            Origin_Agent_Cluster="?1")
        return self

    def set_normal(self):
        self.add_raw_header(
            Content_Security_Policy="default-src 'self' https:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; connect-src 'self' https:; frame-ancestors 'self'; base-uri 'self'",
            Strict_Transport_Security="max-age=31536000; includeSubDomains",
            Cache_Control="public, max-age=86400",
            X_Frame_Options="SAMEORIGIN",
            X_Content_Type_Options="nosniff",
            Referrer_Policy="strict-origin-when-cross-origin",
            Permissions_Policy="geolocation=(self), autoplay=(*)",
            Cross_Origin_Opener_Policy="same-origin-allow-popups",
            Cross_Origin_Resource_Policy="cross-origin",
            Origin_Agent_Cluster="?1")
        return self

    def set_relaxed(self):
        self.add_raw_header(
            Content_Security_Policy="default-src *; script-src * 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline'; img-src * data:; connect-src *; frame-ancestors *; base-uri *",
            Strict_Transport_Security="max-age=86400",
            Cache_Control="public, max-age=31536000, immutable",
            X_Frame_Options="SAMEORIGIN",
            X_Content_Type_Options="nosniff",
            Referrer_Policy="unsafe-url",
            Permissions_Policy="*",
            Cross_Origin_Opener_Policy="unsafe-none",
            Cross_Origin_Embedder_Policy="unsafe-none",
            Cross_Origin_Resource_Policy="cross-origin",
            Origin_Agent_Cluster="?0")
        return self

    def build_header(self):
        self._final_header = {}
        
        for builder in self._obj_classes:
            self._final_header.update(builder.build_header())
        
        self._final_header.update(self._raw_headers)
        
        return self._final_header







# headers = HeaderBuilder()

# # CSP
# headers.csp.add('default-src', "'self'")
# headers.csp.add('script-src', "'self'", "https://example.com")

# # HSTS
# headers.hsts(max_age=31536000, include_subdomains=True, preload=True)

# # Cache-Control
# headers.cache(cache_control="public", max_age=31536000)

# # X-Frame-Options
# headers.frame_options(policy="DENY")

# # X-Content-Type-Options
# headers.content_type_options()

# # Referrer-Policy
# headers.referrer_Policy()

# # Permissions-Policy
# headers.permissions_Policy.add('geolocation', 'self')
# headers.permissions_Policy.add('camera')
# headers.permissions_Policy.add('microphone')
# headers.permissions_Policy.add('autoplay', '*')

# # Cross-Origin-Opener-Policy
# headers.cross_origin_opener(policy="same-origin")

# # Cross-Origin-Embedder-Policy
# headers.cross_origin_embedder(policy="require-corp")

# # Cross-Origin-Resource-Policy
# headers.cross_origin_resource(policy="same-origin")

# # Origin-Agent-Cluster
# headers.origin_agent_cluster()

# # Clear-Site-Data - پاک کردن کوکی‌ها و کش
# headers.clear_site_data('cookies', 'cache')

# result = headers.build_header()
# print(result)
# # {
# #   'Content-Security-Policy': "...",
# #   'Strict-Transport-Security': '...',
# #   'Cache-Control': '...',
# #   'X-Frame-Options': 'DENY',
# #   'X-Content-Type-Options': 'nosniff',
# #   'Referrer-Policy': '...',
# #   'Permissions-Policy': '...',
# #   'Cross-Origin-Opener-Policy': 'same-origin',
# #   'Cross-Origin-Embedder-Policy': 'require-corp',
# #   'Cross-Origin-Resource-Policy': 'same-origin',
# #   'Origin-Agent-Cluster': '?1',
# #   'Clear-Site-Data': '"cookies", "cache"'
# # }