// OLFA DC-3 blade disposal can
// Round yellow body and red face approximation using OLFA's overall length and thickness and product photograph. The sliding door, lettering and rim details are omitted.
// Units: mm
$fn = 64;
union() {
    // Body
    color([0.9765, 0.749, 0.0471])
    translate([0, 0, 0]) rotate([0, 0, 0])
        cylinder(h=23.6, r1=33.5, r2=33.5, $fn=64);
    // Red face
    color([0.6863, 0.1059, 0.1569])
    translate([0, 0, 23.6]) rotate([0, 0, 0])
        cylinder(h=0.4, r1=32.0, r2=32.0, $fn=64);
}
