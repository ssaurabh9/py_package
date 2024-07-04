import os
import shutil
import subprocess
from setuptools.command.build_py import build_py

class CustomBuildCommand(build_py):
    def run(self):
        self.run_command("egg_info")
        self.build_proto()
        super().run()

    def build_proto(self):
        print("Compiling proto files...")
        proto_src_dir = os.path.join('src', 'protos')
        proto_dest_dir = os.path.join('src', 'strique_protopy')
        
        if os.path.exists(proto_dest_dir):
            shutil.rmtree(proto_dest_dir)
        os.makedirs(proto_dest_dir)

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
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
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

def build(setup_kwargs):
    """
    This function is mandatory in order to build the extensions.
    """
    setup_kwargs.update(
        {
            "cmdclass": {
                "build_py": CustomBuildCommand,
            },
        }
    )