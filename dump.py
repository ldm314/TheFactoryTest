with open('webhooks/__init__.py') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    print(f"{i}\t{line}", end='')
