svg_template = (
    '<?xml version="1.0" encoding="utf-8" ?>'
    '<svg baseProfile="tiny" version="1.2" '
    'viewBox="{x0} {y0} {width} {height}" '
    'width="{width}mm" height="{height}mm" '
    'style="background-color:{bg}" '
    'xmlns="http://www.w3.org/2000/svg" '
    'xmlns:ev="http://www.w3.org/2001/xml-events" '
    'xmlns:xlink="http://www.w3.org/1999/xlink">'
    '<path d="M1,1.5 {path_cmds}" '
    'stroke="{fg}" stroke-width="1"/></svg>'
)


def svg_from_matrix(matrix, fg='#000', bg='#FFF', margin=1):
    width = len(matrix[0]) + 2 * margin
    height = len(matrix) + 2 * margin
    x0 = 1 - margin
    y0 = 1 - margin

    def path_cmds():
        cmds = []
        for y, line in enumerate(matrix):
            i = 0
            w = len(line)
            while i < w:
                color = line[i]
                i0 = i
                while i < w and line[i] == color:
                    i += 1
                length = i - i0
                if color == 1:
                    cmds.append(f"h{length}")
                else:
                    cmds.append(f"m{length},0")
            cmds.append(f"m{-w},1")
        return ''.join(cmds)

    return svg_template.format(
        fg=fg, bg=bg, path_cmds=path_cmds(),
        x0=x0, y0=y0, width=width, height=height
    )
