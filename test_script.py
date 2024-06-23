from src.resources.py_strique.strique_protobuf_package import your_proto_file_pb2

def main():
    example = your_proto_file_pb2.Example(id="1234", message="Hello, World!")
    print(example)

if __name__ == "__main__":
    main()


from py_package.src.resources.py_strique.strique_protobuf_package import your_proto_file_pb2