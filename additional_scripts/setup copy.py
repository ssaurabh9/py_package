import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
import logging
import re

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Global Path Variables
proto_src_dir = 'src/protos'
proto_dest_dir = 'strique_proto_schema'

class StriqueInstallCommand(install):
    """
    Custom install command for Strique's Python package.

    This command does the following:
    1. Compiles proto files to Python using protoc.
    2. Processes textproto files to binary_pb files.
    3. Creates a __init__.py file that imports all proto and textproto files.
    4. Deletes original proto files after compilation.
    """

    def run(self):
        """
        Run the custom install command.
        """
        # Ensure destination directory exists
        self.create_dir()

        # Compile proto files
        self.build_proto()

        # Process textproto files
        self.process_textproto()

        # Create init file
        self.create_init()

        # Remove original proto files
        self.remove_original_protos()

        # Run the default install command
        super().run()

    def build_proto(self):
        """
        Compile proto files to Python using protoc.
        """
        logging.info("Starting StriqueInstallCommand.build_proto()")
        print("Compiling proto files...")

        for root, _, files in os.walk(proto_src_dir):
            for file in files:
                if file.endswith('.proto'):
                    proto_file = os.path.join(root, file)
                    try:
                        logging.info(f"Compiling {proto_file}...")
                        subprocess.check_call([
                            'python', '-m', 'grpc_tools.protoc',
                            f'--proto_path={proto_src_dir}',
                            f'--python_out={proto_dest_dir}',
                            proto_file
                        ])
                        logging.info(f"Successfully compiled {proto_file}")
                    except subprocess.CalledProcessError as e:
                        logging.error(f"Failed to compile {proto_file}: {e}")

    def process_textproto(self):
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

    def create_init(self):
        """
        Create a __init__.py file that imports all proto and textproto files.
        """
        logging.info("Starting StriqueInstallCommand.create_init()")

        # Update __init__.py
        init_file = os.path.join(proto_dest_dir, '__init__.py')
        with open(init_file, 'a') as f:
            for root, _, files in os.walk(proto_dest_dir):
                for file in files:
                    if file.endswith('_pb2.py') or file.endswith('.binary_pb'):
                        module_name = os.path.splitext(file)[0]
                        relative_path = os.path.relpath(root, proto_dest_dir).replace(os.path.sep, '.')
                        if relative_path == '.':
                            f.write(f'from .{module_name} import *\n')
                        else:
                            f.write(f'from .{relative_path}.{module_name} import *\n')

    def create_dir(self):
        """
        Create the proto destination directory if it doesn't exist.
        """
        if not os.path.exists(proto_dest_dir):
            logging.info(f"Creating {proto_dest_dir} directory")
            os.makedirs(proto_dest_dir)
        else:
            logging.info(f"{proto_dest_dir} directory already exists")

    def remove_original_protos(self):
        """
        Remove original proto files after compilation.
        """
        logging.info("Starting StriqueInstallCommand.remove_original_protos()")

        for root, _, files in os.walk(proto_src_dir):
            for file in files:
                if file.endswith('.proto') or file.endswith('.textproto'):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        logging.info(f"Removed {file_path}")
                    except OSError as e:
                        logging.error(f"Error removing {file_path}: {e}")

setup(
    name="strique-proto-schema",
    version="13.6.0",
    description="API contracts and Data Transfer Objects (DTO) in the form of Protocol Buffers for Strique binaries.",
    packages=[],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "grpcio",
        "grpcio-tools",
    ],
    cmdclass={
        'install': StriqueInstallCommand,
    },
    include_package_data=True,
    package_data={
        '': ['src/protos/**/*.proto', 'src/protos/**/*.textproto'],
    },
)
