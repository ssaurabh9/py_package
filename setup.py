import os
import shutil
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.egg_info import egg_info
import logging

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class CustomBuildCommand(build_py):
    def run(self):
        self.build_proto()
        super().run()

    def build_proto(self):
        print("Compiling proto files...")
        proto_src_dir = 'src/protos'
        proto_dest_dir = 'strique_protopy'
        
        for root, _, files in os.walk(proto_src_dir):
            for file in files:
                if file.endswith('.proto'):
                    proto_file = os.path.join(root, file)
                    try:
                        print(f'Compiling {proto_file}...')
                        subprocess.check_call([
                            'python', '-m', 'grpc_tools.protoc',
                            f'--proto_path={proto_src_dir}',
                            f'--python_out={proto_dest_dir}',
                            proto_file
                        ])
                        print(f'Successfully compiled {proto_file}')
                    except subprocess.CalledProcessError as e:
                        print(f'Failed to compile {proto_file}: {e}')
                elif file.endswith('.binary_pb'):
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(proto_dest_dir, os.path.relpath(src_file, proto_src_dir))
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    shutil.copy(src_file, dest_file)

        # Update __init__.py
        init_file = os.path.join(proto_dest_dir, '__init__.py')
        with open(init_file, 'a') as f:
            for root, _, files in os.walk(proto_dest_dir):
                for file in files:
                    if file.endswith('_pb2.py') or file.endswith('_pb2_grpc.py'):
                        module_name = os.path.splitext(file)[0]
                        relative_path = os.path.relpath(root, proto_dest_dir).replace(os.path.sep, '.')
                        if relative_path == '.':
                            f.write(f'from .{module_name} import *\n')
                        else:
                            f.write(f'from .{relative_path}.{module_name} import *\n')


class CustomEggInfoCommand(egg_info):
    def run(self):
        logging.info("Starting CustomEggInfoCommand.run()")
        if not os.path.exists('strique_protopy'):
            logging.info("Creating strique_protopy directory")
            os.makedirs('strique_protopy')
        else:
            logging.info("strique_protopy directory already exists")
        super().run()
        logging.info("Finished CustomEggInfoCommand.run()")

setup(
    name="strique-protopy",
    version="2.1.1",
    description="Python package for Strique AI with generated protobuf classes and binary_pb files",
    packages=['strique_protopy'],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "grpcio",
        "grpcio-tools",
    ],
    cmdclass={
        'build_py': CustomBuildCommand,
        'egg_info': CustomEggInfoCommand,
    },
    package_data={
        'strique_protopy': ['**/*.py', '**/*.binary_pb'],
    },
)