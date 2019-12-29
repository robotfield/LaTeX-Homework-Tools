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

If the `-g/--generate-files` option is enabled, `genlatex.py` will generate files in a `problems/`
directory for each entry in a `list` statement (besides nested statements), and
use `\input{}` to insert them into the resulting LaTeX document.
Each nested list statement will create a subdirectory in `problems/` (or whichever
directory the outer list statement occupies) to contain its entries.

For example, running (in a UNIX-like system)
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

and main.tex will contain
```
...

\begin{enumerate}
      \item[1.]
        \input{problems/1.tex}
      \item[2.]
        \input{problems/2.tex}
      \item[3.]
        \input{problems/3.tex}
      \item[4.]
        \input{problems/4.tex}
      \item[5.]
      \begin{enumerate}
        \item[a.]
        \begin{enumerate}
                \item[i.]
                        \input{problems/5/a/i.tex}
                \item[ii.]
                        \input{problems/5/a/ii.tex}
                \item[iii.]
                        \input{problems/5/a/iii.tex}
                \item[iv.]
                        \input{problems/5/a/iv.tex}
        \end{enumerate}
        \item[b.]
                \input{problems/5/b.tex}
        \item[c.]
                \input{problems/5/c.tex}
        \item[d.]
                \input{problems/5/d.tex}
        \item[e.]
                \input{problems/5/e.tex}
      \end{enumerate}
      \item[6.]
        \input{problems/6.tex}
      \item[7.]
        \input{problems/7.tex}
\end{enumerate}
...
```

`-b/--generate-files-boxes` does the same thing as `-g`, except it makes each problem
file contain the following:
```
\begin{mdframed}

\end{mdframed}
```

Note that this requires `\usepackage{mdframed}`

### `\maketitle` Info

By default, `genlatex.py` will set the author to be "Anonymous", the title to be
the name of the current directory, and the date to be the current date in
"[Day] [Month Name] [Full Year]" format.  The strings for all ofthese can be
changed by using `-a/--author`, `-t/--title`, and `-d/--date`.

###  Linking and Auto-Generated Directories+Files

`genlatex.py` expects `~/latexdefaults/` (the '`defaults`' directory), 
`~/latexdefaults/defaults.tex`, and `/latexdefaults/optional/` to exist, as of now.
The `defaults` directory path can be changed using `--defaults`.  However, if they
do not exist, they will be auto-generated.  Note that passing `--defaults "defaults"`
to `genlatex.py` will result in the defaults directory being generated locally.

Additionally, by default, a symlink to the defaults directory will be generated in
the project directory.  This is to avoid constantly copying headers in many similar
projects, and keep paths inputted into the LaTeX document local.

The `-n/--no-symlink` option recursively copies the `defaults` directory into the
project directory instead of symlinking it.  This is necessary if the project
will be compiled on a different computer.

If `-o` is specified, the output file name will be inserted into the first line of
a file called `.genlatex_project_info`.  This is so that `compile_latex_project.sh`
knows what the main `tex` file is.  (The file is also used by 
`compile_latex_project.sh` to detect changes to `tex` files in the project
directory with md5 sums, which are placed on the second line, but `genlatex.py`
does not calculate these sums.)

###  Inputting Defaults

`defaults/defaults.tex` is automatically inputted into the preamble of the output.

Additional `tex` files can be inputted from the `defaults/optional` directory using
the `--optional` option.  For example, if one wanted to write a Physics homework
document, and wanted to include a file called `defaults/optional/physics.tex`
for specialized Physics LaTeX commands, then they could run 
`genlatex.py --optional physics`.

##  `compile_latex_project.sh`


This is a very simple script which checks the project's `.tex` files for changes
every second, then recompiles the entire project if it changes.  Exit with CTRL-C.

Currently relies on `.genlatex_project_info` existing and containing the name of 
the main document on the first line.