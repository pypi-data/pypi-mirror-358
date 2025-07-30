try:
    from importlib.metadata import version
    __version__ = version("spellbind")
except Exception:
    __version__ = "unknown"
