import hashlib
import os
import sys
import inspect
import traceback
import sj

from mitmproxy.script import concurrent
from mitmproxy import http

filename = inspect.getframeinfo(inspect.currentframe()).filename
JALANGI_HOME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(filename)), os.pardir))
WORKING_DIR = os.getcwd()

sys.path.insert(0, JALANGI_HOME + '/scripts')

print("Jalangi home is " + JALANGI_HOME)
print("Current working directory is " + WORKING_DIR)

jalangiArgs = ''
useCache = True
ignore = []


def processFile (flow: http.HTTPFlow, content, ext):
    try:
        url = flow.request.scheme + '://' + flow.request.host + ':' + str(flow.request.port) + flow.request.path
        name = os.path.splitext(flow.request.path_components[-1])[0] \
            if hasattr(flow.request, 'path_components') and len(flow.request.path_components) \
            else 'index'

        hash = hashlib.md5(content).hexdigest()
        fileName = 'cache/' + flow.request.host + '/' + hash + '/' + name + '.' + ext
        instrumentedFileName = 'cache/' + flow.request.host + '/' + hash + '/' + name + '_jalangi_.' + ext
        if not os.path.exists('cache/' + flow.request.host + '/' + hash):
            os.makedirs('cache/' + flow.request.host + '/' + hash)
        if not useCache or not os.path.isfile(instrumentedFileName):
            print('Instrumenting: ' + fileName + ' from ' + url)
            with open(fileName, 'wb') as file:
                file.write(sj.encode_input(content))
            sub_env = { 'JALANGI_URL': url }
            sj.execute(sj.INSTRUMENTATION_SCRIPT + ' ' + jalangiArgs + ' ' + fileName + ' --out ' + instrumentedFileName
                       + ' --outDir ' + os.path.dirname(instrumentedFileName), None, sub_env)
        else:
            print('Already intrumented: ' + fileName + ' from ' + url)
        with open(instrumentedFileName, 'rb') as file:
            data = file.read()
        return data
    except:
        print('Exception in processFile() @ proxy.py')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print(''.join(lines))
        return content


def start():
    global jalangiArgs
    global useCache

    if '--no-cache' in sys.argv:
        print('Cache disabled.')
        useCache = False
        sys.argv.remove('--no-cache')
    elif '--cache' in sys.argv:
        sys.argv.remove('--cache')

    ignoreIdx = sys.argv.index('--ignore') if '--ignore' in sys.argv else -1
    while ignoreIdx >= 0:
        sys.argv.pop(ignoreIdx)
        ignore.append(sys.argv[ignoreIdx])
        sys.argv.pop(ignoreIdx)
        ignoreIdx = sys.argv.index('--ignore') if '--ignore' in sys.argv else -1

    def mapper(p):
        path = os.path.abspath(os.path.join(WORKING_DIR, p))
        return path if not p.startswith('--') and (os.path.isfile(path) or os.path.isdir(path)) else p
    jalangiArgs = ' '.join(map(mapper, [x for x in sys.argv[1:]]))


@concurrent
def response(flow: http.HTTPFlow) -> None:
    for path in ignore:
        if flow.request.url.startswith(path):
            return

    # Do not invoke jalangi if the requested URL contains the query parameter noInstr
    # (e.g. https://cdn.com/jalangi/jalangi.min.js?noInstr=true)
    if flow.request.query and flow.request.query.get('noInstr', None):
        return

    try:
        flow.response.decode()

        content_type = None
        csp_key = None
        for key in flow.response.headers.keys():
            if key.lower() == 'content-type':
                content_type = flow.response.headers[key].lower()
            elif key.lower().startswith('content-security-policy'):
                csp_key = key

        if content_type:
            if content_type.find('javascript') >= 0:
                flow.response.content = processFile(flow, flow.response.content, 'js')
            if content_type.find('html') >= 0:
                flow.response.content = processFile(flow, flow.response.content, 'html')

        if csp_key:
            flow.response.headers.pop(csp_key, None)
    except:
        print('Exception in response() @ proxy.py')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print(''.join(lines))
