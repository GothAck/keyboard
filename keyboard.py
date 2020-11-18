from openpyscad import Cube, Cylinder, Difference, Translate, Union, Minkowski, Hull, Intersection
import json
import sys
from os import system

SPACING = 18.5
SIZE = 14


def stabilizer(width, depth):
    stab = Union()
    stab.append(Cube([width, 4.6, depth], center=True))
    lhs = Translate([-width / 2, 0.62, 0])
    lhs.append([
        Cube([6.75, 12.3, depth], center=True).translate([0, 0, 0]),
        Cube([3.3, 1.2, depth], center=True).translate([0, 6.75, 0]),
        Cube([0.82 + 0.01, 2.8, depth], center=True).translate([-3.79, -1.52, 0]),
    ])
    stab.append(lhs)
    rhs = Translate([width / 2, 0.62, 0])
    rhs.append([
        Cube([6.75, 12.3, depth], center=True).translate([0, 0, 0]),
        Cube([3.3, 1.2, depth], center=True).translate([0, 6.75, 0]),
        Cube([0.82 + 0.01, 2.8, depth], center=True).translate([3.79, -1.52, 0]),
    ])
    stab.append(rhs)
    return stab


def plane_key(width, height, depth):
    k = Union()
    cube = Cube([SIZE, SIZE, depth], center=True)
    k.append(cube)
    if width == 2:
        k.append(stabilizer(23.12, depth))
    elif height == 2:
        k.append(stabilizer(23.12, depth).rotate([0, 0, 90]))
    elif width == 6.25:
        k.append(stabilizer(100, depth))
    return k


def generate_keys(lines, generate_2=False, break_at=None, break_at_one_before=False, use_width=True):
    y = 0
    for line in lines:
        x = 0
        next_x = 0
        next_y = 0
        width = 1
        height = 1
        for keydef in line:
            if break_at is not None and ((x + 1 + (width if use_width else 0)) * SPACING) > break_at:
                break
            if break_at is not None and ((x + 2 + (width if use_width else 0)) * SPACING) > break_at and break_at_one_before:
                break
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
                if generate_2 and any(key.endswith("2") for key in keydef.keys()):
                    x2 = x
                    y2 = y
                    w2 = 1
                    h2 = 1
                    if "x2" in keydef:
                        x2 += keydef["x2"]
                    if "y2" in keydef:
                        y2 += keydef["y2"]
                    if "w2" in keydef:
                        w2 = keydef["w2"]
                    if "h2" in keydef:
                        h2 = keydef["h2"]
                    yield (x2, y2, w2, h2)
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


def size(lines):
    max_x = 0
    max_y = 0
    for x, y, width, height in generate_keys(lines):
        max_x = max(max_x, x)
        max_y = max(max_y, y)

    return max_x + 1, max_y + 1


def key_plate_box(lines, depth=1):
    doc = Translate([0, 0, 0])
    for x, y, width, height in generate_keys(lines):
        doc.append(
            Cube([SPACING * width, SPACING * height, depth], center=True)
            .translate([SPACING * x, SPACING * y, 0])
        )
    return doc


def key_plate_clip_cutout(lines, depth=1):
    doc = Translate([0, 0, 0])
    for x, y, width, height in generate_keys(lines):
        doc.append([
            Cylinder(d=5, h=depth, center=True)
                .translate([SPACING * x, SPACING * y, 0])
                .translate([0, 6, 0]),
            Cylinder(d=5, h=depth, center=True)
                .translate([SPACING * x, SPACING * y, 0])
                .translate([0, -6, 0]),
        ])
    return doc


def key_plate_cutout(lines, depth=1):
    doc = Translate([0, 0, 0])
    for x, y, width, height in generate_keys(lines):
        k = plane_key(width, height, depth)
        doc.append(k.translate([SPACING * x, SPACING * y, 0]))
    return doc


def upper_cutout(lines, depth=1, break_at=None, break_at_one_before=False, use_width=True):
    doc = Translate([0, 0, 0])
    y = 0
    for x, y, width, height in generate_keys(lines, generate_2=True, break_at=break_at, break_at_one_before=break_at_one_before, use_width=not use_width):
        k = Cube([SPACING * (width if use_width else 1), SPACING * height, depth], center=True)
        doc.append(k.translate([SPACING * x, SPACING * y, 0]))
    return doc


