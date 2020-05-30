

* Get a list of all commits using `git log` command.

# For each commit



* `git checkout <COMMIT>`.

## Build pdf diff

* Invoke latexdiff using `perl latexdiff main.tex prev.tex > diff.tex`
* Build `diff.tex` using `pdflatex.exe diff.tex`
* rename `main.tex` into `diff.tex` for next comparison.

## Render pdf to images:

 * Use ghostscript to print pdf to jpeg. https://stackoverflow.com/questions/331918/converting-a-pdf-to-a-series-of-images-with-python
 
