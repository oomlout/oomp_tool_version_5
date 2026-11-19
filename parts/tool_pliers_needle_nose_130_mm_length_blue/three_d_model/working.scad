// Blue needle-nose pliers, 130 mm
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([0, 0, 0])
        linear_extrude(height=10) polygon(points=[[-17, 0], [-17, 54], [-46, 93], [-50, 125], [50, 125], [46, 93], [17, 54], [17, 0]]);
}
