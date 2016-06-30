#!/usr/bin/env python3
import codecs
import subprocess

GS = 'gs'
IGNOREPS = 'ignore.ps'

def tounicode(s):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        s = codecs.BOM_UTF16_BE + s.encode('utf-16-be')
        return '<{}>'.format(''.join('{:02X}'.format(b) for b in s))
    else:
        for x, y in [('\\', '\\\\'), ('(', '\\('), (')', '\\)'), ('\n', '\\n'),
                ('\t', '\\t'), ('\b', '\\b')]:
            s = s.replace(x, y)
        return '({})'.format(s)

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
            return j
        level = len(m.group(1))
        res.append({'count': 0, 'flag': '' if m.group(2) else '-',
            'title': m.group(3), 'page': int(m.group(4))})

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

def gen_pdfmarks(infos, offset=0):
    for i in range(len(infos)):
        c = infos[i]['count']
        if c:
            row = '[/Count {}{} '.format(infos[i]['flag'], c)
        else:
            row = '['
        row += '/Title {} /Page {} /OUT pdfmark'.format(
                tounicode(infos[i]['title']), infos[i]['page']+offset)
        yield row

if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('--in', dest='input', required=True,
            help='the input PDF to add bookmarks to')
    parser.add_argument('--out', dest='out', default='output.pdf',
            help='path to output PDF')
    parser.add_argument('--toc', dest='toc', required=True,
            help='path to toc file')
    parser.add_argument('--offset', dest='offset', type=int, default=0,
            help='offset of page numbers')
    parser.add_argument('--gs', dest='gs', default=GS,
            help='path to the gs (ghostscript) excutable')

    args = parser.parse_args()
    s = []
    with open(args.toc, 'r') as f:
        for line in f:
            s.append(line)
    infos = parsetoc(s)
    if isinstance(infos, int):
        print('Error on line {} in {}:\n{}'.format(infos+1, args.toc, s[infos]))
        exit(1)
    marks = b'/pdfmark { originalpdfmark } bind def'
    marks += b'\n'.join(row.encode() for row in gen_pdfmarks(infos, args.offset))

    gsargs = [args.gs, '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite']
    if args.out:
        gsargs.append('-sOutputFile={}'.format(args.out))

    ignoreps = os.path.dirname(os.path.realpath(__file__))+'/'+IGNOREPS
    gsargs.extend([ignoreps, args.input, '-'])

    subprocess.run(gsargs, input=marks)
