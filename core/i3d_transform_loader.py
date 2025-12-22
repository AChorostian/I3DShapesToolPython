import xml.etree.ElementTree as ET
from core.i3d_math import *

class I3DTransformLoader:
    def __init__(self, filename):
        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()
        self.shape_transforms = {}

    def load(self):
        scene = self.root.find("Scene")
        self._walk(scene, mat_identity())
        return self.shape_transforms

    def _walk(self, node, parent_matrix):
        local = mat_identity()

        if "translation" in node.attrib:
            t = list(map(float, node.attrib["translation"].split()))
            local = mat_mul(mat_translate(*t), local)

        if "rotation" in node.attrib:
            r = list(map(float, node.attrib["rotation"].split()))
            local = mat_mul(mat_rotate_xyz(*r), local)

        if "scale" in node.attrib:
            s = list(map(float, node.attrib["scale"].split()))
            local = mat_mul(mat_scale(*s), local)

        world = mat_mul(parent_matrix, local)

        if node.tag == "Shape" and "shapeId" in node.attrib:
            shape_id = int(node.attrib["shapeId"])
            self.shape_transforms[shape_id] = world

        for child in node:
            self._walk(child, world)