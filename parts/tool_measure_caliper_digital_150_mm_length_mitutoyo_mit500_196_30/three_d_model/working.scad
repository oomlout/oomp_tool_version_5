// Mitutoyo 500-196-30 digital caliper, 150 mm
// Closed caliper. Overall length, beam width and outside jaw length follow the Mitutoyo dimensional drawing. Slider, jaws and display are simplified for identification.
// Units: mm
$fn = 64;
union() {
    translate([0, 0, 0]) rotate([0, 0, 0])
        linear_extrude(height=3) polygon(points=[[-8.0, 0], [8.0, 0], [8.0, 233], [-8.0, 233]]);
    translate([0, 0, 0]) rotate([0, 0, 0])
        linear_extrude(height=3) polygon(points=[[-48.0, 0], [8.0, 0], [24.5, 13], [8.0, 8], [-8.0, 8], [-48.0, 3]]);
    translate([0, 0, 0]) rotate([0, 0, 0])
        linear_extrude(height=3) polygon(points=[[-48.0, 3], [-8.0, 6], [8.0, 6], [24.5, 13], [8.0, 16], [-8.0, 16], [-42.0, 8]]);
    translate([0, 0, 0]) rotate([0, 0, 0])
        linear_extrude(height=13) polygon(points=[[-16, 12], [16, 12], [16, 65], [-16, 65]]);
    translate([0, 0, 13]) rotate([0, 0, 0])
        linear_extrude(height=1) polygon(points=[[-10, 19], [10, 19], [10, 53], [-10, 53]]);
}
