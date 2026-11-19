// Stanley 1-30-696 tape measure, 5 m
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([0, 0, 0])
        linear_extrude(height=42) polygon(points=[[-39, 0], [-39, 74], [39, 74], [39, 0]]);
}
