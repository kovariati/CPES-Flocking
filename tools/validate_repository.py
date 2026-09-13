"""Check canonical metadata and configuration consistency."""
from pathlib import Path
import json,sys,re
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
print(f'PASS: version {__version__}, configuration and metadata')
