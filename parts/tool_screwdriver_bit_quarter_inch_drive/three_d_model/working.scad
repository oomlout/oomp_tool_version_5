// Quarter-inch drive bit
// Representative Wera 851/4 Z PH2 bit, 89 mm long with a quarter-inch drive. The tapered tip is simplified and its length and end diameter are estimated.
// Units: mm
$fn = 64;
union() {
    // Hexagonal shank
    color([0.7176, 0.7216, 0.7059])
    translate([0, 0, 0]) rotate([-90, 0, 0])
        cylinder(h=81, r1=3.6661742093541236, r2=3.6661742093541236, $fn=6);
    // Phillips tip
    color([0.5882, 0.5922, 0.5765])
    translate([0, 81, 0]) rotate([-90, 0, 0])
        cylinder(h=8, r1=3.6661742093541236, r2=1.6, $fn=6);
}
