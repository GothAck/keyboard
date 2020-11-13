import openpyscad
import json
import sys

SPACING = 18.5
SIZE = 14

def main(layout_json):
    with open(layout_json) as fh:
        layout = json.load(fh)

    doc = openpyscad.Union()

    y = 0
    for line in layout[1:]:
        x = 0
        next_x = 0
        next_y = 0
        for key in line:
            if isinstance(key, dict):
                if 'x' in key:
                    x += key['x']
                if 'w' in key:
                    x += (key['w'] - 1) * 0.5
                    next_x = (key['w'] - 1) * 0.5
                if 'y' in key:
                    y += key['y']
                if 'h' in key:
                    next_y += (key['h'] - 1) * 0.5
                continue
            width = 1
            height = 1
            cube = openpyscad.Cube([SIZE, SIZE, 1], center=True).translate([SPACING * x, SPACING * (y + next_y), 0])
            doc.append(cube)
            x += 1
            if next_x:
                x += next_x
                next_x = 0
            if next_y:
                next_y = 0
        y += 1

    doc.write("keyboard.scad")

if __name__ == "__main__":
    layout_json = "layout.json" if len(sys.argv) < 2 else sys.argv[1]
    main(layout_json)