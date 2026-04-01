# Assembly Instructions

## Tools

- Fine-tip soldering station
- Hot air rework tool
- Stereo microscope
- Torque screwdriver set
- Kapton tape
- Thermal pads, 0.5 mm and 1.0 mm
- ESD-safe spudger and tweezers

## Board Assembly Order

1. Reflow PMIC, power path, passive rails, and fuel gauge
2. Reflow CM4 connectors and high-density board-to-board headers
3. Reflow audio codec, MEMS mic, touch controller, and sensors
4. Hand-place shield cans if used
5. Attach modem module and antennas
6. Wire speaker, display flex, battery, and solar input tail
7. Perform bring-up with bench supply before battery connection

## Bring-Up Checklist

- Verify no shorts on 5V, 3V3, and VBAT
- Boot Raspberry Pi OS from known-good image
- Confirm modem enumerates on USB
- Confirm microphone input and speaker output
- Confirm touch panel interrupt and I2C address
- Run battery gauge and charger telemetry checks
- Test outbound and inbound phone calls with headset and speaker path

## Enclosure Assembly

1. Bond display into front shell
2. Route FPC through strain-relief channel
3. Seat PCB and modem into midframe bosses
4. Apply thermal interface pads to shield cans and back shell
5. Seat battery with adhesive pull tabs
6. Close shell and torque screws in cross pattern
