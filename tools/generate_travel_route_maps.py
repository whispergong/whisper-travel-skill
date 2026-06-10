#!/usr/bin/env python3
import json
import math
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / ".codex-output" / "routes"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def amap_key() -> str:
    config = Path.home() / ".codex" / "config.toml"
    text = config.read_text()
    match = re.search(r'AMAP_MAPS_API_KEY\s*=\s*"([^"]+)"', text)
    if not match:
        raise RuntimeError("AMAP_MAPS_API_KEY not found in Codex MCP config")
    return match.group(1)


KEY = amap_key()


def get_json(endpoint: str, params: dict) -> dict:
    params = dict(params)
    params["key"] = KEY
    params["output"] = "json"
    url = endpoint + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def driving(origin: tuple[float, float], destination: tuple[float, float], waypoints: list[tuple[float, float]] | None = None) -> tuple[list[tuple[float, float]], int, int, list[str]]:
    params = {
        "origin": f"{origin[0]},{origin[1]}",
        "destination": f"{destination[0]},{destination[1]}",
        "extensions": "all",
        "strategy": "0",
    }
    if waypoints:
        params["waypoints"] = ";".join(f"{p[0]},{p[1]}" for p in waypoints)
    data = get_json("https://restapi.amap.com/v3/direction/driving", params)
    if data.get("status") != "1":
        raise RuntimeError(f"driving failed: {data.get('info')} {data.get('infocode')}")
    path = data["route"]["paths"][0]
    points: list[tuple[float, float]] = []
    roads: list[str] = []
    for step in path["steps"]:
        road = step.get("road")
        if road and road not in roads:
            roads.append(road)
        for item in step.get("polyline", "").split(";"):
            if not item:
                continue
            lon, lat = item.split(",")
            points.append((float(lon), float(lat)))
    return points, int(path["distance"]), int(path["duration"]), roads[:5]


def mercator(lon: float, lat: float, zoom: int) -> tuple[float, float]:
    scale = 256 * (2**zoom)
    x = (lon + 180.0) / 360.0 * scale
    lat = max(min(lat, 85.05112878), -85.05112878)
    rad = math.radians(lat)
    y = (1.0 - math.log(math.tan(rad) + 1 / math.cos(rad)) / math.pi) / 2.0 * scale
    return x, y


def choose_view(points: list[tuple[float, float]], width: int, height: int) -> tuple[tuple[float, float], int]:
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    center = ((min(lons) + max(lons)) / 2, (min(lats) + max(lats)) / 2)
    for zoom in range(12, 3, -1):
        projected = [mercator(lon, lat, zoom) for lon, lat in points]
        xs = [p[0] for p in projected]
        ys = [p[1] for p in projected]
        if max(xs) - min(xs) <= width * 0.68 and max(ys) - min(ys) <= height * 0.55:
            return center, zoom
    return center, 4


def static_map(center: tuple[float, float], zoom: int, points: list[tuple[float, float]], anchors: list[dict], width: int, height: int, out: Path) -> None:
    sampled = points
    # Static map URL length is finite; downsample long polylines while keeping shape.
    if len(sampled) > 420:
        stride = math.ceil(len(sampled) / 420)
        sampled = sampled[::stride]
        if sampled[-1] != points[-1]:
            sampled.append(points[-1])
    path = ";".join(f"{lon:.6f},{lat:.6f}" for lon, lat in sampled)
    markers = []
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, anchor in enumerate(anchors):
        lon, lat = anchor["coord"]
        label = labels[i] if i < len(labels) else str(i + 1)
        color = "0xE53935" if i == 0 else ("0x00A870" if i == len(anchors) - 1 else "0x2F6BFF")
        markers.append(f"large,{color},{label}:{lon},{lat}")
    params = {
        "location": f"{center[0]:.6f},{center[1]:.6f}",
        "zoom": str(zoom),
        "size": f"{width}*{height}",
        "traffic": "0",
        "paths": f"10,0x2F6BFF,0.85,,:{path}",
        "markers": "|".join(markers),
        "key": KEY,
    }
    url = "https://restapi.amap.com/v3/staticmap?" + urllib.parse.urlencode(params, safe="|,:;")
    with urllib.request.urlopen(url, timeout=30) as response:
        out.write_bytes(response.read())


def font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for item in candidates:
        if Path(item).exists():
            return ImageFont.truetype(item, size)
    return ImageFont.load_default()


