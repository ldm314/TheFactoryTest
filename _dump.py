with open('webhooks/__init__.py') as f:
    lines = f.readlines()
print("TOTAL LINES:", len(lines))
for i, l in enumerate(lines):
    s = l.strip()
    if (s.startswith('def ') or s.startswith('class ')):
        print(i, repr(l[:90]))
