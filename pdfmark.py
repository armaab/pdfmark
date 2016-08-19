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
    regexp = re.compile(r'(^\**)(1*)!(.+?)\s+(-?[0-9]+)\s*$')
    lastlevel = 0
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

def parseinfo(s):
    import re
    regexp = re.compile(r'^BookmarkBegin')
    i = -1
    for l in s:
        if i == 0 or i == -1:
            m = regexp.match(l)
            if m is None:
                if i == 0:
                    break
                continue
            else:
                i = 1
                continue
        elif i == 1:
            title = l.strip().split(': ')[1]
            i += 1
        elif i == 2:
            level = '*' * (int(l.split()[1])-1) + '!'
            i += 1
        elif i == 3:
            yield level + title + ' ' + l.split()[1]
            i = 0

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
    parser.add_argument('--print-pdfmarks', dest='marks', action='store_true',
            help='print pdfmarks to the standard output')

    args = parser.parse_args()
    s = []
    with open(args.toc, 'r') as f:
        infos = parsetoc(f)
    if isinstance(infos, int):
        print('Error on line {} in {}:\n{}'.format(infos+1, args.toc, s[infos]))
        exit(1)
    marks = '\n'.join(row for row in gen_pdfmarks(infos, args.offset))
    if args.marks:
        print(marks)
        exit()
    marks = '/pdfmark { originalpdfmark } bind def' + marks
    marks = marks.encode()

    gsargs = [args.gs, '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite']
    if args.out:
        gsargs.append('-sOutputFile={}'.format(args.out))

    ignoreps = os.path.dirname(os.path.realpath(__file__))+'/'+IGNOREPS
    gsargs.extend([ignoreps, args.input, '-'])

    subprocess.run(gsargs, input=marks)
