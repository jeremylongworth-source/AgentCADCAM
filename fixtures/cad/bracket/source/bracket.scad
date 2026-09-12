// Synthetic, dimensioned OpenSCAD source for CAD/CAM handoff fixtures.
// Units: millimetres. Revision: A.

plate_width = 60;
plate_depth = 40;
plate_thickness = 6;
back_height = 30;
hole_diameter = 6;
hole_offset = 12;

difference() {
    union() {
        cube([plate_width, plate_depth, plate_thickness]);
        cube([plate_width, plate_thickness, back_height]);
    }

    translate([hole_offset, plate_depth / 2, -1])
        cylinder(h = plate_thickness + 2, d = hole_diameter, $fn = 48);
    translate([plate_width - hole_offset, plate_depth / 2, -1])
        cylinder(h = plate_thickness + 2, d = hole_diameter, $fn = 48);
    translate([hole_offset, -1, back_height - hole_offset])
        rotate([-90, 0, 0])
            cylinder(h = plate_thickness + 2, d = hole_diameter, $fn = 48);
    translate([plate_width - hole_offset, -1, back_height - hole_offset])
        rotate([-90, 0, 0])
            cylinder(h = plate_thickness + 2, d = hole_diameter, $fn = 48);
}
