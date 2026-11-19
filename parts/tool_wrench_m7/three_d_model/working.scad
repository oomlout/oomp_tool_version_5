// M7 wrench
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0.0, 0]) rotate([0, 0, 0])
        linear_extrude(height=4.5) polygon(points=[[-8, 0], [-8, 110], [8, 110], [8, 0]]);
}
