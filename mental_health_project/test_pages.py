import urllib.request
pages = ['/', '/wellbeing-intro', '/user-info', '/assessment', '/sentiment', '/about', '/privacy', '/disclaimer']
for p in pages:
    try:
        req = urllib.request.Request(f'http://localhost:5173{p}')
        with urllib.request.urlopen(req, timeout=3) as resp:
            html = resp.read().decode()
            has_root = 'id="root"' in html
            print(f'{p}: OK (len={len(html)}, has_root={has_root})')
    except Exception as e:
        print(f'{p}: FAIL - {e}')
