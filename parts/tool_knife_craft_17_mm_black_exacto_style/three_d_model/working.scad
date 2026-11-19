// Black Exacto-style craft knife, 17 mm
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0.0, 0]) rotate([0, 0, 0])
        linear_extrude(height=27.5) polygon(points=[[-8.5, 0], [-8.5, 160], [8.5, 160], [8.5, 0]]);
}
