// 5 mm metric hex key
// The holder specifies the hex size. Arm lengths follow the Wiha 350 short series as a representative example. The holder source leaves the key manufacturer unspecified. The elbow is simplified.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=80.5, r1=2.886751345948129, r2=2.886751345948129, $fn=6);
    translate([0, 80.5, 0]) rotate([0, 90, 0])
        cylinder(h=30.113248654051873, r1=2.886751345948129, r2=2.886751345948129, $fn=6);
}
