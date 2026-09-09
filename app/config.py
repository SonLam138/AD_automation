

LDAP_HOST = "DC-01.automate.com.vn"

LDAP_PORT = 636

LDAP_USE_SSL = True

LDAP_USER = "administrator@automate.com.vn"

LDAP_PASSWORD = "C0anhtien@123"

LDAP_BASE_DN = "DC=automate,DC=com,DC=vn"

# ============================================================
# LOGIN / PORTAL ACCESS GROUPS
# ============================================================

LOGIN_GROUP_LANDING_MAP = {
    "ad_login": "/assistant",
    "Onboard_Approve_Login": "/pending-request",
}

# ============================================================
# LOCAL LLM / OLLAMA CONFIG
# ============================================================

OLLAMA_BASE_URL = "http://localhost:11434"

OLLAMA_MODEL = "mistral"

OLLAMA_TIMEOUT_SECONDS = 500


ADMIN_APPROVAL_SECRET = (
    "ChuatePV"
)