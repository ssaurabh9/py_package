import os
import shutil
import subprocess
from setuptools.command.build_py import build_py
from setuptools.command.egg_info import egg_info
from setuptools.command.install import install
import logging
import re

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

proto_src_dir = 'src/protos'
proto_dest_dir = 'strique_proto_schema'

def compile_protos():
    print("Compiling proto files...")
    
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
            elif file.endswith(('.binary_pb', '.textproto')):
                src_file = os.path.join(root, file)
                dest_file = os.path.join(proto_dest_dir, os.path.relpath(src_file, proto_src_dir))
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                shutil.copy(src_file, dest_file)
                print(f'Copied {src_file} to {dest_file}')

    # Update __init__.py
    init_file = os.path.join(proto_dest_dir, '__init__.py')
    with open(init_file, 'w') as f:
        for root, _, files in os.walk(proto_dest_dir):
            for file in files:
                if file.endswith(('_pb2.py', '.binary_pb')):
                    module_name = os.path.splitext(file)[0]
                    relative_path = os.path.relpath(root, proto_dest_dir).replace(os.path.sep, '.')
                    if relative_path == '.':
                        f.write(f'from .{module_name} import *\n')
                    else:
                        f.write(f'from .{relative_path}.{module_name} import *\n')

def compile_textproto():
    """
    Process textproto files to binary_pb files.
    """
    logging.info("Starting StriqueInstallCommand.process_textproto()")
    print("Processing textproto files...")

    for root, _, files in os.walk(proto_src_dir):
        for file in files:
            if file.endswith('.textproto'):
                textproto_file_path = os.path.join(root, file)
                
                with open(textproto_file_path, 'r') as f:
                    first_line = f.readline().strip()
                    second_line = f.readline().strip()

                if not first_line.startswith('#') or not second_line.startswith('#'):
                    logging.warning(f"SKIPPING: Invalid format in {textproto_file_path}")
                    continue

                logging.info(f"Generating binary file from textproto file for {textproto_file_path}")

                proto_file_path = first_line.replace('# proto-file: ', '')
                message_name = second_line.replace('# proto-message: ', '')

                proto_file_path = f"./{proto_file_path}"

                with open(proto_file_path, 'r') as f:
                    content = f.read()
                    package = re.search(r'^package\s+([^;]+);', content, re.MULTILINE)
                    if package:
                        package = package.group(1)
                    else:
                        logging.error(f"ERROR: Could not find package in {proto_file_path}")
                        continue

                proto_message_name = f"{package}.{message_name}"

                binary_file_path = textproto_file_path.replace('.textproto', '.binary_pb')
                binary_file_path = binary_file_path.replace(proto_src_dir, proto_dest_dir)

                os.makedirs(os.path.dirname(binary_file_path), exist_ok=True)

                try:
                    logging.info(f"Generating binary file for {textproto_file_path}...")
                    subprocess.run([
                        'python', '-m', 'grpc_tools.protoc',
                        f'--proto_path={proto_src_dir}',
                        f'--encode={proto_message_name}',
                        proto_file_path
                    ], input=open(textproto_file_path, 'rb').read(), stdout=open(binary_file_path, 'wb'), check=True)
                    logging.info(f"SUCCESS: Binary file at path {binary_file_path}")
                except subprocess.CalledProcessError as e:
                    logging.error(f"ERROR: Failed to generate binary file for {textproto_file_path}: {e}")


class CustomBuildCommand(build_py):
    def run(self):
        compile_protos()
        compile_textproto()
        super().run()

class CustomEggInfoCommand(egg_info):
    def run(self):
        logging.info("Starting CustomEggInfoCommand.run()")
        if not os.path.exists(proto_dest_dir):
            logging.info(f"Creating {proto_dest_dir} directory")
            os.makedirs(proto_dest_dir)
        else:
            logging.info(f"{proto_dest_dir} directory already exists")
        super().run()
        logging.info("Finished CustomEggInfoCommand.run()")

class CustomInstallCommand(install):
    def run(self):
        compile_protos()
        compile_textproto()
        super().run()