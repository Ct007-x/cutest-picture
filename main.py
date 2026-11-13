# Draws a kawaii kitten with the standard library only and writes it to /output/entry.png (deterministic).
import math, os, struct, zlib

N = 640
buf = [[0.0, 0.0, 0.0] for _ in range(N * N)]

def lerp(a, b, t):
    return a + (b - a) * t

def smooth(d):  # d: signed distance in px (negative inside) -> coverage
    return min(1.0, max(0.0, 0.5 - d))

def paint(x, y, col, a):
    p = buf[y * N + x]
    for i in range(3):
        p[i] = p[i] * (1 - a) + col[i] * a

def shape(cx, cy, ext, dist, col, alpha=1.0):
    cx, cy, ext = cx * N, cy * N, ext * N
    for y in range(max(0, int(cy - ext)), min(N, int(cy + ext) + 1)):
        for x in range(max(0, int(cx - ext)), min(N, int(cx + ext) + 1)):
            c = smooth(dist(x + 0.5 - cx, y + 0.5 - cy)) * alpha
            if c > 0:
                paint(x, y, col, c)

def ellipse(cx, cy, rx, ry, col, alpha=1.0, ang=0.0):
    rx, ry = rx * N, ry * N
    ca, sa = math.cos(ang), math.sin(ang)
    def d(px, py):
        u, v = px * ca + py * sa, -px * sa + py * ca
        k = math.hypot(u / rx, v / ry)
        return (k - 1) * min(rx, ry)
    shape(cx, cy, max(rx, ry) / N + 0.01, d, col, alpha)

def heart(cx, cy, s, col, alpha=1.0):
    def d(px, py):
        x, y = px / (s * N), -py / (s * N) + 0.25
        x, y = x * 1.2, y * 1.2
        f = (x * x + y * y - 1) ** 3 - x * x * y ** 3
        return f * s * N * 2.2
    shape(cx, cy, s * 1.6, d, col, alpha)

def sparkle(cx, cy, r, col, alpha=1.0):
    def d(px, py):
        return (math.sqrt(abs(px) / (r * N)) + math.sqrt(abs(py) / (r * N)) - 1) * r * N * 0.5
    shape(cx, cy, r * 1.1, d, col, alpha)

# background: pink -> cream gradient
for y in range(N):
    t = y / (N - 1)
    c = (lerp(255, 255, t), lerp(214, 240, t), lerp(228, 232, t))
    for x in range(N):
        buf[y * N + x] = list(c)
# soft polka dots
for i in range(7):
    for j in range(7):
        if (i + j) % 2 == 0:
            ellipse(i / 6.0, j / 6.0, 0.045, 0.045, (255, 255, 255), 0.35)

CREAM, PINK, DARK = (255, 246, 236), (255, 170, 190), (62, 40, 52)
# body, tail, ears, head
ellipse(0.5, 0.90, 0.22, 0.15, CREAM)
ellipse(0.80, 0.82, 0.05, 0.12, CREAM, 1.0, 0.6)
ellipse(0.27, 0.31, 0.085, 0.13, CREAM, 1.0, -0.45)
ellipse(0.73, 0.31, 0.085, 0.13, CREAM, 1.0, 0.45)
ellipse(0.28, 0.32, 0.05, 0.085, PINK, 1.0, -0.45)
ellipse(0.72, 0.32, 0.05, 0.085, PINK, 1.0, 0.45)
ellipse(0.5, 0.56, 0.33, 0.27, CREAM)
# forehead stripes
for dx in (-0.05, 0.0, 0.05):
    ellipse(0.5 + dx, 0.34, 0.012, 0.04, (240, 170, 120), 0.9, dx * 6)
# paws holding a heart
heart(0.5, 0.82, 0.07, (255, 90, 130))
ellipse(0.40, 0.84, 0.05, 0.04, CREAM)
ellipse(0.60, 0.84, 0.05, 0.04, CREAM)
for px in (0.38, 0.42, 0.58, 0.62):
    ellipse(px, 0.855, 0.006, 0.012, PINK, 0.8)
# eyes
for ex in (0.36, 0.64):
    ellipse(ex, 0.56, 0.06, 0.08, DARK)
    ellipse(ex + 0.018, 0.53, 0.024, 0.03, (255, 255, 255))
    ellipse(ex - 0.016, 0.59, 0.011, 0.014, (255, 255, 255), 0.9)
# blush, nose, mouth, whiskers
for bx in (0.24, 0.76):
    ellipse(bx, 0.66, 0.055, 0.032, (255, 120, 150), 0.55)
ellipse(0.5, 0.625, 0.02, 0.014, (255, 120, 150))
for side in (-1, 1):
    for k in range(0, 21):
        t = k / 20
        x = 0.5 + side * 0.03 * t
        y = 0.64 + 0.028 * math.sin(t * math.pi) * 0.9 + 0.0
        ellipse(x, y, 0.004, 0.004, DARK)
    for wy, wa in ((0.655, 0.12), (0.685, -0.05)):
        for k in range(0, 14):
            t = k / 13
            ellipse(0.5 + side * (0.15 + 0.1 * t), wy + wa * t * side * -1 * 0 + wa * t, 0.0028, 0.0028, (200, 170, 170), 0.9)
# floating hearts and sparkles
for (x, y, s, c) in ((0.12, 0.16, 0.04, (255, 120, 150)), (0.88, 0.12, 0.05, (255, 150, 175)), (0.10, 0.60, 0.03, (255, 150, 175)), (0.92, 0.55, 0.035, (255, 120, 150))):
    heart(x, y, s, c)
for (x, y, r, c) in ((0.2, 0.08, 0.035, (255, 225, 120)), (0.78, 0.22, 0.03, (255, 255, 255)), (0.07, 0.38, 0.03, (255, 255, 255)), (0.93, 0.78, 0.04, (255, 225, 120)), (0.14, 0.82, 0.03, (255, 255, 255))):
    sparkle(x, y, r, c)

raw = bytearray()
for y in range(N):
    raw.append(0)
    for x in range(N):
        raw.extend(int(max(0, min(255, round(v)))) for v in buf[y * N + x])

def chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", N, N, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
with open(os.path.join(out, "entry.png"), "wb") as f:
    f.write(png)
