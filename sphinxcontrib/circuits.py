# -*- coding: utf-8 -*-
"""
    sphinxcontrib.circuits

    M4 Circuit diagram extension for Sphinx
"""
from docutils import nodes

class circuit(nodes.Admonition, nodes.Element):
pass

def html_visit_circuit(self, node):
    self.body.append('<h3>HTML Circuit</h3>')
    raise nodes.SkipNode

def latex_visit_circuit(self.node):
    self.body.append( 'LATEX Curcuit')
    raise nodes.SkipNode

def setup(app):
    app.add_node(circuit,
        html=(html_visit_circuit, None),
        latex = (latex_visit_circuit, None))
    app.add_directive('circuit', CircuitDirective)
    app.connect('doctree-resolved', number_equations)

    return {'version': '0.1' }


