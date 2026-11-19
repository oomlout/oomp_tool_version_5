// 4 mm metric hex key
// The holder specifies the hex size. Arm lengths follow the Wiha 350 short series as a representative example. The holder source leaves the key manufacturer unspecified. The elbow is simplified.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=70.0, r1=2.3094010767585034, r2=2.3094010767585034, $fn=6);
    translate([0, 70.0, 0]) rotate([0, 90, 0])
        cylinder(h=26.690598923241495, r1=2.3094010767585034, r2=2.3094010767585034, $fn=6);
}
