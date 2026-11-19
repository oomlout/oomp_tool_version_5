// Red side cutters, 110 mm
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0.0, 0]) rotate([0, 0, 0])
        linear_extrude(height=11) polygon(points=[[-11.5, 0], [-11.5, 35], [-33, 60], [-42, 110], [42, 110], [33, 60], [11.5, 35], [11.5, 0]]);
}
