from enum import Enum
from core.i3d_transform_loader import I3DTransformLoader
from core.i3d_math import *


class ExportMode(Enum):
    SINGLE = "single"      # merge everything
    MULTIPLE = "multiple"  # one group per shape


class WavefrontOBJExporter:
    def __init__(self, shapes, i3d_file=None, name=None, scale=1.0, mode=ExportMode.MULTIPLE):
        if not isinstance(shapes, (list, tuple)):
            shapes = [shapes]

        self.transforms = {}

        self.shapes = shapes
        self.name = name or "export"
        self.scale = scale
        self.mode = mode

        if i3d_file:
            self.transforms = I3DTransformLoader(i3d_file).load()

    def export(self, fp):
        w = fp.write

        # ---- Header ----
        w("# Wavefront OBJx file (extension: 4xUV, VertexColor, multiple Materials)\n")
        w("# Creator: Python I3DShapesTool\n")
        w(f"# Name: {self.name}\n")
        w(f"# Scale: {self.scale}\n\n")

        v_offset = 0
        vt_offset = 0
        vn_offset = 0
        material_id = 1

        if self.mode is ExportMode.SINGLE:
            w("g merged\n")
            w("s off\n")

        for shape in self.shapes:

            shape_transform = self.transforms.get(
                shape.shape_id,
                mat_identity()
            )

            # ---- Vertices ----
            if shape.vertexcolor:
                for (x, y, z), col in zip(shape.positions, shape.vertexcolor):
                    x, y, z = transform_point(shape_transform, x, y, z)
                    w(
                        f"v {x*self.scale:.6f} "
                        f"{y*self.scale:.6f} "
                        f"{z*self.scale:.6f} "
                        f"{col[0]:.6f} {col[1]:.6f} {col[2]:.6f} {col[3]:.6f}\n"
                    )
            else:
                for x, y, z in shape.positions:
                    x, y, z = transform_point(shape_transform, x, y, z)
                    w(f"v {x*self.scale:.6f} {y*self.scale:.6f} {z*self.scale:.6f}\n")

            # ---- UVs ----
            if shape.uvsets:
                if shape.uvsets[0]:
                    for u, v in shape.uvsets[0]:
                        w(f"vt {u:.6f} {v:.6f}\n")

                for idx in range(1, 4):
                    uvs = shape.uvsets[idx] if idx < len(shape.uvsets) else None
                    if uvs:
                        tag = f"vt{idx+1}"
                        for u, v in uvs:
                            w(f"{tag} {u:.6f} {v:.6f}\n")

            # ---- Normals ----
            if shape.normals:
                for x, y, z in shape.normals:
                    w(f"vn {x:.6f} {y:.6f} {z:.6f}\n")

            # ---- Faces ----
            for subset in shape.subsets:
                w(f"usemtl {material_id}\n")
                material_id += 1

                start = subset["FirstIndex"] // 3
                count = subset["NumIndices"] // 3

                for i in range(count):
                    tri = shape.triangles[start + i]
                    self._write_face(
                        w,
                        shape,
                        tri,
                        v_offset,
                        vt_offset,
                        vn_offset
                    )

            # ---- Update offsets ----
            v_offset += len(shape.positions)
            vt_offset += len(shape.uvsets[0]) if shape.uvsets and shape.uvsets[0] else 0
            vn_offset += len(shape.normals) if shape.normals else 0

    def _write_face(self, w, shape, tri, v_off, vt_off, vn_off):
        def v(idx):
            idx += v_off

            has_uv = shape.uvsets and shape.uvsets[0]
            has_n = shape.normals

            if has_uv:
                if has_n:
                    return f"{idx}/{idx+vt_off}/{idx+vn_off}"
                return f"{idx}/{idx+vt_off}"
            else:
                if has_n:
                    return f"{idx}//{idx+vn_off}"
                return f"{idx}"

        w(f"f {v(tri[0])} {v(tri[1])} {v(tri[2])}\n")
