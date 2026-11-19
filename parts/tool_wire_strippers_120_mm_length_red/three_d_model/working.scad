// Red wire strippers, 120 mm
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0.0, 0]) rotate([0, 0, 0])
        linear_extrude(height=11) polygon(points=[[-17, 0], [-17, 35], [-45, 80], [-55, 120], [55, 120], [45, 80], [17, 35], [17, 0]]);
}
