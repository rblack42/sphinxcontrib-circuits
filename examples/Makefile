# Circuit Macros v8.3

FILES	= $(wildcard *.m4)
PNGS	= $(FILES:.m4=.png)
MACROS	= ~/_lib/circuits

all:	$(PNGS)

vars:
	$(info FILES => $(FILES))
	$(info PNGS => $(PNGS))

%.pic:	%.m4
	m4 -I $(MACROS) pgf.m4 libcct.m4 $< > $@

%.tex:	%.pic
	dpic -g $< > picture.tex
	cat m4head picture.tex m4tail > $@
	rm picture.tex

%.pdf:	%.tex
	pdflatex -shell-escape $<
	rm -f $*-* $*.aux* $*.log

%.png:	%.pdf
	convert -density 300 -transparent white $< $@


test:
	convert -density 600 $< $@
	ps2eps --force --quiet --loose $< $@
	dvips $<
	cp default.dvi $@
	cp $@ default.tex


clean:
	rm -f *.aux *.dvi *.pic *.ps *.tex *.auxlock *.log *.pdf *.md5 *.out

