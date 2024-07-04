from setuptools import setup, find_packages, Command
import os
import subprocess

class CustomBuildCommand(Command):
    description = 'Download and compile protobuf files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Download proto files
        subprocess.run(['python', 'src/strique_protopy/custom_install.py'])
        
        # Compile proto files
        subprocess.run(['python', 'src/strique_protopy/build_proto.py'])

setup(
    name='strique-protopy',
    version='0.1.0',
    description='A package that compiles and installs protobuf definitions from a private Git repo',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/strique-protopy',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'protobuf',
        'grpcio-tools',
    ],
    cmdclass={
        'build_py': CustomBuildCommand,
    },
    include_package_data=True,
    zip_safe=False,
)
