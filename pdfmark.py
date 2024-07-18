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

def parsetoc(s, legacy_format=True):
    '''Parse toc file.

    Args:
        s: An iterable of strings each entry represents a line in toc
        file.

    Returns:
        A list of dicts each represents a toc item looking like:

        {'count': 1,
         'flag': '',
         'title': 'Some title',
         'page': 10}

         If there is an error in the toc file, then a tuple is
         returned to indicate the line number and content of the line
         where the error occurs. For example:

         (2, 'Contents 4')

         indicates that there is a error on line 2 of the toc file and
         the content of that line is 'Contents 4'.
    '''
    import re
    if legacy_format:
        regexp = re.compile(r'(^\**)(1*)!(.+?)\s+(-?[0-9]+)\s*$')
    else:
        regexp = re.compile(r'^([0-9]+)\t(.?)\t(.+?)\t(-?[0-9]+)$')
    lastlevel = 0
    res, lines = [], []
    i = 0

    for j, l in enumerate(s):
        m = regexp.match(l)
        if m is None:
            return (j, l)
        level = len(m.group(1)) if legacy_format else int(m.group(1))
        res.append({'count': 0, 'flag': '' if m.group(2) else '-',
            'title': m.group(3), 'page': int(m.group(4))})

        if level > lastlevel + 1:
            return (j, l)
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
    parser.add_argument('--in', dest='input', required=True, nargs='+',
            help='the input PDF to add bookmarks to')
    parser.add_argument('--out', dest='out', default='output.pdf',
            help='path to output PDF')
    parser.add_argument('--toc', dest='toc', required=True,
            help='path to toc file')
    parser.add_argument('--offset', dest='offset', type=int, default=0,
            help='offset of page numbers')
    parser.add_argument('--tsv', action='store_true',
            help='use tab-delimited format for TOC file')
    parser.add_argument('--page', type=int, default=1,
            help='default page to show when pdf opens')
    parser.add_argument('--fit', choices=["page", "width"],
            help='default zoom when pdf opens')
    parser.add_argument('--gs', default=GS,
            help='path to the gs (ghostscript) excutable')
    parser.add_argument('--print-pdfmarks', dest='marks', action='store_true',
            help='print pdfmarks to the standard output and exit')

    args = parser.parse_args()
    s = []
    with open(args.toc, 'r') as f:
        infos = parsetoc(f, legacy_format=not args.tsv)
    if isinstance(infos, tuple):
        print('Error on line {} in {}:\n{}'.format(infos[0]+1, args.toc,infos[1]))
        exit(1)

    page_str = " /Page " + str(args.page)
    fit_str = " /View [/Fit] " if args.fit == "page" else " /View [/FitH -32768] " if args.fit == "width" else ""
    marks = (
        "[/PageMode /UseOutlines"
        + page_str
        + fit_str
        + " /DOCVIEW pdfmark\n"
        + "\n".join(row for row in gen_pdfmarks(infos, args.offset))
    )
    if args.marks:
        for mark in marks.split("\n"):
            print(mark)
        exit()

    marks = '/pdfmark { originalpdfmark } bind def' + marks
    marks = marks.encode()

    gsargs = [args.gs, '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite']
    if args.out:
        gsargs.append('-sOutputFile={}'.format(args.out))

    ignoreps = os.path.dirname(os.path.realpath(__file__))+'/'+IGNOREPS
    gsargs.append(ignoreps)
    gsargs.extend(args.input)
    gsargs.append('-')

    subprocess.run(gsargs, input=marks)
