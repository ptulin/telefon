# Gerber Output Placeholder

This directory is reserved for generated Gerber and drill outputs from KiCad.

For a real fabrication release:

1. Open the KiCad project in `hardware/kicad/`
2. Resolve ERC and DRC warnings
3. Plot Gerbers for all copper, mask, silk, paste, and edge cuts
4. Generate Excellon drill files
5. Verify stackup and dimensions against enclosure model

The included fabrication CSVs are starter artifacts, not final factory outputs.
