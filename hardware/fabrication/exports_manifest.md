# Export Manifest

Expected generated files after KiCad finalization:

- `gerbers/edge-node-F_Cu.gbr`
- `gerbers/edge-node-B_Cu.gbr`
- `gerbers/edge-node-F_SilkS.gbr`
- `gerbers/edge-node-B_SilkS.gbr`
- `gerbers/edge-node-F_Mask.gbr`
- `gerbers/edge-node-B_Mask.gbr`
- `gerbers/edge-node-Edge_Cuts.gbr`
- `gerbers/edge-node.drl`
- `edge-node-pos-top.csv`
- `edge-node-ibom.html`

Run `scripts/export_kicad.sh` after schematic/PCB completion.
