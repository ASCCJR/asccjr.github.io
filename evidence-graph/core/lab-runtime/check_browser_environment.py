"""Check sandboxed Chromium + loopback HTTP capability, not a functional test."""
from contextlib import ExitStack
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import distribution, version
import json
import os
from pathlib import Path
import platform
import sys
import threading

from playwright.sync_api import expect, sync_playwright


PAGE = b'''<!doctype html><html><head><title>Browser capability</title></head>
<body><button id="increment">Increment</button><output id="count">0</output>
<script>document.getElementById('increment').addEventListener('click', () => {
const output = document.getElementById('count');
output.textContent = String(Number(output.textContent) + 1);
});</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(PAGE)))
        self.end_headers()
        self.wfile.write(PAGE)


def record(phase, **state):
    print('EG_BROWSER_CAPABILITY ' + json.dumps({'phase': phase, **state}), flush=True)


def diagnostics():
    """Selected read-only host settings; never modify host protection policies."""
    paths = (
        '/proc/sys/kernel/unprivileged_userns_clone',
        '/proc/sys/user/max_user_namespaces',
        '/proc/sys/kernel/apparmor_restrict_unprivileged_userns',
        '/sys/module/apparmor/parameters/enabled',
    )
    values = {}
    for name in paths:
        try:
            values[name] = Path(name).read_text().strip()
        except OSError as error:
            values[name] = type(error).__name__
    values['process_protection'] = [
        line for line in Path('/proc/self/status').read_text().splitlines()
        if line.startswith(('NoNewPrivs:', 'Seccomp:', 'Seccomp_filters:', 'CapEff:'))
    ]
    record('read-only-diagnostics', **values)


def main():
    package = Path(distribution('playwright').locate_file('playwright/driver/package'))
    browsers = json.loads((package / 'browsers.json').read_text())['browsers']
    expected = next(item for item in browsers if item['name'] == 'chromium')
    options = {'headless': True, 'chromium_sandbox': True}
    record('environment', os_release=Path('/etc/os-release').read_text(),
           platform=platform.platform(), python=sys.version, uid=os.geteuid(),
           playwright=version('playwright'), expected_chromium=expected,
           launch_options=options, debug_launch_logging=os.getenv('DEBUG') == 'pw:browser')
    assert os.geteuid() != 0, 'The browser must run as a non-root user'
    assert version('playwright') == '1.57.0', 'Unexpected Playwright version'
    assert not os.getenv('EG_BROWSER_PATH'), 'A browser executable override is not allowed in this check'
    with ExitStack() as stack:
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def stop_server():
            server.shutdown()
            server.server_close()
            thread.join(5)

        stack.callback(stop_server)
        pw = stack.enter_context(sync_playwright())
        browser = stack.enter_context(pw.chromium.launch(**options))
        record('launched', browser_version=browser.version,
               playwright_executable=pw.chromium.executable_path, launch_options=options)
        assert browser.version == expected['browserVersion'], 'Unexpected Chromium version'
        context = stack.enter_context(browser.new_context())
        page = context.new_page()
        page.set_default_timeout(5000)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        response = page.goto(f'http://127.0.0.1:{server.server_port}/', wait_until='load')
        assert response.status == 200, 'Loopback HTTP did not return 200'
        expect(page.locator('#count')).to_have_text('0')
        page.click('#increment')
        expect(page.locator('#count')).to_have_text('1')
        assert errors == [], errors
        record('http-interaction', http_status=response.status, javascript_count='1', page_errors=errors)
    record('passed', browser_context_and_server_closed=True, functional_test_count=0)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        record('failed', error_type=type(error).__name__, message=str(error))
        diagnostics()
        raise
