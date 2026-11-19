// M13 wrench
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([0, 0, 0])
        linear_extrude(height=8) polygon(points=[[-14, 0], [-14, 160], [14, 160], [14, 0]]);
}
