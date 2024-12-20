# pdfmark
Scripts to add boomarks to PDF file according to a table of contents(we'll refer it as toc).
[This post][1] shows that it's easy to add bookmarks to a PDF using [ghostscript][2].
But some PDF has no bookmarks at all, and in general it's hard to manually generate a pdfmarks
file required by gs. With this script, bookmarks can be added to PDF according to a toc file
(descripted in the following).

## Requirements
* Python3
* [ghostscript][2]

## Toc file
We can add bookmarks to a PDF file by feeding the PDF file and
a toc file to this program. A toc file looks like the toc (table of contents) of a book, with
some other stuffs at the beginning of each line, as shown in the following:
```
!Contents 1
!0. Introduction 2
!1. First section 3
*1!1.1 Subsection 3
**!1.1.1 Subsubsection 3
**!1.1.2 Another subsubsection 5
*!1.2 Another subsection 7
!2. Second section 8
*!2.1 Subsection 3
*!2.2 Subsection 3
!3. Third section 8
```
As you can see, there are zero or more `*`s in the beginning of each line, followed
by an optional `1` and then a `!`. The number of `*`s
means the level of current items in the bookmarks, starting at 0.
That is to say that the top level entries always start with `!` or `1!`.
If there is a `1` before `!`, then this entry is opened by default,
otherwise it is closed. The exclamation mark indicates the end of those asterisks and
the beginning of the bookmark title. There are one or more spaces, i.e. ' ', after the title,
then follows the page number. In summary, each line of toc
file should match the regular expression `(^\**)(1?)!(.+?)\s+(-?[0-9]+)\s*$`.

## Alternative Toc file format (Tab-delemited)
If preferred, a tab-delimited format can be used instead as the toc file (by passing `--tsv` to the command line).
It has a fixed number of columns and hence easier to edit in Excel or other tabular editors. The columns are:
```
Level,IsOpen,Title,Page
```

The tab-delimited equivalent of the above toc would be (ignore the empty "header" line):

|||||
|-|-|-|-|
|0||Contents|1|
|0||0. Introduction|2|
|0||1. First section|3|
|1|*|1.1 Subsection|3|
|2||1.1.1 Subsubsection|3|
|2||1.1.2 Another subsubsection|5|
|1||1.2 Another subsection|7|
|0||2. Second section|8|
|1||2.1 Subsection|3|
|1||2.2 Subsection|3|
|0||3. Third section|8|

Where:
- `Level` is a non-empty zero-based integer indicating the depth of the current item in the bookmarks
- `IsOpen`, if not blank, indicates whether this entry is opened by default, and can be any **single character**
- The file can't contain headers, comments, and empty lines.

Technically, each line of this toc format should match the regular expression `^([0-9]+)\t(.?)\t(.+?)\t(-?[0-9]+)$`.

# Usage
```
$ pdfmark --in <input> --toc <toc-file> --out <output> [--offset <offset>] [--tsv] [--page <page>] [--fit page|width] [--print-pdfmarks]
```
Where:
- `<input>`, and `<output>` are input PDF and output PDF
- `<toc-file>` is the toc file as described above
- `<offset>` (optional) stands for the offset that should be added to the page numbers in toc file in order to get the real page number in the PDF file
- `--tsv` (optional) indicates that the toc file format is tab-delimited
- `<page>` (optional) sets the default page to display when the PDF opens (defaults to 1)
- `--fit` (optional) sets the default zoom for when the PDF opens, can be either `page` or `width`
- `--print-pdfmarks` (optional) is for debugging purposes, prints `pdfmarks` and exists (doesn't create an output PDF)

[1]: http://blog.tremily.us/posts/PDF_bookmarks_with_Ghostscript/
[2]: http://ghostscript.com/
