// M7 spanner
// Generic 7 mm open-end spanner using the FACOM 34.7 as a dimensional reference. Length, maximum head width and thickness follow the catalogue. The square-on jaws and shank are simplified, and the workshop specimen has not been measured.
// Units: mm
$fn = 64;
union() {
    // Open spanner
    color([0.7176, 0.7216, 0.7059])
    translate([0, 0, -1.35]) rotate([0, 0, 0])
        linear_extrude(height=2.7) polygon(points=[[-7.5, 0], [-3.5, 0], [-3.5, 7.5], [3.5, 7.5], [3.5, 0], [7.5, 0], [7.5, 8.25], [3.0, 18.75], [3.0, 61.25], [7.5, 71.75], [7.5, 80], [3.5, 80], [3.5, 72.5], [-3.5, 72.5], [-3.5, 80], [-7.5, 80], [-7.5, 71.75], [-3.0, 61.25], [-3.0, 18.75], [-7.5, 8.25]]);
}
