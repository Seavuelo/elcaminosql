import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from game.version import VERSION


class ReleaseTests(unittest.TestCase):
    def test_install_diagnostic_uses_packaged_resources_without_modifying_seed(self):
        root=Path(__file__).resolve().parents[1]
        seed=root/'database'/'universidad.db'
        before=seed.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            report=Path(folder)/'check.json'
            completed=subprocess.run([sys.executable,str(root/'main.py'),'--check-install',str(report)],
                                     cwd=folder,capture_output=True,text=True,timeout=30)
            self.assertEqual(completed.returncode,0,completed.stderr)
            result=json.loads(report.read_text(encoding='utf8'))
            self.assertTrue(result['success'],result.get('error'))
            self.assertEqual(result['version'],VERSION)
            self.assertEqual(len(result['checks']),4)
        self.assertEqual(seed.read_bytes(),before)
