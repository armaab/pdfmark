# pdfmark
Scripts to add boomarks to PDF file, from table of contents(we'll refer it as toc).
It's super easy to add bookmarks to a PDF using [ghostscript][2], according to [this post][1].
But some PDF has no bookmarks at all, and it's not easy to generate a pdfmarks file that is used by gs manually.
With this script, bookmarks can be added to PDF from a toc file(descripted in the following).

## Requirements
* Python
* [ghostscript][2]

## Toc file
Bookmarks are generated from a toc file that just likes the toc of a book, except
the beginning of each line. Toc file should be provided by the user.The toc file should looks like:
```
!Contents 1
!0. Introduction 2
!1. First section 3
*1!1.1 Subection 3
**!1.1.1 Subsubsection 3
**!1.1.2 Another subsubsection 5
*!1.2 Another subsection 7
!2. Second section 8
*!2.1 Subection 3
*!2.2 Subection 3
!3. Third section 8
```
As in the example, there are zero or more '\*'s followed by an optional
'1' and then an '!', at the beginning of each line. The number of '\*'s
means the level of current items in the bookmarks, and it's started from 0.
If there is an '1' before '!', then the default display of current item is open,
otherwise it is closed. The excalmatory mark indicste the end of those '\*''s and
the beginning of bookmark title. There are one or more spaces, i.e. ' ', after the title,
then follows the page number.
# Usage
`$ pdfmark --in <input> --toc <toc-file> --out <output> [--offset <offset>]`
Where `<input>`, and `<output>` are input PDF and output PDF, `<toc-file>`
is the toc file as described above, and the option `<offset>` is optional, it
means the offset that should be added to the page numbers in toc file.

[1]: http://blog.tremily.us/posts/PDF_bookmarks_with_Ghostscript/
[2]: http://ghostscript.com/
