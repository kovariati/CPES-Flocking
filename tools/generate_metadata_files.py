"""Generate citation/discovery exports from PROJECT_METADATA.json; stdlib only."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'PROJECT_METADATA.json').read_text())
def put(n,s): (ROOT/n).write_text(s.strip()+'\n',encoding='utf-8')
def cff_author(a):return f'  - family-names: "{a["family"]}"\n    given-names: "{a["given"]}"\n    orcid: "{a["orcid"]}"'
cff=f'''cff-version: 1.2.0
message: "Cite this software version when reusing code; cite the associated manuscript for the formulation. Publication metadata is pending."
title: "{m['software_name']}"
type: software
version: "{m['software_version']}"
license: MIT
repository-code: "{m['repository']}"
authors:
'''+ '\n'.join(cff_author(a) for a in m['software_authors'])
put('CITATION.cff',cff)
auth=' and '.join(a['family']+', '+a['given'] for a in m['article_authors'])
put('CITATION.bib',f'''@unpublished{{KovariRaisz2026CPES,
  author = {{{auth}}},
  title = {{{{{m['article_title']}}}}},
  year = {{{m['year']}}},
  note = {{Manuscript under revision for Results in Engineering}}
}}
@software{{Kovari2026CPESSoftware,
  author = {{Kovari, Attila}},
  title = {{{m['software_name']}}},
  version = {{{m['software_version']}}},
  year = {{{m['year']}}},
  url = {{{m['repository']}}},
  note = {{Prepared revision source snapshot}}
}}''')
put('CITATION.ris',f'''TY  - UNPB
AU  - Kovari, Attila
AU  - Raisz, David
TI  - {m['article_title']}
PY  - {m['year']}
N1  - Manuscript under revision for Results in Engineering
ER  -

TY  - COMP
AU  - Kovari, Attila
TI  - {m['software_name']}
PY  - {m['year']}
ET  - {m['software_version']}
UR  - {m['repository']}
N1  - Prepared revision source snapshot
ER  -''')
def author(a):return {'@type':'Person','givenName':a['given'],'familyName':a['family'],'@id':a['orcid']}
a={'@context':'https://schema.org','@type':'ScholarlyArticle','name':m['article_title'],'author':[author(x) for x in m['article_authors']],'creativeWorkStatus':m['article_status'],'description':'Manuscript under revision for '+m['target_journal']}
put('ARTICLE_METADATA.json',json.dumps(a,indent=2))
c={'@context':['https://schema.org','https://w3id.org/codemeta/3.1'],'@type':'SoftwareSourceCode','name':m['software_name'],'version':m['software_version'],'codeRepository':m['repository'],'license':'https://spdx.org/licenses/MIT','programmingLanguage':'Python','runtimePlatform':'Python 3.12','author':[author(x) for x in m['software_authors']],'keywords':m['keywords'],'developmentStatus':m['software_status'],'citation':a}
put('codemeta.json',json.dumps(c,indent=2))
put('llms.txt',f'''# {m['software_name']}

Version {m['software_version']}; prepared revision source. Related manuscript: {m['article_title']}, by Attila Kovari and David Raisz. No article DOI is assigned in this record.

Repository: {m['repository']}

Read README.md for scientific scope, README_RUNNING.md for execution, CITATION.cff for software citation, and docs/METHOD_TO_CODE_MAP.md for equation mapping. All data are synthetic. The experiments do not validate a deployable CPES controller. This is an optional plain-text index, not a discovery or ranking guarantee.
''')
print('Generated six metadata exports')
