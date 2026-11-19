// Sharpie-style felt-tip pen, 13 × 137 mm
// Nominal capped body from the vertical holder's tool identity. The 14 mm pocket includes clearance. Cap and barrel split are illustrative.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=5.48, r1=5.07, r2=5.59, $fn=64);
    translate([0, 5.48, 0]) rotate([-90, 0, 0])
        cylinder(h=93.16000000000001, r1=5.59, r2=5.59, $fn=64);
    translate([0, 98.64000000000001, 0]) rotate([-90, 0, 0])
        cylinder(h=32.879999999999995, r1=6.5, r2=6.5, $fn=64);
    translate([0, 131.52, 0]) rotate([-90, 0, 0])
        cylinder(h=5.48, r1=6.5, r2=5.98, $fn=64);
}
