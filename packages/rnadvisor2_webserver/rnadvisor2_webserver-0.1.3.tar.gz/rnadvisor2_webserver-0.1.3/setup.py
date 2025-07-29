from setuptools import setup
from setuptools.command.install import install
import subprocess
import os
import shutil
from setuptools import find_packages


class CustomInstallCommand(install):
    def run(self):
        install.run(self)

        usalign_src_dir = "build_bin"
        os.makedirs(usalign_src_dir, exist_ok=True)
        cpp_path = os.path.join(usalign_src_dir, "USalign.cpp")
        bin_path = os.path.join(usalign_src_dir, "USalign")

        subprocess.run([
            "wget", "https://zhanggroup.org/US-align/bin/module/USalign.cpp", "-O", cpp_path
        ], check=True)
        subprocess.run([
            "g++", "-O3", "-lm", "-o", bin_path, cpp_path
        ], check=True)
        os.chmod(bin_path, 0o755)

        package_dir = os.path.join(self.install_lib, "rnadvisor2_webserver", "bin")
        os.makedirs(package_dir, exist_ok=True)
        shutil.copy2(bin_path, os.path.join(package_dir, "USalign"))



setup(
    name="rnadvisor2-webserver",
    version="0.1.3",
    packages=find_packages(where="src", include=["rnadvisor2_webserver*"]),
    package_dir={"": "src"},
    include_package_data=True,
    cmdclass={
        'install': CustomInstallCommand,
    },
)
