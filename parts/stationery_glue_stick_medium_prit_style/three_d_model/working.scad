// Medium Prit glue stick
// Geometry follows the holder clearance profile. Its dimensions describe the pocket used in the source design. Physical tool dimensions and fit have yet to be measured.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=96, r1=14, r2=14, $fn=64);
}
