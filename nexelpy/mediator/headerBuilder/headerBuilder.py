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
            self._raw_headers[key.replace("__", "-")] = value
        return self
    
    def set_super_strict(self):
        self.add_raw_header(
            Content__Security__Policy="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
            Strict__Transport__Security="max-age=31536000; includeSubDomains; preload",
            Cache__Control="no-store, no-cache, must-revalidate, private",
            X__Frame__Options="DENY",
            X__Content__Type__Options="nosniff",
            Referrer__Policy="no-referrer",
            Permissions__Policy="geolocation=(), camera=(), microphone=(), usb=(), payment=(), encrypted-media=(), speaker=(), autoplay=()",
            Cross__Origin__Opener__Policy="same-origin",
            Cross__Origin__Embedder__Policy="require-corp",
            Cross__Origin__Resource__Policy="same-origin",
            Origin__Agent__Cluster="?1",)
        return self

    def set_strict(self):
        self.add_raw_header(
            Content__Security__Policy="default-src 'self'; script-src 'self' https:; style-src 'self' https:; img-src 'self' data: https:; connect-src 'self' https:; frame-ancestors 'self'; base-uri 'self'; form-action 'self'",
            Strict__Transport__Security="max-age=31536000; includeSubDomains; preload",
            Cache__Control="no-cache, no-store, must-revalidate",
            X__Frame__Options="SAMEORIGIN",
            X__Content__Type__Options="nosniff",
            Referrer__Policy="strict-origin-when-cross-origin",
            Permissions__Policy="geolocation=(self), camera=(), microphone=(), usb=(), payment=(), autoplay=(self)",
            Cross__Origin__Opener__Policy="same-origin",
            Cross__Origin__Embedder__Policy="require-corp",
            Cross__Origin__Resource__Policy="same-origin",
            Origin__Agent__Cluster="?1")
        return self

    def set_normal(self):
        self.add_raw_header(
            Content__Security__Policy="default-src 'self' https:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; connect-src 'self' https:; frame-ancestors 'self'; base-uri 'self'",
            Strict__Transport__Security="max-age=31536000; includeSubDomains",
            Cache__Control="public, max-age=86400",
            X__Frame__Options="SAMEORIGIN",
            X__Content__Type__Options="nosniff",
            Referrer__Policy="strict-origin-when-cross-origin",
            Permissions__Policy="geolocation=(self), autoplay=(*)",
            Cross__Origin__Opener__Policy="same-origin-allow-popups",
            Cross__Origin__Resource__Policy="cross-origin",
            Origin__Agent__Cluster="?1")
        return self

    def set_relaxed(self):
        self.add_raw_header(
            Content__Security__Policy="default-src *; script-src * 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline'; img-src * data:; connect-src *; frame-ancestors *; base-uri *",
            Strict__Transport__Security="max-age=86400",
            Cache__Control="public, max-age=31536000, immutable",
            X__Frame__Options="SAMEORIGIN",
            X__Content__Type__Options="nosniff",
            Referrer__Policy="unsafe-url",
            Permissions__Policy="*",
            Cross__Origin__Opener__Policy="unsafe-none",
            Cross__Origin__Embedder__Policy="unsafe-none",
            Cross__Origin__Resource__Policy="cross-origin",
            Origin__Agent__Cluster="?0")
        return self

    def build_header(self):
        self._final_header = {}
        
        for builder in self._obj_classes:
            self._final_header.update(builder.build_header())
        
        self._final_header.update(self._raw_headers)
        
        return self._final_header