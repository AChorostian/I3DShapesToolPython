import os, struct
from core.i3d_cipher import I3DCipher
from core.key import KEY_CONST
import xml.etree.ElementTree as ET
from core.binary_reader import BinaryReader
from core.i3d_part import I3d_shape


class I3d_fileset():
    def __init__(self):
        self.working_directory = None

        self.file_i3d_shapes = None
        self.file_i3d_shapes_stream = None
        self.i3d_shapes_version = None
        self.i3d_shapes_seed = None
        self.i3d_shapes_endian = None
        self.i3d_shapes_cipher = None
        self.i3d_shapes_entities_count = None
        self.i3d_shapes_entities = []

        self.file_i3d = None
        self.file_xml = None

    def validate_files(self, files): 
        """Returns None if validation success or warning message if validation fails"""

        for file in files:
            if not os.path.exists(file):
                return "File " + file + " doesn't exists!"

        self.working_directory = os.path.split(files[0])[0].lower()
        i3d_shapes_files = [f for f in files if f.lower().endswith(".i3d.shapes")]

        if not(len(i3d_shapes_files) == 1):
            return "You can load only one .i3d.shapes file!" 

        self.file_i3d_shapes = os.path.split(i3d_shapes_files[0])[1].lower()
        
        if len(files) == 1:
            return None

        i3d_files = [f for f in files if f.lower().endswith(".i3d")]

        if not(len(i3d_files)==1):
            return "Wrong set of files!"
        if not(self.validate_i3d(i3d_files[0], i3d_shapes_files[0])):
            return "files .i3d and .i3d.shapes are not linked correctly!"

        self.file_i3d = os.path.split(i3d_files[0])[1].lower()

        if len(files) == 2:
            return None
        
        xml_files = [f for f in files if f.lower().endswith(".xml")]

        if not(len(xml_files)==1):
            return "Wrong set of files!"
        if not(self.validate_xml(xml_files[0], i3d_files[0])):
            return "files .xml and .i3d are not linked correctly!"

        self.file_xml = os.path.split(xml_files[0])[1].lower()

        if len(files) == 3:
            return None
        return"Too many files!"
    
    def validate_i3d(self, i3d_file, i3d_shapes_file):
        search = ET.parse(i3d_file).getroot().find(".//Shapes")
        if search is not None:
            expected_i3d_shapes_file = search.attrib["externalShapesFile"].lower()
            actual_i3d_shapes_file = os.path.split(i3d_shapes_file)[1].lower()
            if (actual_i3d_shapes_file == expected_i3d_shapes_file):
                return True
        return False
    
    def validate_xml(self, xml_file, i3d_file):
        search = ET.parse(xml_file).getroot().find(".//base//filename")
        if search is not None:
            expected_i3d_file = search.text.lower()
            actual_i3d_file = os.path.split(i3d_file)[1].lower()
            if (actual_i3d_file == expected_i3d_file):
                return True
        return False
    
    def load_file_i3d_shapes(self):
        self.file_i3d_shapes_stream = open(self.file_i3d_shapes, "rb")

        data = self.file_i3d_shapes_stream.read(4)
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
        
        self.i3d_shapes_version = version
        self.i3d_shapes_seed = seed
        self.i3d_shapes_endian = endian

        self.i3d_shapes_cipher = I3DCipher(seed, KEY_CONST)
        entities_bytes = self.file_i3d_shapes_stream.read(4)
        self.i3d_shapes_entities_count = struct.unpack("<I", self.i3d_shapes_cipher.decrypt_stream(entities_bytes))[0]

    def load_file_i3d_shapes_part(self):
        '''This function can be called only "self.i3d_shapes_entities_count" times'''
        # TODO add limitation for calls number
        type_int = struct.unpack("<I", self.i3d_shapes_cipher.decrypt_stream(self.file_i3d_shapes_stream.read(4)))[0]
        type_str = {1: "Shape", 2: "Spline", 6: "SplineL"}.get(type_int, "Unknown")
        size = struct.unpack("<I", self.i3d_shapes_cipher.decrypt_stream(self.file_i3d_shapes_stream.read(4)))[0]
        data = self.i3d_shapes_cipher.decrypt_stream(self.file_i3d_shapes_stream.read(size))
        reader = BinaryReader(data)
        shape = I3d_shape()
        shape.read(reader, self.i3d_shapes_version)
        self.i3d_shapes_entities.append(shape)

