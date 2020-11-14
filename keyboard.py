import openpyscad
import json
import sys

SPACING = 18.5
SIZE = 14

def stabilizer(width, depth):
    stab = openpyscad.Union()
    stab.append(openpyscad.Cube([width, 4.6, depth], center=True))
    lhs = openpyscad.Translate([-width / 2, 0.62, 0])
    lhs.append([
        openpyscad.Cube([6.75, 12.3, depth], center=True).translate([0, 0, 0]),
        openpyscad.Cube([3.3, 1.2, depth], center=True).translate([0, 6.75, 0]),
        openpyscad.Cube([0.82, 2.8, depth], center=True).translate([-3.79, -1.52, 0]),
    ])
    stab.append(lhs)
    rhs = openpyscad.Translate([width / 2, 0.62, 0])
    rhs.append([
        openpyscad.Cube([6.75, 12.3, depth], center=True).translate([0, 0, 0]),
        openpyscad.Cube([3.3, 1.2, depth], center=True).translate([0, 6.75, 0]),
        openpyscad.Cube([0.82, 2.8, depth], center=True).translate([3.79, -1.52, 0]),
    ])
    stab.append(rhs)
    return stab

def plane_key(width, height, depth):
    k = openpyscad.Union()
    cube = openpyscad.Cube([SIZE, SIZE, 1], center=True)
    k.append(cube)
    if width == 2:
        k.append(stabilizer(23.12, depth))
    elif height == 2:
        k.append(stabilizer(23.12, depth).rotate([0, 0, 90]))
    elif width == 6.25:
        k.append(stabilizer(100, depth))
    return k

def generate_keys(lines):
    y = 0
    for line in lines:
        x = 0
        next_x = 0
        next_y = 0
        width = 1
        height = 1
        for keydef in line:
            if isinstance(keydef, dict):
                if 'x' in keydef:
                    x += keydef['x']
                if 'w' in keydef:
                    width = keydef['w']
                    x += (width - 1) * 0.5
                    next_x = (width - 1) * 0.5
                if 'y' in keydef:
                    y += keydef['y']
                if 'h' in keydef:
                    height = keydef['h']
                    next_y += (height - 1) * 0.5
                # FIXME: x2, w2, h2
                continue
            yield (x, y + next_y, width, height)
            x += 1
            if next_x:
                x += next_x
                next_x = 0
            if next_y:
                next_y = 0
            width = 1
            height = 1
        y += 1

def key_plate_cutout(lines, depth=1):
    doc = openpyscad.Translate([0, 0, 0])
    for x, y, width, height in generate_keys(lines):
        k = plane_key(width, height, depth)
        doc.append(k.translate([SPACING * x, SPACING * y, 0]))
    return doc

def upper_cutout(lines):
    doc = openpyscad.Translate([0, 0, 0])
    y = 0
    for x, y, width, height in generate_keys(lines):
        k = openpyscad.Cube([SPACING * width, SPACING * height, 1], center=True)
        doc.append(k.translate([SPACING * x, SPACING * y, 0]))
    return doc

def main(layout_json):
    with open(layout_json) as fh:
        layout = json.load(fh)


    data = layout[0]
    lines = layout[1:]
    print(f"Generating keyboard {data}")

    doc = openpyscad.Translate([0, 0, 0])
    doc.append(key_plate_cutout(lines))
    doc.write("key_plate_cutout.scad")

    doc = openpyscad.Translate([0, 0, 0])
    doc.append(upper_cutout(lines))
    doc.write("upper_cutout.scad")

if __name__ == "__main__":
    layout_json = "layout.json" if len(sys.argv) < 2 else sys.argv[1]
    main(layout_json)