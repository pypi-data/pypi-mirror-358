import subprocess
import sys
import os
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

class BuildSharedLib(build_ext):
    def run(self):
        # Build your shared lib first
        subprocess.check_call(['make', '-C', 'src/piegy/C_core', 'clean', 'so'])
        # Then continue with normal build_ext run
        super().run()

    def build_extension(self, ext):
        if sys.platform == 'win32':
            lib_name = 'piegyc.dll'
        else:
            lib_name = 'piegyc.so'
        so_path = os.path.abspath(f'src/piegy/C_core/{lib_name}')
        target_path = self.get_ext_fullpath(ext.name)

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        self.copy_file(so_path, target_path)

# Declare the extension module (empty sources)
ext_modules = [
    Extension('piegy.C_core.piegyc', sources=[])
]

setup(
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildSharedLib},
    package_data={"piegy": ["C_core/piegyc.so"]},
    include_package_data=True,
)
