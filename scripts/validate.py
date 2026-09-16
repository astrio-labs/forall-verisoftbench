"""Check schema, derived reports, release inventory, and accidental private content."""
from pathlib import Path
import re
from release_data import ROOT, load, require
from summarize import numeric_reports

FILES={
 '.gitignore','README.md','DATA_DICTIONARY.md','RECONCILIATION.md','LICENSE','NOTICE','CITATION.cff','requirements.txt',
 'tasks.csv','reported_results.csv','results.csv','axiom_audits.csv','independent_checks.csv',
 'environment/README.md','environment/benchmark.json','environment/evaluation.json',
 'scripts/release_data.py','scripts/summarize.py','scripts/validate.py',
 'reports/summary.md','reports/summary.json','reports/by_repository.csv','reports/benchmark-results.png'}

def validate(root=ROOT):
    found=set()
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if any(part in {'.git','.venv','__pycache__'} for part in rel.parts):continue
        require(not p.is_symlink(),'Symlink in release')
        if p.is_file():found.add(rel.as_posix())
    require(found==FILES,'Unexpected release inventory '+str(sorted(found^FILES)))
    data=load(root)
    for path,text in numeric_reports(data).items():
        require((root/path).read_text()==text,'Stale report '+path)
    patterns=[r'/(?:Users|home|private/var)/',r'gh[pousr]_[A-Za-z0-9]{20,}',
              r'github_pat_[A-Za-z0-9_]{30,}',r'sk-[A-Za-z0-9_-]{25,}',
              r'-----BEGIN [A-Z ]*PRIVATE KEY-----',r'\b(?:theorem|lemma)\s+\S+\s*[:(]']
    for path in sorted(FILES):
        p=root/path
        if p.suffix=='.png':
            require(p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'),'Invalid plot file')
            continue
        text=p.read_text()
        for pattern in patterns:require(re.search(pattern,text) is None,'Unexpected private content in '+path)
        if p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',text):
                if target.startswith(('https://','http://','#')):continue
                require((p.parent/target.split('#')[0]).exists(),'Broken local link in '+path)
    require(sum(r['artifact_hash_check']=='mismatch' for r in data['results'])==0,'Artifact hash mismatch')
    print(f"Validated {len(FILES)} release files, {len(data['results'])} task records, {len(data['axioms'])} axiom audits, and {len(data['checks'])} independent checks")

if __name__=='__main__':validate()
