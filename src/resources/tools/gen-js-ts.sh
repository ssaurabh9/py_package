#!/usr/bin/env bash

# Base path for all proto tools
readonly PROTO_TOOLS_BASE_PATH="./src/resources/tools"

# Path to proto compiler
readonly PROTOC="${PROTO_TOOLS_BASE_PATH}/protoc"

# Path to binary data proto generator
readonly GEN_BINARY_PROTO="${PROTO_TOOLS_BASE_PATH}/gen-binary-pb.sh"

# Path to the js generator plugin
readonly PROTOC_GEN_JS_PATH="${PROTO_TOOLS_BASE_PATH}/protoc-gen-js"

# Path to the ts generator plugin
readonly PROTOC_GEN_TS_PATH="$(npm root)/.bin/protoc-gen-ts"

# Directory to write generated code to (.js and .d.ts files)
readonly OUT_DIR="./gen/js-ts"

# All the proto files in this package
readonly PROTO_FILES=`find  ./src/ -name \*.proto -print`

# Path to the proto files
readonly PROTO_PATH="./src/protos/"

# Compiling all the protobuf to generate js-ts files.
${PROTOC} \
 --proto_path="${PROTO_PATH}" \
 --plugin="protoc-gen-ts_proto=${PROTOC_GEN_TS_PATH}" \
 --plugin="protoc-gen-js=${PROTOC_GEN_JS_PATH}" \
 --js_out="import_style=commonjs,binary:${OUT_DIR}" \
 --ts_proto_out="${OUT_DIR}" \
 ${PROTO_FILES}

# Generating binary_pb for all the textprotos.
 ${GEN_BINARY_PROTO} \
 --out "${OUT_DIR}"