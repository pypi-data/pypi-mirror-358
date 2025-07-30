from setuptools import setup
from setuptools.command.install import install
import subprocess

class CustomInstall(install):
    def run(self):
        install.run(self)
        subprocess.run(['python', '-m', 'exorigsim.main'])

setup(
    name='exorigsim',
    version='0.1.0',
    author='Your Name',
    author_email='you@example.com',
    description='CTF educational package to simulate persistence behaviors',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=['exorigsim'],
    include_package_data=True,
    package_data={'exorigsim': ['dummy.exe', 'watchdog.vbs']},
    cmdclass={'install': CustomInstall},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Topic :: Security",
    ],
    python_requires='>=3.6',
)


