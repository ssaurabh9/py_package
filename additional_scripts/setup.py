import os
import subprocess
import logging
import shutil
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.egg_info import egg_info


protoc_version = "27.2"
protobuf_version = "5.27.2"

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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

class CustomBuildCommand(build_py):
    def run(self):
        logging.info("Starting CustomBuildCommand.run()")
        self.setup_environment()
        self.install_protoc()
        self.build_proto()
        logging.info("Calling super().run()")
        super().run()
        self.cleanup()
        logging.info("Finished CustomBuildCommand.run()")

    def setup_environment(self):
        logging.info("Setting up virtual environment")
        subprocess.check_call(['python3', '-m', 'venv', 'venv'])
        subprocess.check_call(['venv/bin/pip', 'install', '--upgrade', 'pip'])
        subprocess.check_call(['venv/bin/pip', 'install', 'requests', 'protobuf<5'])

    def install_protoc(self):
        logging.info("Downloading and installing protoc compiler")
        PB_REL = "https://github.com/protocolbuffers/protobuf/releases"
        protoc_zip = f'protoc-{protoc_version}-osx-x86_64.zip'
        protoc_url = f"{PB_REL}/download/v{protoc_version}/{protoc_zip}"
        
        # Download protoc
        subprocess.check_call(['curl', '-LO', protoc_url])
        
        # Unzip protoc
        protoc_dest = os.path.expanduser("~/.local")
        subprocess.check_call(['unzip', '-o', protoc_zip, '-d', protoc_dest])
        
        # Update PATH
        os.environ["PATH"] += os.pathsep + os.path.join(protoc_dest, 'bin')
        logging.info("Protoc installed and PATH updated")

    def build_proto(self):
        logging.info("Starting build_proto()")
        print("Compiling proto files...")
        proto_src_dir = 'src/protos'
        proto_dest_dir = 'strique_protopy'
        
        for root, _, files in os.walk(proto_src_dir):
            for file in files:
                if file.endswith('.proto'):
                    proto_file = os.path.join(root, file)
                    try:
                        logging.info(f'Compiling {proto_file}...')
                        subprocess.check_call([
                            'protoc',
                            f'--proto_path={proto_src_dir}',
                            f'--python_out={proto_dest_dir}',
                            proto_file
                        ])
                        logging.info(f'Successfully compiled {proto_file}')
                    except subprocess.CalledProcessError as e:
                        logging.error(f'Failed to compile {proto_file}: {e}')
                elif file.endswith('.textproto'):
                    textproto_file = os.path.join(root, file)
                    logging.info(f'Compiling textproto file: {textproto_file}...')
                    proto_file = os.path.join(root, os.path.splitext(file)[0] + '.proto')
                    logging.info(f'Found corresponding .proto file: {proto_file}')
                    if os.path.exists(proto_file):
                        try:
                            logging.info(f'Compiling {textproto_file}...')
                            subprocess.check_call([
                                'protoc',
                                f'--proto_path={proto_src_dir}',
                                f'--encode={os.path.splitext(file)[0]}',
                                textproto_file,
                                f'--output_dir={proto_dest_dir}'
                            ])
                            logging.info(f'Successfully compiled {textproto_file}')
                        except subprocess.CalledProcessError as e:
                            logging.error(f'Failed to compile {textproto_file}: {e}')
                    else:
                        logging.error(f'No corresponding .proto file found for {textproto_file}')

        # Update __init__.py
        init_file = os.path.join(proto_dest_dir, '__init__.py')
        logging.info(f'Updating {init_file}')
        with open(init_file, 'a') as f:
            for root, _, files in os.walk(proto_dest_dir):
                for file in files:
                    if file.endswith('_pb2.py'):
                        module_name = os.path.splitext(file)[0]
                        relative_path = os.path.relpath(root, proto_dest_dir).replace(os.path.sep, '.')
                        if relative_path == '.':
                            f.write(f'from .{module_name} import *\n')
                        else:
                            f.write(f'from .{relative_path}.{module_name} import *\n')
        logging.info("Finished build_proto()")

    def cleanup(self):
        logging.info("Starting cleanup process")
        print("Cleaning up...")
        
        # Deactivate virtual environment
        deactivate_script = os.path.join('venv', 'bin', 'deactivate')
        if os.path.exists(deactivate_script):
            subprocess.call(['source', deactivate_script])
        
        # Remove directories and files
        directories_to_remove = ['venv', 'strique_protopy', os.path.expanduser("~/.local")]
        for directory in directories_to_remove:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                logging.info(f'Removed directory: {directory}')
        
        files_to_remove = ['protoc-25.1-linux-x86_64.zip']
        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)
                logging.info(f'Removed file: {file}')
        
        logging.info("Cleanup process finished")


setup(
    name="strique-protopy",
    version="1.1.14",
    description="Python package for Strique AI with generated protobuf classes and textproto files",
    packages=['strique_protopy'],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        f"protobuf=={protobuf_version}",
    ],
    cmdclass={
        'build_py': CustomBuildCommand,
        'egg_info': CustomEggInfoCommand,
    },
    package_data={
        'strique_protopy': ['**/*.py', '**/*.textproto'],
    },
)


