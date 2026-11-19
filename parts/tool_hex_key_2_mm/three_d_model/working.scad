// 2 mm metric hex key
// The holder specifies the hex size. Arm lengths follow the Wiha 350 short series as a representative example. The holder source leaves the key manufacturer unspecified. The elbow is simplified.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=50.0, r1=1.1547005383792517, r2=1.1547005383792517, $fn=6);
    translate([0, 50.0, 0]) rotate([0, 90, 0])
        cylinder(h=16.845299461620748, r1=1.1547005383792517, r2=1.1547005383792517, $fn=6);
}
