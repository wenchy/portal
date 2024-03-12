#!/bin/bash

# set -eux
set -e
set -o pipefail

cd "$(git rev-parse --show-toplevel)"

INDIR="./protobuf/protocol"
THIRD_PARTY_PROTO_DIR='./third_party'
OUTDIR="./tools/portal/common/protocol"

rm -fv $OUTDIR/*pb2*.py
mkdir -p $OUTDIR && touch $OUTDIR/__init__.py

python3 -m grpc_tools.protoc \
    --python_out="$OUTDIR" \
    --grpc_python_out="$OUTDIR" \
    --proto_path="$INDIR" \
    --proto_path="$THIRD_PARTY_PROTO_DIR" \
    "$INDIR"/*.proto

for item in "$OUTDIR"/*pb2*.py ; do
    echo "generated: $item"
done

# for item in "$INDIR"/* ; do
#     echo "$item"
#     if [[ -f "$item" ]]; then
#         python3 -m grpc_tools.protoc \
#         --python_out="$OUTDIR" \
#         --grpc_python_out="$OUTDIR" \
#         --proto_path="$INDIR" \
#         "$item"
#     fi
# done