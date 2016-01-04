import re, sys, os
import codecs
import shutil
import tempfile
import posixpath
from os import path, getcwd, chdir
from subprocess import Popen, PIPE
try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

from docutils import nodes, utils
from docutils.parsers.rst import directives

from sphinx.util.compat import Directive

from sphinx.errors import SphinxError
from sphinx.util.png import read_png_depth, write_png_depth
from sphinx.util.osutil import ensuredir, ENOENT

LATEX_IMAGE_DIR = '/Users/rblack/_lib/images/'
LATEX_URL = '/_images/'
LATEX_BUILD_DIR = '/Users/rblack/_tmp'

class CircuitExtError(SphinxError):
    category = 'Circuit extension error'

    def __init__(self, msg, stderr=None, stdout=None):
        if stderr:
            msg += '\n[stderr]\n' + stderr
        if stdout:
            msg += '\n[stdout]\n' + stdout
        SphinxError.__init__(self, msg)

DOC_BODY = r'''
\begin{document}
\begin{circuit}
%s
\end{circuit}
\end{document}
'''

depth_re = re.compile(r'\[\d+ depth=(-?\d+)\]')

def render_circuit(self, circuit):
    '''given the raw circuit code, produce the png file''' 
    shasum = "%s.png" % sha(circuit.encode('utf-8')).hexdigest()
    relfn = posixpath.join(self.builder.imgpath, 'circuit', shasum)
    outfn = path.join(self.builder.outdir, '_images', 'circuit', shasum)
    if path.isfile(outfn):
        depth = read_png_depth(outfn)
        return relfn, depth

    # if latex or dvipng has failed once, don't bother to try again
    if hasattr(self.builder, '_circuit_warned_latex') or \
       hasattr(self.builder, '_circuit_warned_dvipng'):
        return None, None

    latex = (DOC_BODY) % circuit

    if not hasattr(self.builder, '_circuitpng_tempdir'):
        tempdir = self.builder._circuit_tempdir = LATEX_BUILD_DIR
    else:
        tempdir = self.builder._circuit_tempdir

    tf = codecs.open(path.join(tempdir, 'circuit.tex'), 'w', 'utf-8')
    tf.write(latex)
    tf.close()

    ltx_args = [self.builder.config.circuit_latex, '--interaction=nonstopmode']
    # add custom args from the config file
    ltx_args.extend(self.builder.config.circuit_latex_args)
    ltx_args.append('circuit.tex')

    curdir = getcwd()
    chdir(tempdir)

