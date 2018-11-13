# pdfmark
Scripts to add boomarks to PDF file according to a table of contents(we'll refer it as toc).
[This post][1] shows that it's easy to add bookmarks to a PDF using [ghostscript][2].
But some PDF has no bookmarks at all, and in general it's hard to manually generate a pdfmarks
file required by gs. With this script, bookmarks can be added to PDF according to a toc file
(descripted in the following).

## Requirements
* Python
* [ghostscript][2]

## Toc file
We can add bookmarks to a PDF file by feeding the PDF file and
a toc file to this program. A toc file looks like the toc (table of contents) of a book, with
some other stuffs at the beginning of each line, as shown in the following:
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
As you can see, there are zero or more `*`s in the beginning of each line, followed
by an optional `1` and then a `!`. The number of `*`s
means the level of current items in the bookmarks, starting at 0.
That is to say that the top level entries always start with `!` or `1!`.
If there is an '1' before '!', then this entry is open by default,
otherwise it is closed. The excalmatory mark indicates the end of those '\*''s and
the beginning of bookmark title. There are one or more spaces, i.e. ' ', after the title,
then follows the page number. In summary, each line of toc
file should match the regular expression `(^\**)(1?)!(.+?)\s+(-?[0-9]+)\s*$`.
# Usage
```
$ pdfmark --in <input> --toc <toc-file> --out <output> [--offset <offset>]
```
Where `<input>`, and `<output>` are input PDF and output PDF, `<toc-file>`
is the toc file as described above, and the option `<offset>` is optional, it
stands for the offset that should be added to the page numbers in toc file in order
to get the real page number in the PDF file.

[1]: http://blog.tremily.us/posts/PDF_bookmarks_with_Ghostscript/
[2]: http://ghostscript.com/
