def parsetoc(s):
    import re
    regexp = re.compile(r'(^\**)(-*)!(.+?) ([0-9]+$)')
    m = regexp.match(s[0])
    lastlevel = len(m.group(1))
    res, lines = [], []
    i = 0

    for j, l in enumerate(s):
        m = regexp.match(l)
        if m is None:
            continue
        level = len(m.group(1))
        res.append({'count': 0, 'flag': '' if m.group(2) else '-',
            'title': m.group(3), 'page': m.group(4)})

        if level > lastlevel + 1:
            return j
        elif level == lastlevel + 1:
            lines.append((i-1, lastlevel))
        elif level < lastlevel:
            lines.pop()
            while lines and lines[-1][1] >= level:
                lines.pop()
        if lines:
            res[lines[-1][0]]['count'] += 1
        lastlevel = level
        i += 1
    return res
