import math

def mat_identity():
    return [
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1],
    ]


def mat_mul(a, b):
    out = [[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            out[i][j] = sum(a[i][k] * b[k][j] for k in range(4))
    return out


def mat_translate(x, y, z):
    m = mat_identity()
    m[0][3] = x
    m[1][3] = y
    m[2][3] = z
    return m


def mat_scale(x, y, z):
    m = mat_identity()
    m[0][0] = x
    m[1][1] = y
    m[2][2] = z
    return m


def mat_rotate_xyz(rx, ry, rz):
    rx, ry, rz = map(math.radians, (rx, ry, rz))

    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)

    mx = [
        [1,0,0,0],
        [0,cx,-sx,0],
        [0,sx,cx,0],
        [0,0,0,1],
    ]

    my = [
        [cy,0,sy,0],
        [0,1,0,0],
        [-sy,0,cy,0],
        [0,0,0,1],
    ]

    mz = [
        [cz,-sz,0,0],
        [sz,cz,0,0],
        [0,0,1,0],
        [0,0,0,1],
    ]

    return mat_mul(mz, mat_mul(my, mx))


def transform_point(m, x, y, z):
    return (
        m[0][0]*x + m[0][1]*y + m[0][2]*z + m[0][3],
        m[1][0]*x + m[1][1]*y + m[1][2]*z + m[1][3],
        m[2][0]*x + m[2][1]*y + m[2][2]*z + m[2][3],
    )
