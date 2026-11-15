"""Fail-closed source packaging. Never archives a directory or a glob."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

# Intentional, reviewable file-by-file allowlist. Adding a file requires review.
PACKAGE_FILES = (
    'README.md','docs/MATHEMATICS.md','docs/NX2412.md','docs/CATIA-V5-R32.md',
    'docs/VALIDATION.md','docs/RELEASES.md','reference/cases.csv',
    'wrinkle/__init__.py','wrinkle/core.py','wrinkle/__main__.py',
    'cad/nx/wrinkle_dialog.py','cad/catia/WrinkleCore.bas','cad/catia/Launch.bas',
    'cad/catia/UserForm-code.txt','cad/catia/test_core.vbs',
    'tools/__init__.py','tools/run_vbscript_tests.py','tools/package_preview.py','tools/independent_check.py',
    'tests/test_core.py','tests/test_packaging.py','tests/test_cli.py',
)
FORBIDDEN = re.compile(r'\.(?:xls[a-z0-9]*|xlt[a-z0-9]*|xla[a-z0-9]*|ods|ots|numbers|csv)(?:\.|$)',re.I)
MAX_BYTES = 2_000_000


def check_payload(path, data):
    """Reject spreadsheet names, containers and spreadsheet XML, even renamed."""
    if FORBIDDEN.search(path) and path != 'reference/cases.csv':
        raise ValueError('spreadsheet filename prohibited: ' + path)
    if len(data) > MAX_BYTES or b'\x00' in data or data.startswith((b'PK', bytes.fromhex('d0cf11e0a1b11ae1'))):
        raise ValueError('binary/container/oversize payload prohibited: ' + path)
    try:
        content = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ValueError('non UTF-8 payload prohibited: ' + path) from exc
    lowered = content.lower()
    if re.search(r'<(?:[a-z0-9_]+:)?workbook\b', lowered) or ('urn:schemas-microsoft-com:office:' + 'spreadsheet') in lowered:
        raise ValueError('spreadsheet XML prohibited: ' + path)


def audit_index(root):
    """Inspect staged blob bytes (not just working files) before commit/upload."""
    entries = subprocess.check_output(['git','ls-files','--stage','-z'],cwd=root)
    count = 0
    for entry in entries.split(b'\x00'):
        if not entry:
            continue
        metadata, raw_path = entry.split(b'\t',1)
        mode, sha, stage = metadata.decode('ascii').split()
        path = raw_path.decode('utf-8')
        if mode not in ('100644','100755') or stage != '0':
            raise ValueError('non-regular or conflicted staged entry: ' + path)
        data = subprocess.check_output(['git','cat-file','blob',sha],cwd=root)
        check_payload(path,data)
        count += 1
    return count


def build_preview(root, output, revision):
    root,output = Path(root).resolve(),Path(output)
    if not re.fullmatch('[0-9a-f]{40}',revision):
        raise ValueError('full commit SHA required')
    if output.exists():
        raise ValueError('refusing to overwrite existing package')
    contents = {}
    for name in PACKAGE_FILES:
        path = root/name
        if any((root / Path(*Path(name).parts[:i])).is_symlink() for i in range(1,len(Path(name).parts)+1)):
            raise ValueError('symlink prohibited: '+name)
        if not path.is_file():
            raise ValueError('missing package file: '+name)
        data = path.read_bytes()
        check_payload(name,data)
        contents[name] = data
    manifest = {
        'status':'SOURCE PREVIEW - UNTESTED IN CAD',
        'revision':revision,
        'not_verified':['NX 2412 runtime','CATIA V5 R32 runtime','VBA compilation',
                        'native UI import','CAD licenses','workstation installation'],
        'sha256':{name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},
    }
    contents['MANIFEST.json'] = json.dumps(manifest,indent=2,sort_keys=True).encode('utf-8')
    # All validation above precedes any output. Write exclusively; remove on failure.
    try:
        with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as archive:
            for name,data in contents.items():
                info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o100644 << 16
                archive.writestr(info,data)
        validate_archive(output)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return hashlib.sha256(output.read_bytes()).hexdigest()


def validate_archive(path):
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(PACKAGE_FILES)|{'MANIFEST.json'}:
            raise ValueError('archive does not match exact allowlist')
        if any(i.file_size > MAX_BYTES or (i.external_attr >> 16) & 0o170000 != 0o100000 for i in archive.infolist()):
            raise ValueError('archive contains unsafe size/type')
        manifest=json.loads(archive.read('MANIFEST.json'))
        if manifest.get('status') != 'SOURCE PREVIEW - UNTESTED IN CAD' or set(manifest['sha256']) != set(PACKAGE_FILES):
            raise ValueError('invalid preview manifest')
        if not re.fullmatch('[0-9a-f]{40}',manifest.get('revision','')):
            raise ValueError('invalid revision')
        for name in PACKAGE_FILES:
            data=archive.read(name)
            check_payload(name,data)
            if hashlib.sha256(data).hexdigest() != manifest['sha256'][name]:
                raise ValueError('checksum mismatch: '+name)
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['audit','build','verify'])
    parser.add_argument('--archive',type=Path,default=Path('dist/wrinkle-source-preview.zip'))
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    if args.action == 'verify':
        print(json.dumps(validate_archive(args.archive),indent=2))
        return
    count=audit_index(root)
    print('PASS: staged source audit ('+str(count)+' regular files)')
    if args.action == 'build':
        if subprocess.check_output(['git','status','--porcelain'],cwd=root).strip():
            raise ValueError('build requires a clean checkout of a verified commit')
        revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
        args.archive.parent.mkdir(parents=True,exist_ok=True)
        digest=build_preview(root,args.archive,revision)
        checksum=args.archive.with_suffix('.sha256')
        checksum.write_text(digest+'  '+args.archive.name+'\n',encoding='ascii')
        print('PASS: '+str(args.archive)+' SHA256 '+digest)

if __name__ == '__main__': main()