# process this latex script with circuit
    try:
        try:
            # first latex run
            p = Popen(ltx_args, stdout=PIPE, stderr=PIPE)
        except OSError, err:
            if err.errno != ENOENT:   # No such file or directory
                raise
            self.builder.warn('LaTeX command %r cannot be run (needed for circuit '
                              'display), check the circuit_latex setting' %
                              self.builder.config.circuit_latex)
            self.builder._circuit_warned_latex = True
            return None, None
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise CircuitExtError('latex exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))          
        print 'first run of latex',ltx_args

        try:
            # first circuit run
            circuit_args = ['circuit','circuit']
            p = Popen(circuit_args, stdout=PIPE, stderr=PIPE)
        except OSError, err:
            if err.errno != ENOENT:
                raise
            self.builder,warn('Circuit command failed')
            self.builder._circuit_warned_latex = True
            return None, None
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise CircuitExtError('circuit exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))            
        print 'first circuit run:', circuit_args  
        try:
            p = Popen(circuit_args, stdout=PIPE, stderr=PIPE)
        except OSError, err:
            if err.errno != ENOENT:
                raise
            self.builder,warn('Circuit command failed')
            self.builder._circuit_warned_latex = True
            return None, None
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise CircuitExtError('circuit exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))            
        print 'second circuit run:', circuit_args               
        try:
            p = Popen(ltx_args, stdout=PIPE, stderr=PIPE)
        except OSError, err:
            if err.errno != ENOENT:   # No such file or directory
                raise
            self.builder.warn('LaTeX command %r cannot be run (needed for circuit '
                              'display), check the circuit_latex setting' %
                              self.builder.config.circuit_latex)
            self.builder._circuitpng_warned_latex = True
            return None, None
    finally:
        chdir(curdir)
    print 'second run of latex',ltx_args        

    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise CircuitExtError('latex exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))

    ensuredir(path.dirname(outfn))

    # Now, convert the image to a PNG file
    # use some standard dvipng arguments
    dvipng_args = [self.builder.config.circuit_dvipng]
    dvipng_args += ['-o', outfn, '-T', 'tight', '-z9']
    # add custom ones from config value
    dvipng_args.extend(self.builder.config.circuit_dvipng_args)
    # last, the input file name
    dvipng_args.append(path.join(tempdir, 'circuit.dvi'))
    try:
        p = Popen(dvipng_args, stdout=PIPE, stderr=PIPE)
        print 'dvipng run',dvipng_args
    except OSError, err:
        if err.errno != ENOENT:   # No such file or directory
            raise
        self.builder.warn('dvipngpng command %r cannot be run (needed for circuit '
                          'display), check the circuit_dvipng setting' %
                          self.builder.config.circuit_dvipng)
        self.builder._circuit_warned_dvipng = True
        return None, None
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise CircuitExtError('dvipng exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))
    depth = None

    return relfn, depth

class circuit(nodes.Inline, nodes.TextElement):
    pass

class displaycircuit(nodes.Part, nodes.Element):
    pass

class CircuitDirective(Directive):

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'label': directives.unchanged
    }

    def run(self):
        latex = '\n'.join(self.content)
        if self.arguments and self.arguments[0]:
            latex = self.arguments[0] + '\n\n' + latex
        node = displaycircuit()
        node['latex'] = latex
        node['label'] = self.options.get('label', None)
        node['docname'] = self.state.document.settings.env.docname
        ret = [node]
        if node['label']:
            tnode = nodes.target('', '', ids=['equation-' + node['label']])
            self.state.document.note_explicit_target(tnode)
            ret.insert(0, tnode)
        return ret

def html_visit_circuit(self, node):
    try:
        fname, depth = render_circuit(self, '$'+node['latex']+'$')
    except CircuitExtError, exc:
        msg = unicode(str(exc), 'utf-8', 'replace')
        sm = nodes.system_message(msg, type='WARNING', level=2,
                                  backrefs=[], source=node['latex'])
        sm.walkabout(self)
        self.builder.warn('display latex %r: ' % node['latex'] + str(exc))
        raise nodes.SkipNode
    if fname is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="circuit">%s</span>' %
                         self.encode(node['latex']).strip())
    else:
         c = ('<img class="circuit" src="%s"' % fname)
         if depth is not None:
             c += ' style="vertical-align: %dpx"' % (-depth)
         self.body.append( c + '/>')
    raise nodes.SkipNode

def html_visit_displaycircuit(self, node):
    latex = node['latex']
    try:
        fname, depth = render_circuit(self, latex)
    except CircuitExtError, exc:
        sm = nodes.system_message(str(exc), type='WARNING', level=2,
                                  backrefs=[], source=node['latex'])
        sm.walkabout(self)
        self.builder.warn('inline latex %r: ' % node['latex'] + str(exc))
        raise nodes.SkipNode
    self.body.append(self.starttag(node, 'div', CLASS='circuit'))
    self.body.append('<p>')
    if node['number']:
        self.body.append('<span class="eqno">(%s)</span>' % node['number'])
    if fname is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="circuit">%s</span></p>\n</div>' %
                         self.encode(node['latex']).strip())
    else:
        self.body.append('<img src="%s"' % fname + '/><p>\n</div>')
    raise nodes.SkipNode

def latex_visit_circuit(self, node):
    self.body.append('$' + node['latex'] + '$')
    raise nodes.SkipNode

def latex_visit_displaycircuit(self, node):
    self.body.append(node['latex'])
    raise nodes.SkipNode

def text_visit_circuit(self, node):
    self.add_text(node['latex'])
    raise nodes.SkipNode

def text_visit_displaycircuit(self, node):
    self.new_state()
    self.add_text(node['latex'])
    self.end_state()
    raise nodes.SkipNode

def man_visit_circuit(self, node):
    self.body.append(node['latex'])
    raise nodes.SkipNode

def man_visit_displaycircuit(self, node):
    self.visit_centered(node)

def man_depart_displaycircuit(self, node):
    self.depart_centered(node)

def number_equations(app, doctree, docname):
    num = 0
    numbers = {}
    for node in doctree.traverse(displaycircuit):
        if node['label'] is not None:
            num += 1
            node['number'] = num
            numbers[node['label']] = num
        else:
            node['number'] = None

def setup(app):
    app.add_config_value('circuit_dvipng', 'dvipng', 'html')
    app.add_config_value('circuit_latex', 'latex', 'html')
    app.add_config_value('circuit_dvipng_args',
                         ['-gamma 1.5', '-D 110'], 'html')
    app.add_config_value('circuit_latex_args', [], 'html')
    app.add_config_value('circuit_latex_preamble', '', 'html')
    app.add_node(circuit,
                 latex=(latex_visit_circuit, None),
                 text=(text_visit_circuit, None),
                 man=(man_visit_circuit, None),
                 html=(html_visit_circuit,None))
    app.add_node(displaycircuit,
                 latex=(latex_visit_displaycircuit, None),
                 text=(text_visit_displaycircuit, None),
                 man=(man_visit_displaycircuit, man_depart_displaycircuit),
                 html=(html_visit_displaycircuit,None))
    app.add_directive('circuit', CircuitDirective)
    app.connect('doctree-resolved', number_equations)

 
