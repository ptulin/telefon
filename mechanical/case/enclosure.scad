device_length = 140;
device_width = 70;
device_thickness = 7.5;
wall = 1.2;
corner_r = 8;
display_window = [58, 44];
speaker_slot = [14, 2.2];
usb_cutout = [10, 4];

module rounded_box(size=[10,10,10], r=2) {
  hull() {
    for (x = [r, size[0]-r])
      for (y = [r, size[1]-r])
        for (z = [r, size[2]-r])
          translate([x,y,z]) sphere(r=r, $fn=24);
  }
}

module shell_outer() {
  rounded_box([device_length, device_width, device_thickness], corner_r);
}

module shell_inner() {
  translate([wall, wall, wall])
    rounded_box(
      [device_length - 2*wall, device_width - 2*wall, device_thickness - wall],
      max(corner_r - wall, 2)
    );
}

module front_features() {
  translate([41, 13, device_thickness - wall - 0.2])
    cube([display_window[0], display_window[1], wall + 1]);
  translate([device_length/2 - speaker_slot[0]/2, 8, device_thickness - wall - 0.2])
    cube([speaker_slot[0], speaker_slot[1], wall + 1]);
}

module bottom_features() {
  translate([device_length/2 - usb_cutout[0]/2, device_width - wall - 0.2, 1.8])
    rotate([90,0,0]) cube([usb_cutout[0], usb_cutout[1], wall + 1]);
}

difference() {
  shell_outer();
  shell_inner();
  front_features();
  bottom_features();
}
