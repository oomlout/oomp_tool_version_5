// 2.5 mm metric hex key
// The holder specifies the hex size. Arm lengths follow the Wiha 350 short series as a representative example. The holder source leaves the key manufacturer unspecified. The elbow is simplified.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=55.75, r1=1.4433756729740645, r2=1.4433756729740645, $fn=6);
    translate([0, 55.75, 0]) rotate([0, 90, 0])
        cylinder(h=18.556624327025936, r1=1.4433756729740645, r2=1.4433756729740645, $fn=6);
}
