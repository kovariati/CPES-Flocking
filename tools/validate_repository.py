"""Check canonical metadata, complete tree integrity and configuration consistency."""
from pathlib import Path
import hashlib,json,sys,re
from dataclasses import asdict
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cpes_flocking import __version__
from cpes_flocking.model import Parameters
m=json.loads((ROOT/'PROJECT_METADATA.json').read_text());assert m['software_version']==__version__
assert json.loads((ROOT/'configs/canonical.json').read_text())==asdict(Parameters())
for f in ('ARTICLE_METADATA.json','codemeta.json'):json.loads((ROOT/f).read_text())
assert m['article_title'] in (ROOT/'CITATION.bib').read_text()
assert m['article_title'] in (ROOT/'CITATION.ris').read_text()
assert __version__ in (ROOT/'CITATION.cff').read_text()
assert (ROOT/'LICENSE').read_text().startswith('MIT License')
seen=set()
for line in (ROOT/'manifests/SHA256SUMS.txt').read_text().splitlines():
 h,n=line.split('  ',1);p=ROOT/n;assert p.is_file(),n
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h,'checksum mismatch: '+n
 seen.add(n)
files={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.git','.venv','__pycache__','rerun')) and p.suffix not in ('.pyc','.log')}
assert files==seen|{'manifests/SHA256SUMS.txt'},'unmanifested file or missing path'
print(f'PASS: version {__version__}, configuration, metadata and {len(seen)} file checksums')