def key_plate_outer_lhs(lines, padding=5):
    return Union().append([
        Hull().append(
            Minkowski().append([
                upper_cutout(lines, depth=4.4, break_at=200, break_at_one_before=True, use_width=True),
                Cube([padding * 2, padding * 2, 0.2]),
            ])
        ),
        Hull().append(
            Minkowski().append([
                upper_cutout(lines, depth=4.4, break_at=250, break_at_one_before=True, use_width=False),
                Cube([padding * 2, padding * 2, 0.2]),
            ])
        ),
        Minkowski().append([
            upper_cutout(lines, depth=4.4, break_at=250, break_at_one_before=False, use_width=True),
            Cube([padding, padding, 0.2]),
        ])
    ])


def key_plate_outer_rhs(lines, padding=5):
    return Difference().append([
        Hull().append(
            Minkowski().append([
                upper_cutout(lines, depth=4.4),
                Cube([padding * 2, padding * 2, 0.2]),
            ])
        ),
        Minkowski().append([
            key_plate_outer_lhs(lines, padding),
            Cube(0.25, center=True)
        ])
    ])


def key_plate_lhs(lines, padding=5):
    doc = Difference()
    doc.append(key_plate_outer_lhs(lines, padding))
    doc.append(
        key_plate_cutout(lines, depth=5)
    )
    doc.append(
        key_plate_clip_cutout(lines, depth=4.5)
            .translate([0, 0, 1.5])
    )
    return doc


def key_plate_rhs(lines, padding=5):
    doc = Difference()
    doc.append(key_plate_outer_rhs(lines, padding))
    doc.append(key_plate_cutout(lines, depth=5))
    doc.append(key_plate_clip_cutout(lines, depth=4.5).translate([0, 0, 1.5]))
    return doc


def upper_plate(lines, padding=5):
    w, h = size(lines)
    w *= SPACING
    h *= SPACING
    w += padding * 2
    h += padding * 2
    doc = Difference()
    doc.append(
        Cube([w, h, 1.5], center=True)
        .translate([-SPACING / 2, -SPACING / 2, 0])
        .translate([-padding, -padding, 0])
        .translate([w / 2, h / 2, 0])
    )
    doc.append(upper_cutout(lines, depth=1.6))
    return doc


def upper_plate_2(lines, padding=5):
    w, h = size(lines)
    w *= SPACING
    h *= SPACING
    w += padding * 2
    h += padding * 2
    doc = Difference()
    doc.append([
        Translate([0, 0, 0]).append([
            Hull().append(
                Minkowski().append([
                upper_cutout(lines, depth=1.5, break_at=210, break_at_one_before=True),
                Cube([padding * 2, padding * 2, 0.01], center=True)
            ])
            ),
            # Hull().append(
                Minkowski().append([
                upper_cutout(lines, depth=1.5, break_at=210),
                Cube([padding * 2, padding * 2, 0.01], center=True)
            ])
            # ),
        ]),
        upper_cutout(lines, depth=1.6, break_at=220),
    ])
    return doc


def convert(filename_bare):
    system(f"openscad -o {filename_bare}.stl {filename_bare}.scad")


def main(layout_json):
    with open(layout_json) as fh:
        layout = json.load(fh)

    data = layout[0]
    lines = layout[1:]
    print(f"Generating keyboard {data}")

    print(f"Size {size(lines)}")

    doc = Translate([0, 0, 0])
    doc.append(key_plate_lhs(lines))
    doc.append(key_plate_rhs(lines, 5).translate([35, 0, 0]))
    doc.write("key_plate.scad")
    # convert("key_plate")
    doc2 = Intersection()
    doc2.append(doc)
    doc2.append(Translate([200, -20, -10]).append(Cube([100, 180, 50])))
    doc2.write("key_plate_test.scad")

    doc = Translate([0, 0, 0])
    doc.append(upper_plate_2(lines))
    doc.write("upper_plate.scad")
    # convert("upper_plate")


if __name__ == "__main__":
    layout_json = "layout.json" if len(sys.argv) < 2 else sys.argv[1]
    main(layout_json)
