// OLFA DC-3 blade disposal can
// Round body approximation using OLFA's overall length and thickness. The sliding door and rim details are omitted.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([0, 0, 0])
        cylinder(h=24, r1=33.5, r2=33.5, $fn=64);
}
