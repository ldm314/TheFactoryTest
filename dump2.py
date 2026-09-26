with open('webhooks/__init__.py') as f:
    text = f.read()
idx = text.find('def list_records(self):')
print(text[idx:])
