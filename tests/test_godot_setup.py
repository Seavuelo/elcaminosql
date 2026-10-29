import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'setup_godot.py'
spec = importlib.util.spec_from_file_location('setup_godot', MODULE)
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class GodotSetupTests(unittest.TestCase):
    def test_extraction_rejects_parent_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / 'bad.zip'
            with zipfile.ZipFile(archive, 'w') as package:
                package.writestr('../escape.txt', 'bad')
            with self.assertRaises(ValueError):
                setup.extract(archive, root / 'engine')
            self.assertFalse((root / 'escape.txt').exists())

    def test_download_rejects_unverified_bytes(self):
        import io
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(setup, 'CACHE', Path(directory)), patch.object(
                    setup.urllib.request, 'urlopen', return_value=io.BytesIO(b'not-the-package')):
                with self.assertRaises(ValueError):
                    setup.download('engine')
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
