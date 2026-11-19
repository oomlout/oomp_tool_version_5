// M8 wrench
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0.0, 0]) rotate([0, 0, 0])
        linear_extrude(height=5.5) polygon(points=[[-9, 0], [-9, 120], [9, 120], [9, 0]]);
}
