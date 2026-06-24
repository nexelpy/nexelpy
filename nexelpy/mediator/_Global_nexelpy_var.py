from datetime import datetime


nexelpyOBJ = None
root_progect = None
project_root_dir =None
dev_Mode = None


FERNET = None


scan_python_file = []
inspect_python_file = []
AutoRegister_list = []
manualRegister_list = []


erorr = []
def erorr_append(ClassName,e):
    if dev_Mode :
        now = datetime.now().strftime("%H:%M:%S")
        er_dict = {"class":ClassName,"date":now,"e":e}
        erorr.append(er_dict)
        return er_dict
    




STRICT_GLOBAL_HEADERS = {
    # ==========================================
    # (Security Headers - Balanced)
    # ==========================================
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; upgrade-insecure-requests;",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "accelerometer=(), autoplay=(), camera=(), fullscreen=(), geolocation=(), gyroscope=(), microphone=(), payment=(), usb=()",
    

    "Cross-Origin-Opener-Policy": "same-origin", 
    "Cross-Origin-Resource-Policy": "cross-origin", 
    # "Cross-Origin-Embedder-Policy"
    
    "X-Permitted-Cross-Domain-Policies": "none",
    "X-Download-Options": "noopen",
    
    # ==========================================
    # (Caching Headers)
    # ==========================================
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
    
    # ==========================================
    # (Content & Behavior)
    # ==========================================
    "Content-Language": "en",
    "X-DNS-Prefetch-Control": "on",
}
