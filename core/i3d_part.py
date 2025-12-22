from enum import IntFlag


class I3d_part:
    ENTITY_TYPES = {
        0: "Unknown",
        1: "Shape",
        2: "Spline",
        6: "SplineL"
    }

    def __init__(self):
        self.entity_type = self.ENTITY_TYPES[0]
        self.name = ""
        self.id = 0
        self.contents = []

    def read_header(self, reader):
        name_len = reader.read("<i")
        self.name = reader.read_bytes(name_len).decode("utf-8", errors="replace")
        reader.align()
        self.id = reader.read("<I")

    def read_contents(reader, file_version):
        # to overload
        pass

    def read(self, reader, file_version):
        self.read_header(reader)
        self.read_contents(reader, file_version)

    def write_header(self, writer):
        # TODO
        pass

    def write_contents(self, writer, file_version):
        # to overload
        pass

    def write(self, writer, file_version):
        # TODO
        pass


class Options(IntFlag):
    HAS_NORMALS        = 0b0001
    HAS_UV1            = 0b0010
    HAS_UV2            = 0b0100
    HAS_UV3            = 0b1000
    HAS_UV4            = 0b0001_0000
    HAS_VERTEX_COLOR   = 0b0010_0000
    HAS_SKINNING_INFO  = 0b0100_0000
    HAS_TANGENTS       = 0b1000_0000
    SINGLE_BLEND       = 0b0001_0000_0000
    HAS_GENERIC        = 0b0010_0000_0000


class I3d_shape(I3d_part):
    VERSION_WITH_TANGENTS = 5

    def __init__(self):
        super().__init__()
        self.bounding_volume = []
        self.corner_count = 0
        self.vertex_count = 0
        self.subsets = []
        self.triangles = []
        self.positions = []
        self.normals = []
        self.tangents = []
        self.uvsets = []
        self.vertexcolor = []
        self.blend_weights = []
        self.blend_indices = []
        self.generic_data = []
        self.attachments = []
        self.options_raw = 0
        self.shape_id = self.id

    def read_contents(self, reader, file_version):
        self.bounding_volume = list(reader.read("<4f"))
        self.corner_count = reader.read("<I")
        num_subsets = reader.read("<I")
        self.vertex_count = reader.read("<I")

        self.options_raw = reader.read("<I")
        self.detect_unknown_options()
        options = Options(self.options_raw)

        if file_version >= 10:
            vtx_compression = reader.read("<f")
            print(f"[WARNING] VTX Compression enabled (but not handled): {vtx_compression}")

        for _ in range(num_subsets):
            subset = {}
            subset["FirstVertex"] = reader.read("<I")
            subset["NumVertices"] = reader.read("<I")
            subset["FirstIndex"] = reader.read("<I")
            subset["NumIndices"] = reader.read("<I")

            if file_version >= 6:
                if Options.HAS_UV1 in options:
                    subset["UVDensity1"] = reader.read("<f")
                if Options.HAS_UV2 in options:
                    subset["UVDensity2"] = reader.read("<f")
                if Options.HAS_UV3 in options:
                    subset["UVDensity3"] = reader.read("<f")
                if Options.HAS_UV4 in options:
                    subset["UVDensity4"] = reader.read("<f")
            self.subsets.append(subset)

        if (self.id == 2):
            {}

        if file_version >= 10:
            material_names = []
            for _ in range(num_subsets):
                count = reader.read("<H")

                if count > 0:
                    mat_name_bytes = reader.read_bytes(count)
                    material_names.append(mat_name_bytes.decode("utf-8", errors="replace"))
                else:
                    material_names.append(None)
            reader.align()

            print(material_names)

        for i in range(self.corner_count // 3):
            if self.vertex_count <= 0xFFFF:
                tri = [reader.read("<H") +1 for _ in range(3)]  # ushort
            else:
                tri = [reader.read("<I") +1 for _ in range(3)]  # uint
            self.triangles.append(tri)

        reader.align()

        self.positions = [list(reader.read("<3f")) for _ in range(self.vertex_count)]

        if Options.HAS_NORMALS in options:
            self.normals = [list(reader.read("<3f")) for _ in range(self.vertex_count)]

        if Options.HAS_TANGENTS in options and file_version >= 10:
            self.tangents = [list(reader.read("<4f")) for _ in range(self.vertex_count)]

        for uv_idx in range(4):
            uv_flag = 2 << uv_idx
            if self.options_raw & uv_flag:
                uvs = [list(reader.read("<2f")) for _ in range(self.vertex_count)]
                self.uvsets.append(uvs)
            else:
                self.uvsets.append(None)

        if Options.HAS_VERTEX_COLOR in options:
            self.vertexcolor = [list(reader.read("<4f")) for _ in range(self.vertex_count)]

        if Options.HAS_SKINNING_INFO in options:
            single_blend = Options.SINGLE_BLEND in options
            num_indices = 1 if single_blend else 4

            if not single_blend:
                self.blend_weights = [[reader.read("<f") for _ in range(num_indices)] for _ in range(self.vertex_count)]

            self.blend_indices = [[reader.read("<B") for _ in range(num_indices)] for _ in range(self.vertex_count)]
     
        if Options.HAS_GENERIC in options:
            self.generic_data = [reader.read("<f") for _ in range(self.vertex_count)]

        num_attachments = reader.read("<I")
        self.attachments = [reader.read("<I") for _ in range(num_attachments)]

        print(f"position: {reader.pos}")
        print(f"size: {len(reader.data)}")



        
    def detect_unknown_options(self):
        KNOWN_BITS = sum(flag.value for flag in Options)
        unknown_bits = self.options_raw & ~KNOWN_BITS

        if unknown_bits:
            print(f"[WARNING] Unknown option bits set: {unknown_bits:#010x}")