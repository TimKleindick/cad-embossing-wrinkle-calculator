import pathlib
import tempfile
import unittest
import zipfile
from tools.package_preview import build_preview, check_payload, validate_archive, audit_index, PACKAGE_FILES
import subprocess
from unittest import mock

class PackagingTests(unittest.TestCase):
    def test_only_exact_allowlist_is_packed_and_manifest_checksums_are_emitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)/'repo';root.mkdir()
            for name in PACKAGE_FILES:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('safe source\n')
            (root/'internal.xlsx').write_bytes(b'PK\x03\x04secret')
            (root/'extra.txt').write_text('private metadata')
            output=pathlib.Path(tmp)/'preview.zip'
            build_preview(root,output,'a'*40)
            with zipfile.ZipFile(output) as z:
                self.assertEqual(set(z.namelist()),set(PACKAGE_FILES)|{'MANIFEST.json'})
                self.assertNotIn(b'private metadata',b''.join(z.read(p) for p in z.namelist()))
                self.assertIn(b'UNTESTED IN CAD',z.read('MANIFEST.json'))

    def test_spreadsheets_disguised_binaries_and_xml_are_rejected(self):
        for path,data in [('x.XLSX',b'ordinary'),('x.xlsm.txt',b'ordinary'),
                          ('x.txt',b'PK\x03\x04xx'),('x.txt',bytes.fromhex('d0cf11e0a1b11ae1')),
                          ('x.txt',b'<?xml version="1.0"?><' + b'workbook xmlns="x"/>'),
                          ('x.txt',b'<ss:' + b'Workbook xmlns:ss="urn:schemas-microsoft-com:office:' + b'spreadsheet"/>'),
                          ('x.txt',b'\x00secret'),('x.csv',b'internal,metadata')]:
            with self.subTest(path=path,data=data),self.assertRaises(ValueError): check_payload(path,data)

    def test_allowlisted_symlink_and_missing_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)/'repo';root.mkdir()
            for name in PACKAGE_FILES:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('safe source\n')
            target=root/PACKAGE_FILES[0];target.unlink()
            with self.assertRaises(ValueError): build_preview(root,pathlib.Path(tmp)/'missing.zip','a'*40)
            secret=pathlib.Path(tmp)/'secret';secret.write_text('internal')
            target.symlink_to(secret)
            with self.assertRaises(ValueError): build_preview(root,pathlib.Path(tmp)/'leak.zip','a'*40)

    def test_failed_build_does_not_leave_publishable_partial_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=pathlib.Path(tmp)/'preview.zip'
            with self.assertRaises(ValueError): build_preview(pathlib.Path(tmp),out,'a'*40)
            self.assertFalse(out.exists())


    def test_staged_blob_audit_cannot_be_bypassed_by_clean_working_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            subprocess.run(['git','init','-q'],cwd=root,check=True)
            file=root/'source.py'
            file.write_bytes(b'PK\x03\x04private')
            subprocess.run(['git','add','source.py'],cwd=root,check=True)
            file.write_text('safe working copy')
            with self.assertRaises(ValueError): audit_index(root)

    def test_archive_tampering_and_extra_entries_are_rejected(self):
        for extra in [False,True]:
            with tempfile.TemporaryDirectory() as tmp:
                root=pathlib.Path(tmp)/'repo';root.mkdir()
                for name in PACKAGE_FILES:
                    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('safe source\n')
                archive=pathlib.Path(tmp)/'preview.zip'
                build_preview(root,archive,'a'*40)
                with zipfile.ZipFile(archive) as z:
                    contents={n:z.read(n) for n in z.namelist()}
                if extra: contents['secret.xlsx']=b'PK\x03\x04secret'
                else: contents['README.md']=b'changed after manifest'
                with zipfile.ZipFile(archive,'w') as z:
                    for name,data in contents.items():
                        info=zipfile.ZipInfo(name);info.external_attr=0o100644 << 16
                        z.writestr(info,data)
                with self.assertRaises(ValueError): validate_archive(archive)


    def test_package_bytes_do_not_depend_on_zip_creator_platform(self):
        # Python's ZipInfo defaults to different creator systems on Windows/Unix.
        # Vary that real dependency default; package contents must stay identical.
        real_info=zipfile.ZipInfo
        class WindowsDefaultInfo(real_info):
            def __init__(self,*args,**kwargs):
                super().__init__(*args,**kwargs)
                self.create_system=0
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)/'repo';root.mkdir()
            for name in PACKAGE_FILES:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('safe source\n')
            one,two=pathlib.Path(tmp)/'unix.zip',pathlib.Path(tmp)/'windows.zip'
            build_preview(root,one,'a'*40)
            with mock.patch.object(zipfile,'ZipInfo',WindowsDefaultInfo):
                build_preview(root,two,'a'*40)
            self.assertEqual(one.read_bytes(),two.read_bytes())

if __name__=='__main__': unittest.main()
