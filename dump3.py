import sys
with open('webhooks/__init__.py') as f:
    text = f.read()
idx = text.find('def list_records(self):')
if idx == -1:
    print("NOT FOUND")
else:
    # print from there to end, but only a chunk
    chunk = text[idx:]
    sys.stdout.write(chunk[:4000])
