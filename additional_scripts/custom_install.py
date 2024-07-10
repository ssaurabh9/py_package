import subprocess
import os
from setuptools import setup
from setuptools.command.install import install

class CustomInstallCommand(install):
    """Customized setuptools install command - fetches and compiles proto files."""
    
    def run(self):
        # Fetch the proto files from the git repository
        repo_url = "https://github.com/ssaurabh9/py_package.git"
        repo_dir = "py_package"
        proto_dir = os.path.join(repo_dir, "src", "protos")
        
        if not os.path.exists(repo_dir):
            subprocess.check_call(["git", "clone", "--branch", "main", repo_url, repo_dir])

        # Compile the proto files
        proto_files = [os.path.join(proto_dir, f) for f in os.listdir(proto_dir) if f.endswith('.proto')]
        for proto_file in proto_files:
            subprocess.check_call(["protoc", "--python_out=.", proto_file])

        # Run the standard install
        install.run(self)

setup(
    cmdclass={
        'install': CustomInstallCommand,
    },
)
