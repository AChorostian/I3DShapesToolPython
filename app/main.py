import struct
import sys, os

from core.i3d_cipher import I3DCipher
from core.binary_reader import BinaryReader
from core.i3d_part import I3d_shape
from core.key import KEY_CONST
from core.exporter import WavefrontOBJExporter
from core.exporter import ExportMode

from gui.main_window import launch_gui

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="{asctime} [{levelname}] {message}", style="{")
logger.setLevel(logging.DEBUG)


def parse_header(data):
    if (data[0] >= 4): # Might be 5 as well 
        version = data[0]
        seed = data[2]
        endian = "little"
    elif (data[3] == 2 or data[3] == 3):
        version = data[3]
        seed = data[1]
        endian = "big"
    else:
        raise Exception("Unknown version")
    if (version < 2 or version > 10):
        raise Exception("Unsupported version")
    return version, seed, endian

def read_entity(cipher: I3DCipher, stream, file_version):
    type_int = struct.unpack("<I", cipher.decrypt_stream(stream.read(4)))[0]
    type_str = {1: "Shape", 2: "Spline", 6: "SplineL"}.get(type_int, "Unknown")

    size = struct.unpack("<I", cipher.decrypt_stream(stream.read(4)))[0]
    data = cipher.decrypt_stream(stream.read(size))

    reader = BinaryReader(data)
    read = reader.read
    read_bytes = reader.read_bytes
    remaining = reader.remaining


    shape = I3d_shape()
    shape.read(reader, file_version)

    return shape


def read_entities(cipher, stream, file_version, count):
    entities_list = []
    for i in range(count):
        e = read_entity(cipher, stream, file_version)
        logger.info(f"Shape {i+1}/{count} loaded.\n")
        entities_list.append(e)
    return entities_list

def export_to_obj(shapes, i3d_file):
    if not os.path.isdir("data/output"):
        os.mkdir("data/output")

    # SINGLE FILES
    for e in shapes:
        with open(f"data/output/{e.id}_{e.name}.obj", "w", encoding="utf-8") as f:
            WavefrontOBJExporter(e, mode=ExportMode.SINGLE).export(f)

    # ONE FILE ONE MESH
    with open(f"data/output/one_file_one_mesh.obj", "w", encoding="utf-8") as f:
        WavefrontOBJExporter(shapes, mode=ExportMode.SINGLE, i3d_file=i3d_file).export(f)

    # ONE FILE MULTI MESH
    with open(f"data/output/one_file_multi_mesh.obj", "w", encoding="utf-8") as f:
        WavefrontOBJExporter(shapes, mode=ExportMode.MULTIPLE, i3d_file=i3d_file).export(f)

def main(args):

    with open(args.shapes_file, "rb") as f:
        version, seed, endian = parse_header(f.read(4))
        print("version: " + str(version))
        print("seed: " + str(seed))
        print("endian: " + str(endian))

        cipher = I3DCipher(seed, KEY_CONST)

        entities_bytes = f.read(4)
        entities_count = struct.unpack("<I", cipher.decrypt_stream(entities_bytes))[0]
        print("entities: " + str(entities_count))

        entities_list = read_entities(cipher, f, version, entities_count)

    # delete componentshapes
    elist_new = []
    for e in entities_list:
        if "Shape" in e.name:
            continue
        elist_new.append(e)

    launch_gui(scene=elist_new)

    export_to_obj(elist_new, args.i3d_file)