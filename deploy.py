import subprocess as sp
import re
import os

LESSC = 'lessc'
JSMIN = 'jsmin'

def compile_less(in_less_file, out_css_file):
    LESSC_OPTS = ['--include-path='+os.path.dirname(in_less_file),'-'] #['--yui-compress', '-']
    print(" compiling %s to %s"%(in_less_file, out_css_file))
    with open(in_less_file, 'rb') as fr:
        with open(out_css_file, 'wb') as fw:
            less_file_dir = os.path.dirname(in_less_file)
            compiler = sp.Popen([LESSC]+LESSC_OPTS,
                                stdin=sp.PIPE,
                                stdout=sp.PIPE)
            stout, sterr = compiler.communicate(fr.read())
            fw.write(stout)
            print(" Wrote %s bytes."% fw.tell())

def parse_args(argsstr):
    argpairs = [x.split('=') for x in argsstr.strip().split(' ')]
    return dict(argpairs)

def match_less_compile(match):
    args = parse_args(match.group(1))
    lessfile = re.findall('href="([^"]+)', match.group(2))[0]
    outfile = args['out']
    compile_less(lessfile, outfile)
    return '<link href="%s" media="all" rel="stylesheet" type="text/css" />' % outfile

def compile_jsmin(instr, outfile):
     with open(outfile, 'wb') as fw:
        compiler = sp.Popen([JSMIN], stdin=sp.PIPE, stdout=sp.PIPE)
        stout, sterr = compiler.communicate(instr)
        fw.write(stout)
        print(" compressed to %s bytes."% fw.tell())

def match_js_concat_min(match):
    args = parse_args(match.group(1))
    jsstr = b''
    for scriptpath in re.findall('<script.*src="([^"]+)"', match.group(2)):
        print('concatenating %s' % scriptpath)
        with open(scriptpath, 'rb') as script:
            jsstr += script.read()
            jsstr += b';\n'
    print('js scripts uncompressed %d bytes' % len(jsstr))
    compile_jsmin(jsstr, args['out'])
    return '<script type="text/javascript" src="%s"></script>' % args['out']

html = None
with open('res/devel.html', 'r') as develhtml:
    html = develhtml.read()

html = re.sub('<!--LESS-TO-CSS-BEGIN([^>]*)-->(.*)<!--LESS-TO-CSS-END-->',
              match_less_compile,
              html,
              flags=re.MULTILINE | re.DOTALL)
html = re.sub('<!--REMOVE-BEGIN-->(.*)<!--REMOVE-END-->',
              '',
              html,
              flags=re.MULTILINE | re.DOTALL)
html = re.sub('<!--COMPRESS-JS-BEGIN([^>]*)-->(.*)<!--COMPRESS-JS-END-->',
              match_js_concat_min,
              html,
              flags=re.MULTILINE | re.DOTALL)


with open('res/main.html', 'w') as mainhtml:
    mainhtml.write(html)