def overlay_labels(path: Path, points: list[tuple[float, float]], anchors: list[dict], center: tuple[float, float], zoom: int, distance: int, duration: int) -> None:
    image = Image.open(path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    w, h = image.size
    cx, cy = mercator(center[0], center[1], zoom)
    f_label = font(24)
    f_small = font(21)
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    occupied: list[tuple[int, int, int, int]] = []

    def to_px(coord: tuple[float, float]) -> tuple[int, int]:
        x, y = mercator(coord[0], coord[1], zoom)
        return int(w / 2 + (x - cx) * 2), int(h / 2 + (y - cy) * 2)

    def intersects(rect):
        x1, y1, x2, y2 = rect
        return x1 < 0 or y1 < 0 or x2 > w or y2 > h or any(not (x2 < a or x1 > c or y2 < b or y1 > d) for a, b, c, d in occupied)

    offsets = [(18, -58), (18, 18), (-190, -58), (-190, 18), (18, -104), (-190, -104)]
    for i, anchor in enumerate(anchors):
        x, y = to_px(anchor["coord"])
        label = f"{labels[i] if i < len(labels) else i + 1} {anchor['name']}"
        bbox = draw.textbbox((0, 0), label, font=f_label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        chosen = None
        for ox, oy in offsets:
            x1 = max(8, min(w - tw - 32, x + ox))
            y1 = max(8, min(h - th - 26, y + oy))
            rect = (x1, y1, x1 + tw + 24, y1 + th + 18)
            if not intersects(rect):
                chosen = rect
                break
        if chosen is None:
            x1 = max(8, min(w - tw - 32, x + 18))
            y1 = max(8, min(h - th - 26, y + 18))
            chosen = (x1, y1, x1 + tw + 24, y1 + th + 18)
        draw.rounded_rectangle(chosen, radius=9, fill=(255, 255, 255, 226), outline=(47, 107, 255, 210), width=3)
        draw.text((chosen[0] + 12, chosen[1] + 8), label, font=f_label, fill=(31, 41, 55, 255))
        occupied.append(chosen)

    info = f"{distance / 1000:.0f} km / {duration / 3600:.1f} h"
    bbox = draw.textbbox((0, 0), info, font=f_small)
    rect = (18, h - 58, 18 + bbox[2] - bbox[0] + 26, h - 18)
    draw.rounded_rectangle(rect, radius=8, fill=(255, 255, 255, 224), outline=(47, 107, 255, 180), width=2)
    draw.text((31, h - 51), info, font=f_small, fill=(31, 41, 55, 255))
    image.convert("RGB").save(path, quality=95)


ROUTES = [
    {
        "day": "D16",
        "alt": "D16 喀什到阿克苏自驾路线图",
        "anchors": [
            {"name": "喀什", "coord": (75.993936, 39.468230)},
            {"name": "阿克苏", "coord": (80.299036, 41.192810)},
        ],
    },
    {
        "day": "D21",
        "alt": "D21 那拉提到伊宁自驾路线图",
        "anchors": [
            {"name": "那拉提", "coord": (84.003822, 43.328259)},
            {"name": "伊宁", "coord": (81.277715, 43.908021)},
        ],
    },
    {
        "day": "D26",
        "alt": "D26 贾登峪到乌鲁木齐自驾路线图",
        "anchors": [
            {"name": "贾登峪", "coord": (87.089700, 48.506800)},
            {"name": "布尔津", "coord": (86.875043, 47.701892)},
            {"name": "乌鲁木齐", "coord": (87.616848, 43.825592)},
        ],
    },
    {
        "day": "D27",
        "alt": "D27 乌鲁木齐到吐鲁番自驾路线图",
        "anchors": [
            {"name": "乌鲁木齐", "coord": (87.616848, 43.825592)},
            {"name": "达坂城", "coord": (88.311099, 43.363668)},
            {"name": "吐鲁番", "coord": (89.189655, 42.951384)},
        ],
    },
    {
        "day": "D31",
        "alt": "D31 敦煌经瓜州雕塑群到酒泉自驾路线图",
        "anchors": [
            {"name": "敦煌", "coord": (94.661967, 40.142128)},
            {"name": "瓜州雕塑群", "coord": (95.776400, 40.514800)},
            {"name": "嘉峪关", "coord": (98.227304, 39.802397)},
            {"name": "酒泉", "coord": (98.494352, 39.732819)},
        ],
    },
    {
        "day": "D32",
        "alt": "D32 酒泉到张掖七彩丹霞自驾路线图",
        "anchors": [
            {"name": "酒泉", "coord": (98.494352, 39.732819)},
            {"name": "七彩丹霞", "coord": (100.061300, 38.971900)},
            {"name": "张掖", "coord": (100.449818, 38.924766)},
        ],
    },
    {
        "day": "D33",
        "alt": "D33 张掖到祁连自驾路线图",
        "anchors": [
            {"name": "张掖", "coord": (100.449818, 38.924766)},
            {"name": "峨堡", "coord": (100.917600, 37.953500)},
            {"name": "祁连", "coord": (100.253211, 38.177112)},
        ],
    },
    {
        "day": "D34",
        "alt": "D34 祁连到门源到兰州自驾路线图",
        "anchors": [
            {"name": "祁连", "coord": (100.253211, 38.177112)},
            {"name": "门源", "coord": (101.622364, 37.376449)},
            {"name": "兰州", "coord": (103.834249, 36.061100)},
        ],
    },
]


def main() -> None:
    manifest = []
    for route in ROUTES:
        anchors = route["anchors"]
        origin = anchors[0]["coord"]
        destination = anchors[-1]["coord"]
        waypoints = [a["coord"] for a in anchors[1:-1]]
        points, distance, duration, roads = driving(origin, destination, waypoints)
        center, zoom = choose_view(points + [a["coord"] for a in anchors], 1024, 620)
        out = OUT_DIR / f"{route['day']}_route_clean.png"
        static_map(center, zoom, points, anchors, 1024, 620, out)
        overlay_labels(out, points, anchors, center, zoom, distance, duration)
        manifest.append({
            "day": route["day"],
            "alt": route["alt"],
            "file": str(out),
            "distance_m": distance,
            "duration_s": duration,
            "roads": roads,
            "zoom": zoom,
        })
        time.sleep(0.4)
    (OUT_DIR / "manifest_clean.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
