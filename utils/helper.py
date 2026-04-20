def build_url(base_url, path=""):
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}" if path else base_url.rstrip("/")
