def str2bool(v):
    """
    Function to parse a string representing a bool
    """
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 'True', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'False', 'f', 'n', '0'):
        return False
    else:
        raise Exception('Boolean value expected.')

def is_tool(name):
    """
    Check whether `name` is on PATH and marked as executable.

    Returns
    -------
    True if `name` exists
    """

    # from whichcraft import which
    from shutil import which

    return which(name) is not None