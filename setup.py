from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import subprocess
import os
import shutil

class BuildProto(build_py):
    def run(self):
        proto_src_dir = 'src/protos'
        proto_dest_dir = 'py_strique/strique_pyproto'
        
        if not os.path.exists(proto_dest_dir):
            os.makedirs(proto_dest_dir)

        # Walk through the proto_src_dir to find all .proto and .binary_pb files
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
                            f'--grpc_python_out={proto_dest_dir}',
                            proto_file
                        ])
                        print(f'Successfully compiled {proto_file}')
                    except subprocess.CalledProcessError as e:
                        print(f'Failed to compile {proto_file}: {e}')
                elif file.endswith('.binary_pb'):
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(proto_dest_dir, os.path.relpath(src_file, proto_src_dir))
                    dest_dir = os.path.dirname(dest_file)
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    try:
                        print(f'Copying {src_file} to {dest_file}...')
                        shutil.copy(src_file, dest_file)
                        print(f'Successfully copied {src_file}')
                    except IOError as e:
                        print(f'Failed to copy {src_file}: {e}')

        # Import generated classes in __init__.py
        init_file = os.path.join(proto_dest_dir, '__init__.py')
        with open(init_file, 'a') as f:
            for root, _, files in os.walk(proto_dest_dir):
                for file in files:
                    if file.endswith('_pb2.py') or file.endswith('_pb2_grpc.py'):
                        module_name = os.path.splitext(file)[0]
                        f.write(f'from .{module_name} import *\n')

        super().run()

setup(
    name='strique_py',
    version='0.1.0',
    description='Python package for Strique AI with generated protobuf classes and binary_pb files',
    packages=find_packages(where='py_strique'),
    package_dir={'': 'py_strique'},
    install_requires=[
        'grpcio',
        'grpcio-tools',
        'protobuf',
    ],
    cmdclass={
        'build_py': BuildProto,
    },
)
