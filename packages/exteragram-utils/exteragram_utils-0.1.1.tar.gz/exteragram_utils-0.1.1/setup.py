import os
import shutil
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info


def generate_py_from_pyi():
    setup_dir = Path(__file__).parent
    typings_dir = setup_dir / "typings"
    py_stubs_dir = setup_dir / "py_stubs"

    if not typings_dir.exists():
        return

    py_stubs_dir.mkdir(exist_ok=True)

    for pyi_file in typings_dir.rglob("*.pyi"):
        rel_path = pyi_file.relative_to(typings_dir)
        py_path = py_stubs_dir / rel_path.with_suffix(".py")

        py_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(pyi_file, py_path)


def copy_typing_files(target_dir):
    generate_py_from_pyi()

    setup_dir = Path(__file__).parent
    py_stubs_dir = setup_dir / "py_stubs"

    if not py_stubs_dir.exists():
        print(f"Warning: py_stubs directory not found at {py_stubs_dir}")
        return

    for py_file in py_stubs_dir.rglob("*.py"):
        rel_path = py_file.relative_to(py_stubs_dir)
        target_path = Path(target_dir) / rel_path

        target_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(py_file, target_path)
        print(f"Copied {rel_path} to {target_path}")


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        copy_typing_files(self.install_lib)


class CustomDevelopCommand(develop):
    def run(self):
        develop.run(self)
        generate_py_from_pyi()

        setup_dir = Path(__file__).parent
        py_stubs_dir = setup_dir / "py_stubs"
        site_packages = Path(self.install_lib)

        if py_stubs_dir.exists():
            for py_file in py_stubs_dir.rglob("*.py"):
                rel_path = py_file.relative_to(py_stubs_dir)
                target_path = site_packages / rel_path

                target_path.parent.mkdir(parents=True, exist_ok=True)

                if not target_path.exists():
                    target_path.symlink_to(py_file)
                    print(f"Linked {rel_path} to {target_path}")


class CustomEggInfoCommand(egg_info):
    def run(self):
        egg_info.run(self)


setup(
    cmdclass={
        "install": CustomInstallCommand,
        "develop": CustomDevelopCommand,
        "egg_info": CustomEggInfoCommand,
    },
)
