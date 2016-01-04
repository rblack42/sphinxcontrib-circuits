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

class RailExtError(SphinxError):
    category = 'Rail extension error'

    def __init__(self, msg, stderr=None, stdout=None):
        if stderr:
            msg += '\n[stderr]\n' + stderr
        if stdout:
            msg += '\n[stdout]\n' + stdout
        SphinxError.__init__(self, msg)


DOC_HEAD = r'''\documentclass[11pt]{article}
\usepackage{rail}
\pagestyle{empty}
\railoptions{+ac}
\railalias{quote}{'}
\railalias{dquote}{"}
\railalias{cr}{\char"5C"\char"5C}
\railterm{quote,dquote,cr}
\railalias{lbrace}{\{}
\railalias{rbrace}{\}}
\railalias{underscore}{\_}
\railterm{lbrace,rbrace,underscore}
\newcommand\Rail{rail}
\newcommand\nt[1]{\textit{#1}}
\newcommand\file[1]{\textit{file}\textt{.#1}}
\newcommand\lit[1]{\textt{#1}}
\newcommand\cs[1]{\lit{\char"5C\relax#1}}
'''

DOC_BODY = r'''
\begin{document}
\begin{rail}
%s
\end{rail}
\end{document}
'''

DOC_BODY_PREVIEW = r'''
\usepackage[active]{preview}
\begin{document}
\begin{preview}
%s
\end{preview}
\end{document}
'''

depth_re = re.compile(r'\[\d+ depth=(-?\d+)\]')

def render_rail(self, rail):

    shasum = "%s.png" % sha(rail.encode('utf-8')).hexdigest()
    relfn = posixpath.join(self.builder.imgpath, 'rail', shasum)
    outfn = path.join(self.builder.outdir, '_images', 'rail', shasum)
    if path.isfile(outfn):
        depth = read_png_depth(outfn)
        return relfn, depth

    # if latex or dvipng has failed once, don't bother to try again
    if hasattr(self.builder, '_rail_warned_latex') or \
       hasattr(self.builder, '_rail_warned_dvipng'):
        return None, None

    latex = DOC_HEAD + self.builder.config.rail_latex_preamble
    latex += (DOC_BODY) % rail

    if not hasattr(self.builder, '_railpng_tempdir'):
        tempdir = self.builder._rail_tempdir = LATEX_BUILD_DIR
    else:
        tempdir = self.builder._rail_tempdir

    tf = codecs.open(path.join(tempdir, 'rail.tex'), 'w', 'utf-8')
    tf.write(latex)
    tf.close()

    ltx_args = [self.builder.config.rail_latex, '--interaction=nonstopmode']
    # add custom args from the config file
    ltx_args.extend(self.builder.config.rail_latex_args)
    ltx_args.append('rail.tex')

    curdir = getcwd()
    chdir(tempdir)

