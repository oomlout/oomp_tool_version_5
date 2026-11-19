// Picquic Teeny Turner precision multi-driver
// Four coaxial sections follow the archived OOMP drawing, read at its document scale. The handle and exposed bit use simplified round sections.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=17, r1=2.7, r2=2.7, $fn=64);
    translate([0, 17, 0]) rotate([-90, 0, 0])
        cylinder(h=4, r1=3.75, r2=3.75, $fn=64);
    translate([0, 21, 0]) rotate([-90, 0, 0])
        cylinder(h=7, r1=4.5, r2=4.5, $fn=64);
    translate([0, 28, 0]) rotate([-90, 0, 0])
        cylinder(h=41.5, r1=14.0, r2=14.0, $fn=64);
}
