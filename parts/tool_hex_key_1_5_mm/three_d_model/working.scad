// 1.5 mm metric hex key
// The holder specifies the hex size. Arm lengths follow the Wiha 350 short series as a representative example. The holder source leaves the key manufacturer unspecified. The elbow is simplified.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=45.25, r1=0.8660254037844387, r2=0.8660254037844387, $fn=6);
    translate([0, 45.25, 0]) rotate([0, 90, 0])
        cylinder(h=14.13397459621556, r1=0.8660254037844387, r2=0.8660254037844387, $fn=6);
}
