// Medium Prit glue stick
// Representative PLUS Pritt medium NS-702, approximately 20 g and 26 × 95 mm. The red closed body and dark twist base are simplified, with estimated cap and base lengths. The workshop specimen has not been measured.
// Units: mm
$fn = 64;
union() {
    // Twist base
    color([0.1843, 0.1804, 0.1961])
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=6, r1=12.219999999999999, r2=12.219999999999999, $fn=64);
    // Glue stick body
    color([0.6863, 0.1059, 0.1569])
    translate([0, 6, 0]) rotate([-90, 0, 0])
        cylinder(h=61, r1=12.48, r2=12.48, $fn=64);
    // Closed cap
    color([0.6863, 0.1059, 0.1569])
    translate([0, 67, 0]) rotate([-90, 0, 0])
        cylinder(h=28, r1=13.0, r2=13.0, $fn=64);
}
