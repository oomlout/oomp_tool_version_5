// Round black timer, 80 × 30 mm
// External body envelope from the OOMP timer record. The holder has clearance around both faces and the rim.
// Units: mm
$fn = 64;
union() {
    // Body
    color([0.1843, 0.1804, 0.1961])
    translate([0, 0, 0]) rotate([0, 0, 0])
        cylinder(h=30, r1=40.0, r2=40.0, $fn=64);
}
