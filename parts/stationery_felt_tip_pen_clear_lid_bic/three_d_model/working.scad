// BIC clear-lid marker
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=112, r1=5, r2=5, $fn=64);
    translate([0, 112, 0]) rotate([-90, 0, 0])
        cylinder(h=35, r1=6, r2=6, $fn=64);
}
