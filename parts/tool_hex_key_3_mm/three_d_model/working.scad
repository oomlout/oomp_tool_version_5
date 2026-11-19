// 3 mm metric hex key
// The holder specifies the hex size. Arm lengths follow the Wiha 350 short series as a representative example. The holder source leaves the key manufacturer unspecified. The elbow is simplified.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=62.5, r1=1.7320508075688774, r2=1.7320508075688774, $fn=6);
    translate([0, 62.5, 0]) rotate([0, 90, 0])
        cylinder(h=21.26794919243112, r1=1.7320508075688774, r2=1.7320508075688774, $fn=6);
}
