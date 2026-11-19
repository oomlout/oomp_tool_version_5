// M21 wrench
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([0, 0, 0])
        linear_extrude(height=10) polygon(points=[[-22, 0], [-22, 140], [22, 140], [22, 0]]);
}
