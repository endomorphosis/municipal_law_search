def type_name(obj: object) -> str:
    """Get the type name of an object."""
    if obj is None:
        return "NoneType"
    if not hasattr(obj, "__name__"):
        return "unknown"
    return type(obj).__name__
