from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
import numpy as np
import aiohttp
import certifi
import ssl

def rgbtl(rgb):
    rgb_color = sRGBColor(rgb[0], rgb[1], rgb[2], is_upscaled=True)
    lab_color = convert_color(rgb_color, LabColor)
    return lab_color.lab_l, lab_color.lab_a, lab_color.lab_b

def delta(lab1, lab2):
    return np.sqrt((lab1[0] - lab2[0]) ** 2 + (lab1[1] - lab2[1]) ** 2 + (lab1[2] - lab2[2]) ** 2)

def p_similarity(rgb1, rgb2):
    lab1 = rgbtl(rgb1)
    lab2 = rgbtl(rgb2)
    delta_e = delta(lab1, lab2)
    similarity = max(0, 100 - delta_e)
    return similarity

async def avgbg(gradient):
    k = gradient.get("g", {}).get("k", {}).get("k", [])
    if not k or len(k) < 8:
        return None

    colors = []
    for i in range(0, len(k), 4):
        if i + 3 >= len(k):
            break
        r, g, b = k[i + 1:i + 4]
        colors.append((r * 255, g * 255, b * 255))

    if not colors:
        return None

    avg_r = sum(c[0] for c in colors) / len(colors)
    avg_g = sum(c[1] for c in colors) / len(colors)
    avg_b = sum(c[2] for c in colors) / len(colors)
    return (avg_r, avg_g, avg_b)

async def rgbshapes(shapes):
    color_counts = {}

    async def handle_shape(shape):
        nonlocal color_counts
        if shape.get("o", {}).get("k", 100) == 0:
            return

        if shape.get("ty") in {"fl", "st"}:
            k = shape.get("c", {}).get("k", [])
            if isinstance(k, list) and len(k) >= 3:
                r, g, b = [min(max(c * 255, 0), 255) for c in k[:3]]
            elif isinstance(k, dict):
                r, g, b = k.get("r", 0) * 255, k.get("g", 0) * 255, k.get("b", 0) * 255
            else:
                return

            color = (round(r), round(g), round(b))
            if not (color == (0, 0, 0) or color == (255, 255, 255)):
                color_counts[color] = color_counts.get(color, 0) + 1

        elif shape.get("ty") == "gr":
            nested_shapes = shape.get("it", [])
            for nested in nested_shapes:
                await handle_shape(nested)

    for shape in shapes:
        try:
            await handle_shape(shape)
        except Exception:
            continue

    return color_counts

async def dominantcolor(color_counts):
    if not color_counts:
        return (0, 0, 0)
    dominant = max(color_counts.items(), key=lambda x: x[1])[0]
    return dominant

async def color_similarity(url):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            data = await response.json()

    background_layer = next((l for l in data["layers"] if l.get("nm", "").lower() == "background"), None)
    background_color = (0, 0, 0)
    if background_layer:
        for shape in background_layer.get("shapes", []):
            if shape.get("ty") == "gr":
                for item in shape.get("it", []):
                    if item.get("ty") == "gf":
                        avg = await avgbg(item)
                        if avg:
                            background_color = avg
                            break

    gift_ref = next((l.get("refId") for l in data["layers"] if l.get("nm") == "Gift"), None)
    gift_layers = []
    if gift_ref:
        gift_asset = next((a for a in data["assets"] if a.get("id") == gift_ref), None)
        if gift_asset:
            gift_layers = gift_asset.get("layers", [])

    gift_color_counts = {}
    for layer in gift_layers:
        if layer.get("ty") == 4:
            colors = await rgbshapes(layer.get("shapes", []))
            for color, count in colors.items():
                gift_color_counts[color] = gift_color_counts.get(color, 0) + count

    dominant_gift_color = await dominantcolor(gift_color_counts)
    similarity = p_similarity(dominant_gift_color, background_color)

    return {
        "bg": tuple(round(x) for x in background_color),
        "gift": tuple(round(x) for x in dominant_gift_color),
        "similarity": round(similarity, 2)
    }
