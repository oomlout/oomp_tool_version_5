// Wera 2054 Micro hex screwdriver, 2.5 × 60 mm
// Wera specifies the shaft diameter, shaft length and handle length. The archived OOMP record supplies the 18 mm handle envelope. Grip taper, cap and tip transition are illustrative.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=5, r1=1.4433756729740645, r2=1.4433756729740645, $fn=6);
    translate([0, 5, 0]) rotate([-90, 0, 0])
        cylinder(h=55, r1=2.0, r2=2.0, $fn=64);
    translate([0, 60, 0]) rotate([-90, 0, 0])
        cylinder(h=15.52, r1=4.5, r2=9.0, $fn=64);
    translate([0, 75.52, 0]) rotate([-90, 0, 0])
        cylinder(h=24.25, r1=9.0, r2=6.0, $fn=64);
    translate([0, 99.77, 0]) rotate([-90, 0, 0])
        cylinder(h=37.83, r1=6.0, r2=6.0, $fn=64);
    translate([0, 137.6, 0]) rotate([-90, 0, 0])
        cylinder(h=11.639999999999999, r1=6.0, r2=9.0, $fn=64);
    translate([0, 149.23999999999998, 0]) rotate([-90, 0, 0])
        cylinder(h=7.76, r1=9.0, r2=9.0, $fn=64);
}
