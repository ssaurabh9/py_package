from setuptools import setup, find_packages
import subprocess
import os
import shutil

def build_proto():
    proto_src_dir = 'src/protos'
    proto_dest_dir = 'strique_protopy'
    
    if os.path.exists(proto_dest_dir):
        shutil.rmtree(proto_dest_dir)
    os.makedirs(proto_dest_dir)

    # Compile .proto files and copy .binary_pb files
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
                shutil.copy(src_file, dest_file)

    # Create __init__.py
    init_file = os.path.join(proto_dest_dir, '__init__.py')
    with open(init_file, 'w') as f:
        for root, _, files in os.walk(proto_dest_dir):
            for file in files:
                if file.endswith('_pb2.py') or file.endswith('_pb2_grpc.py'):
                    module_name = os.path.splitext(file)[0]
                    relative_path = os.path.relpath(root, proto_dest_dir).replace(os.path.sep, '.')
                    if relative_path == '.':
                        f.write(f'from .{module_name} import *\n')
                    else:
                        f.write(f'from .{relative_path}.{module_name} import *\n')


setup(
    name='strique-protopy',
    version='0.2.2',
    description='Python package for Strique AI with generated protobuf classes and binary_pb files',
    url='https://github.com/ssaurabh9/py_package',
    packages=['strique_protopy'],
    package_data={'strique_protopy': ['*.py', '*.binary_pb']},
    install_requires=[
        'grpcio',
        'protobuf',
    ],
)