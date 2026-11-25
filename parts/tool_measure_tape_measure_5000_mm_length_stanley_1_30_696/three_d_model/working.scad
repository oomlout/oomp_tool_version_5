// Stanley 1-30-696 tape measure, 5 m
// Retracted Stanley Tylon 1-30-696, modelled with a 69 × 72 × 40 mm case from a distributor listing. The outline and coloured face follow the manufacturer photograph. The lock, hook and belt clip are simplified or omitted; dimensions and physical fit require confirmation on the actual tool.
// Units: mm
$fn = 64;
union() {
    // Yellow case
    color([0.9765, 0.749, 0.0471])
    translate([0, 0, 0]) rotate([0, 0, 0])
        linear_extrude(height=39.4) polygon(points=[[-22.5, 0], [22.5, 0], [34.5, 12], [34.5, 60], [22.5, 72], [-22.5, 72], [-34.5, 60], [-34.5, 12]]);
    // Dark front panel
    color([0.1843, 0.1804, 0.1961])
    translate([0, 0, 39.4]) rotate([0, 0, 0])
        linear_extrude(height=0.6) polygon(points=[[-25.5, 10], [25.5, 10], [29.5, 17], [29.5, 56], [19.5, 65], [-19.5, 65], [-29.5, 56], [-29.5, 17]]);
}
