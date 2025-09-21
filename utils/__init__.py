def sizeFormat(size):
    if size < 1024:
        return f"{size}B"
    elif size < 1024**2:
        return f"{round(size / 1024, 2)}KB"
    elif size < 1024**3:
        return f"{round(size / 1024**2, 2)}MB"
    elif size < 1024**4:
        return f"{round(size / 1024**3, 2)}GB"
    elif size < 1024**5:
        return f"{round(size / 1024**4, 2)}TB"
    else:
        return f"{round(size / 1024**5, 2)}PB"
