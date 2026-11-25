// Driver bit, 60 mm profile
// Representative 60 mm quarter-inch double-ended PH2/PZ2 bit. Length and drive size follow the HiKOKI product. The tapered hexagonal tips are simplified and their length and end diameter are estimates.
// Units: mm
$fn = 64;
union() {
    // Lower tip
    color([0.5882, 0.5922, 0.5765])
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=8, r1=1.6, r2=3.6661742093541236, $fn=6);
    // Hexagonal shank
    color([0.7176, 0.7216, 0.7059])
    translate([0, 8, 0]) rotate([-90, 0, 0])
        cylinder(h=44, r1=3.6661742093541236, r2=3.6661742093541236, $fn=6);
    // Upper tip
    color([0.5882, 0.5922, 0.5765])
    translate([0, 52, 0]) rotate([-90, 0, 0])
        cylinder(h=8, r1=3.6661742093541236, r2=1.6, $fn=6);
}
