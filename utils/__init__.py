import re


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


def convertLxlyricToElyric(lxlyric: str) -> str:
    lxlyric = lxlyric.replace("\\n", "\n")

    lines = lxlyric.splitlines()
    converted_lines = []

    def ms_to_timestamp(ms: int) -> str:
        total_seconds = ms / 1000.0
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:06.3f}"

    for line in lines:
        line = line.rstrip("\n\r")

        if not line:
            converted_lines.append("")
            continue

        match = re.match(r"\[([^\]]+)\](.+)", line)
        if not match:
            converted_lines.append(line)
            continue

        timestamp = match.group(1)
        content = match.group(2)

        pattern = r"<(\d+),(\d+)>([^<]*)"
        matches = re.findall(pattern, content)

        converted_parts = []
        for i, (start_str, duration_str, text) in enumerate(matches):
            start_ms = int(start_str)
            duration_ms = int(duration_str)  # noqa: F841

            start_time = ms_to_timestamp(start_ms)

            if i == 0:
                converted_parts.append(f"<{start_time}>{text}")
            else:
                converted_parts.append(f"<{start_time}>{text}")

        if matches:
            last_start = int(matches[-1][0])
            last_duration = int(matches[-1][1])
            final_time = ms_to_timestamp(last_start + last_duration)
            converted_parts.append(f"<{final_time}>")

        converted_lines.append(f"[{timestamp}]{''.join(converted_parts)}")

    return "\n".join(converted_lines)
