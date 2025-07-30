def build_path(base_path: str, paths: list[str]) -> str:
    """
    Build path from base path and given list of paths

    Args:
        base_path (str): base path
        paths (list[str]): list of paths

    Returns:
        str: built path
    """
    assert all(
        isinstance(path, str) for path in paths
    ), "paths must be a list of strings."

    return "/".join([base_path, ("/".join(paths)).replace("//", "/")])
