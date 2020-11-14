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

def main(layout_json):
    with open(layout_json) as fh:
        layout = json.load(fh)

    doc = openpyscad.Union()

    y = 0
    for line in layout[1:]:
        x = 0
        next_x = 0
        next_y = 0
        width = 1
        height = 1
        for key in line:
            if isinstance(key, dict):
                if 'x' in key:
                    x += key['x']
                if 'w' in key:
                    width = key['w']
                    x += (width - 1) * 0.5
                    next_x = (width - 1) * 0.5
                if 'y' in key:
                    y += key['y']
                if 'h' in key:
                    height = key['h']
                    next_y += (height - 1) * 0.5
                continue
            key = openpyscad.Translate([SPACING * x, SPACING * (y + next_y), 0])
            cube = openpyscad.Cube([SIZE, SIZE, 1], center=True)
            key.append(cube)
            if width == 2:
                key.append(stabilizer(23.12))
            if height == 2:
                key.append(stabilizer(23.12).rotate([0, 0, 90]))
            if width == 6.25:
                key.append(stabilizer(100))
            doc.append(key)
            x += 1
            if next_x:
                x += next_x
                next_x = 0
            if next_y:
                next_y = 0
            width = 1
            height = 1
        y += 1

    doc.write("keyboard.scad")

if __name__ == "__main__":
    layout_json = "layout.json" if len(sys.argv) < 2 else sys.argv[1]
    main(layout_json)