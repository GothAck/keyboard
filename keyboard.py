import openpyscad
import json
import sys

SPACING = 18.5
SIZE = 14

def stabilizer(width):
    stab = openpyscad.Union()
    stab.append(openpyscad.Cube([width, 4.6, 1], center=True))
    lhs = openpyscad.Translate([-width / 2, 0.62, 0])
    lhs.append([
        openpyscad.Cube([6.75, 12.3, 1], center=True).translate([0, 0, 0]),
        openpyscad.Cube([3.3, 1.2, 1], center=True).translate([0, 6.75, 0]),
        openpyscad.Cube([0.82, 2.8, 1], center=True).translate([-3.79, -1.52, 0]),
    ])
    stab.append(lhs)
    rhs = openpyscad.Translate([width / 2, 0.62, 0])
    rhs.append([
        openpyscad.Cube([6.75, 12.3, 1], center=True).translate([0, 0, 0]),
        openpyscad.Cube([3.3, 1.2, 1], center=True).translate([0, 6.75, 0]),
        openpyscad.Cube([0.82, 2.8, 1], center=True).translate([3.79, -1.52, 0]),
    ])
    stab.append(rhs)
    return stab

def plane_key(width, height):
    k = openpyscad.Union()
    cube = openpyscad.Cube([SIZE, SIZE, 1], center=True)
    k.append(cube)
    if width == 2:
        k.append(stabilizer(23.12))
    elif height == 2:
        k.append(stabilizer(23.12).rotate([0, 0, 90]))
    elif width == 6.25:
        k.append(stabilizer(100))
    return k

def key_plate_cutout(lines):
    doc = openpyscad.Translate([0, 0, 0])
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
                continue
            k = plane_key(width, height)
            doc.append(k.translate([SPACING * x, SPACING * (y + next_y), 0]))
            x += 1
            if next_x:
                x += next_x
                next_x = 0
            if next_y:
                next_y = 0
            width = 1
            height = 1
        y += 1
    return doc

def key_plane(lines):
    pass

def main(layout_json):
    with open(layout_json) as fh:
        layout = json.load(fh)


    data = layout[0]
    lines = layout[1:]
    print(f"Generating keyboard {data}")

    doc = openpyscad.Union()

    doc.append(key_plate_cutout(lines))

    doc.write("keyboard.scad")

if __name__ == "__main__":
    layout_json = "layout.json" if len(sys.argv) < 2 else sys.argv[1]
    main(layout_json)