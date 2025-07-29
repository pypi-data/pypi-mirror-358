def rgb_to_ansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m" 
def reset_color():
    return "\033[0m"
def interpolate_color(start, end, factor):
    return tuple(
        int(start[i] + (end[i] - start[i]) * factor) for i in range(3)
    )
def gradify(text_or_content, start_color, end_color, direction="horizontal"):
    if direction not in ["horizontal", "vertical"]:
        raise ValueError("Direction must be 'horizontal' or 'vertical'.")

    # Check if input is a starri content list (list of dicts)
    if isinstance(text_or_content, list) and text_or_content and isinstance(text_or_content[0], dict):
        content = text_or_content
        # Extract labels for types that have labels
        labels = [item["label"] for item in content if item.get("type") in ("option", "checkbox", "text")]

        # Apply gradient vertically across all labels combined
        total_lines = len(labels)
        colored_labels = []

        if direction == "horizontal":
            # Apply horizontal gradient per label individually
            for line in labels:
                length = len(line)
                output = ""
                for i, char in enumerate(line):
                    factor = i / max(length - 1, 1)
                    r, g, b = interpolate_color(start_color, end_color, factor)
                    output += f"{rgb_to_ansi(r, g, b)}{char}"
                output += reset_color()
                colored_labels.append(output)

        else:  # vertical gradient across all labels combined
            for i, line in enumerate(labels):
                factor = i / max(total_lines - 1, 1)
                r, g, b = interpolate_color(start_color, end_color, factor)
                colored_labels.append(f"{rgb_to_ansi(r, g, b)}{line}{reset_color()}")

        # Replace labels inside content with colored versions
        new_content = []
        color_index = 0
        for item in content:
            new_item = item.copy()
            if item.get("type") in ("option", "checkbox", "text"):
                new_item["label"] = colored_labels[color_index]
                color_index += 1
            new_content.append(new_item)
        return new_content

    # Otherwise treat input as string or list of strings (as before)
    if isinstance(text_or_content, list):
        lines = text_or_content
    else:
        lines = text_or_content.splitlines()

    output_lines = []

    if direction == "horizontal":
        for line in lines:
            length = len(line)
            output = ""
            for i, char in enumerate(line):
                factor = i / max(length - 1, 1)
                r, g, b = interpolate_color(start_color, end_color, factor)
                output += f"{rgb_to_ansi(r, g, b)}{char}"
            output += reset_color()
            output_lines.append(output)

    else:  # vertical
        total_lines = len(lines)
        for i, line in enumerate(lines):
            factor = i / max(total_lines - 1, 1)
            r, g, b = interpolate_color(start_color, end_color, factor)
            output_lines.append(f"{rgb_to_ansi(r, g, b)}{line}{reset_color()}")

    if isinstance(text_or_content, list):
        return output_lines
    else:
        return "\n".join(output_lines)

