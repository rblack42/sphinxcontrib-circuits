M4 Circuit Processing
#####################

:Reference: http://www.fabrice-salvaire.fr/open-hardware/electronic-circuit-diagram/index.html

..  include::   /references.inc

In setting up to build a Sphinx_ extension that will generate ``PNG`` files for
inclusion in |RST| documents, I did a bit of research on the web and found the
reference above. From this, I generated this simple Makefile

..  literalinclude::    examples/Makefile

This ``Makefile`` will process all ``.m4`` files found in the current directory
and leave behind a set of ``PNG`` files that can be added to a |RST| document
manually.

..  vim:filetype=rst spell:

