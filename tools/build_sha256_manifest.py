"""Hash the shipped source tree, excluding local caches and the manifest itself."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'manifests/SHA256SUMS.txt'
files=[p for p in ROOT.rglob('*') if p.is_file() and p!=manifest and not any(x in p.parts for x in ('.git','.venv','__pycache__','rerun')) and p.suffix not in ('.pyc','.log')]
manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in sorted(files)),encoding='utf-8')
print(f'Hashed {len(files)} files')
