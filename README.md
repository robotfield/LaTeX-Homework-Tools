# LaTeX Homework Tools

Various scripts to assist in creating and compiling similarly-formatted LaTeX projects.  Written in Bash and Python 3.

## `genlatex.py`

This is a script to generate LaTeX files.  By default, it prints to standard output,
but it can print to a file specified with the `-o` tag.

### Document Structure

The most useful part of this script is its ability to generate enumerate statements,
and optionally generate separate `.tex` files for each problem and `\input{}` them.
Especially if you're transcribing from a printed document, this saves a lot of time.

The script reads a very simple structuring format, either as a string in the
commandline argument `-s`, or from a file.

Format strings contain lists of words separated by any kind of whitespace or newline,
so they can be written with any spacing or indentation.  To specify an enumerate
statement, simply write `list ... end`.  List statements can be nested.  Inside a 
list statement, words will turn into `\item[]`s in the output unless they are `list`,
`end`, or `..` (two dots). Writing `..` will generate a range of words between the
immediately preceding and following words.  For example `a .. d` expands to `a b c d`.
This also works for numbers and Roman numerals.  For example the following format (example_structure.txt)

```
list
	1 .. 5
	list
		a
		list
			i
			..
			iv
		end
		b
		..
		e
	end
	6 7
end
```
expands to this:
```
...
\begin{enumerate}
      \item[1.]
      \item[2.]
      \item[3.]
      \item[4.]
      \item[5.]
      \begin{enumerate}
        \item[a.]
        \begin{enumerate}
                \item[i.]
                \item[ii.]
                \item[iii.]
                \item[iv.]
        \end{enumerate}
        \item[b.]
        \item[c.]
        \item[d.]
        \item[e.]
      \end{enumerate}
      \item[6.]
      \item[7.]
\end{enumerate}
...
```

Restrictions on the formatting language are that nested `list` statements 
must have preceding elements, `..` must have elements on either side (which 
are not `list` statements), and writing `i .. v` will generate `i ii iii iv v`
instead of `i j k l m n o p q r s t u v` (and similar things will happen for
other character ranges with boundries which happen to also be Roman numerals).

These format statements can either be read as a string in the commandline
(for example, `genlatex.py -s "list a .. e end"`), or as a file (for example,
`genlatex.py -f example_structure.txt`).

### Separate Homework Files

If the `-g` option is enabled, `genlatex.py` will generate files in a `problems/`
directory for each entry in a `list` statement (besides nested statements), and
use `\input{}` to insert them into the resulting LaTeX document.
Each nested list statement will create a subdirectory in `problems/` (or whichever
directory the outer list statement occupies) to contain its entries.

For example, running 
```
$ genlatex.py -gf example_structure.txt -o main.tex
$ cd problems
$ tree
```
will result in the following output:
```
problems/
├── 1.tex
├── 2.tex
├── 3.tex
├── 4.tex
├── 5
│   ├── a
│   │   ├── iii.tex
│   │   ├── ii.tex
│   │   ├── i.tex
│   │   └── iv.tex
│   ├── b.tex
│   ├── c.tex
│   ├── d.tex
│   └── e.tex
├── 6.tex
└── 7.tex

2 directories, 14 files
```