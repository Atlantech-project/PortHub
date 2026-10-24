"""Package the design kit as a zip to send to the UI/UX designer.

    python tools/package_design_kit.py [output-folder]

Refuses to package if the tokens and the code are out of sync. The zip is named
with the version from the newest CHANGELOG entry, for example
ATLANTECH-Design-Kit-1.0.0.zip, and contains:

  design/*            tokens, TOKENS.md, swatches, references, the designer README
  logos/              the 12 master logos
  fonts/              static Montserrat and Inter (installable) with their licences
  CHANGELOG.md
"""
import os, re, subprocess, sys, zipfile

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

check = subprocess.run([sys.executable, os.path.join(KIT, 'tools', 'check_tokens.py')], capture_output=True, text=True)
print(check.stdout.strip())
if check.returncode:
    sys.exit('Not packaging: fix the mismatches above first.')

subprocess.run([sys.executable, os.path.join(KIT, 'tools', 'build_design_assets.py')], check=True)

with open(os.path.join(KIT, 'CHANGELOG.md'), encoding='utf-8') as f:
    m = re.search(r'^## (\d+\.\d+\.\d+)', f.read(), re.M)
if not m:
    sys.exit('CHANGELOG.md needs a "## x.y.z (date)" entry for this version.')
version = m.group(1)

root = f'ATLANTECH-Design-Kit-{version}'
zip_path = os.path.join(out_dir, root + '.zip')
entries = [(os.path.join(KIT, 'CHANGELOG.md'), 'CHANGELOG.md')]
for src, dest in [('design', ''), ('logos', 'logos'), (os.path.join('flutter', 'fonts'), 'fonts')]:
    base = os.path.join(KIT, src)
    for folder, _, files in os.walk(base):
        for name in files:
            full = os.path.join(folder, name)
            rel = os.path.relpath(full, base)
            entries.append((full, os.path.join(dest, rel) if dest else rel))

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for full, rel in sorted(entries, key=lambda e: e[1]):
        z.write(full, f'{root}/{rel}'.replace(os.sep, '/'))

print(f'{zip_path}  ({len(entries)} files, {os.path.getsize(zip_path) / 1e6:.1f} MB)')
