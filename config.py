import os

# Shared entry password
ENTRY_PASSWORD = os.getenv("ENTRY_PASSWORD", "")

# Comma-separated whitelist: "alice,bob,charlie"
WHITELIST = set(
    user.strip().lower()
    for user in os.getenv("WHITELIST", "").split(",")
    if user.strip()
)

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")