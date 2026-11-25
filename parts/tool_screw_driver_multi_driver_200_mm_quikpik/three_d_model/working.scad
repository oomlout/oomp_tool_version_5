// Quikpik multi-driver, 200 mm
// Representative Picquic SIXPAC Plus, 200 mm overall and 32 mm handle diameter from a distributor listing. Picquic specifies 3-inch quarter-inch bits and a 7/16-inch hex bolster. Exposed bit, shank and bolster lengths are estimates for the stored-bit pose. The handle contour, stored bits and workshop specimen have not been measured.
// Units: mm
$fn = 64;
union() {
    // Exposed bit
    color([0.5882, 0.5922, 0.5765])
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=57, r1=3.6661742093541236, r2=3.6661742093541236, $fn=6);
    // Shank
    color([0.7176, 0.7216, 0.7059])
    translate([0, 57, 0]) rotate([-90, 0, 0])
        cylinder(h=30, r1=5.0, r2=5.0, $fn=64);
    // Hex bolster
    color([0.7176, 0.7216, 0.7059])
    translate([0, 87, 0]) rotate([-90, 0, 0])
        cylinder(h=17, r1=6.415804866369717, r2=6.415804866369717, $fn=6);
    // Handle
    color([0.1843, 0.1804, 0.1961])
    translate([0, 104, 0]) rotate([-90, 0, 0])
        cylinder(h=96, r1=16.0, r2=16.0, $fn=64);
}