# process this latex script with rail
    try:
        try:
            # first latex run
            p = Popen(ltx_args, stdout=PIPE, stderr=PIPE)
        except OSError, err:
            if err.errno != ENOENT:   # No such file or directory
                raise
            self.builder.warn('LaTeX command %r cannot be run (needed for rail '
                              'display), check the rail_latex setting' %
                              self.builder.config.rail_latex)
            self.builder._rail_warned_latex = True
            return None, None
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise RailExtError('latex exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))          
        print 'first run of latex',ltx_args

        try:
            # first rail run
            rail_args = ['rail','rail']
            p = Popen(rail_args, stdout=PIPE, stderr=PIPE)
        except OSError, err:
            if err.errno != ENOENT:
                raise
            self.builder,warn('Rail command failed')
            self.builder._rail_warned_latex = True
            return None, None
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise RailExtError('rail exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))            
        print 'first rail run:', rail_args  
        try:
            p = Popen(rail_args, stdout=PIPE, stderr=PIPE)
        except OSError, err:
            if err.errno != ENOENT:
                raise
            self.builder,warn('Rail command failed')
            self.builder._rail_warned_latex = True
            return None, None
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise RailExtError('rail exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))            
        print 'second rail run:', rail_args               
        try:
            p = Popen(ltx_args, stdout=PIPE, stderr=PIPE)
        except OSError, err:
            if err.errno != ENOENT:   # No such file or directory
                raise
            self.builder.warn('LaTeX command %r cannot be run (needed for rail '
                              'display), check the rail_latex setting' %
                              self.builder.config.rail_latex)
            self.builder._railpng_warned_latex = True
            return None, None
    finally:
        chdir(curdir)
    print 'second run of latex',ltx_args        

    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise RailExtError('latex exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))

    ensuredir(path.dirname(outfn))

    # Now, convert the image to a PNG file
    # use some standard dvipng arguments
    dvipng_args = [self.builder.config.rail_dvipng]
    dvipng_args += ['-o', outfn, '-T', 'tight', '-z9']
    # add custom ones from config value
    dvipng_args.extend(self.builder.config.rail_dvipng_args)
    # last, the input file name
    dvipng_args.append(path.join(tempdir, 'rail.dvi'))
    try:
        p = Popen(dvipng_args, stdout=PIPE, stderr=PIPE)
        print 'dvipng run',dvipng_args
    except OSError, err:
        if err.errno != ENOENT:   # No such file or directory
            raise
        self.builder.warn('dvipngpng command %r cannot be run (needed for rail '
                          'display), check the rail_dvipng setting' %
                          self.builder.config.rail_dvipng)
        self.builder._rail_warned_dvipng = True
        return None, None
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise RailExtError('dvipng exited with error:\n[stderr]\n%s\n'
                           '[stdout]\n%s' % (stderr, stdout))
    depth = None

    return relfn, depth

class rail(nodes.Inline, nodes.TextElement):
    pass

class displayrail(nodes.Part, nodes.Element):
    pass

class RailDirective(Directive):

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
        node = displayrail()
        node['latex'] = latex
        node['label'] = self.options.get('label', None)
        node['docname'] = self.state.document.settings.env.docname
        ret = [node]
        if node['label']:
            tnode = nodes.target('', '', ids=['equation-' + node['label']])
            self.state.document.note_explicit_target(tnode)
            ret.insert(0, tnode)
        return ret

def html_visit_rail(self, node):
    try:
        fname, depth = render_rail(self, '$'+node['latex']+'$')
    except RailExtError, exc:
        msg = unicode(str(exc), 'utf-8', 'replace')
        sm = nodes.system_message(msg, type='WARNING', level=2,
                                  backrefs=[], source=node['latex'])
        sm.walkabout(self)
        self.builder.warn('display latex %r: ' % node['latex'] + str(exc))
        raise nodes.SkipNode
    if fname is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="rail">%s</span>' %
                         self.encode(node['latex']).strip())
    else:
         c = ('<img class="rail" src="%s"' % fname)
         if depth is not None:
             c += ' style="vertical-align: %dpx"' % (-depth)
         self.body.append( c + '/>')
    raise nodes.SkipNode

def html_visit_displayrail(self, node):
    latex = node['latex']
    try:
        fname, depth = render_rail(self, latex)
    except RailExtError, exc:
        sm = nodes.system_message(str(exc), type='WARNING', level=2,
                                  backrefs=[], source=node['latex'])
        sm.walkabout(self)
        self.builder.warn('inline latex %r: ' % node['latex'] + str(exc))
        raise nodes.SkipNode
    self.body.append(self.starttag(node, 'div', CLASS='rail'))
    self.body.append('<p>')
    if node['number']:
        self.body.append('<span class="eqno">(%s)</span>' % node['number'])
    if fname is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="rail">%s</span></p>\n</div>' %
                         self.encode(node['latex']).strip())
    else:
        self.body.append('<img src="%s"' % fname + '/><p>\n</div>')
    raise nodes.SkipNode

def latex_visit_rail(self, node):
    self.body.append('$' + node['latex'] + '$')
    raise nodes.SkipNode

def latex_visit_displayrail(self, node):
    self.body.append(node['latex'])
    raise nodes.SkipNode

def text_visit_rail(self, node):
    self.add_text(node['latex'])
    raise nodes.SkipNode

def text_visit_displayrail(self, node):
    self.new_state()
    self.add_text(node['latex'])
    self.end_state()
    raise nodes.SkipNode

def man_visit_rail(self, node):
    self.body.append(node['latex'])
    raise nodes.SkipNode

def man_visit_displayrail(self, node):
    self.visit_centered(node)

def man_depart_displayrail(self, node):
    self.depart_centered(node)

def number_equations(app, doctree, docname):
    num = 0
    numbers = {}
    for node in doctree.traverse(displayrail):
        if node['label'] is not None:
            num += 1
            node['number'] = num
            numbers[node['label']] = num
        else:
            node['number'] = None

def setup(app):
    app.add_config_value('rail_dvipng', 'dvipng', 'html')
    app.add_config_value('rail_latex', 'latex', 'html')
    app.add_config_value('rail_dvipng_args',
                         ['-gamma 1.5', '-D 110'], 'html')
    app.add_config_value('rail_latex_args', [], 'html')
    app.add_config_value('rail_latex_preamble', '', 'html')
    app.add_node(rail,
                 latex=(latex_visit_rail, None),
                 text=(text_visit_rail, None),
                 man=(man_visit_rail, None),
                 html=(html_visit_rail,None))
    app.add_node(displayrail,
                 latex=(latex_visit_displayrail, None),
                 text=(text_visit_displayrail, None),
                 man=(man_visit_displayrail, man_depart_displayrail),
                 html=(html_visit_displayrail,None))
    app.add_directive('rail', RailDirective)
    app.connect('doctree-resolved', number_equations)

 
