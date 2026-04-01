# Manufacturing Notes

## Prototype Strategy

Use a two-stage prototype path:

1. EVT-A
   - CM4 carrier
   - EC25 LTE modem
   - 3.2" SPI OLED
   - 3D printed enclosure
2. EVT-B
   - Thin custom PCB spin
   - improved antenna placement
   - optional RM520N-GL 5G variant
   - gasketed enclosure and flex cabling cleanup

## JLCPCB / PCBWay Outputs

The repository includes:

- `hardware/fabrication/jlcpcb_bom.csv`
- `hardware/fabrication/jlcpcb_cpl.csv`
- `hardware/fabrication/gerbers/README.md`
- `hardware/fabrication/exports_manifest.md`

These are intended as the fabrication package skeleton for export from KiCad after final ERC/DRC closure.

## Key DFM Rules

- 4-layer stackup minimum for RF and power integrity
- Controlled keep-outs under antennas and modem RF feed lines
- Avoid battery under high-temperature modem zones
- Maintain service access to SIM/eSIM debug points, USB-C, and SWD/UART
- Use board stiffeners or internal ribbing to meet thinness target

## Carrier Certification Risks

- Voice call support depends on modem SKU, carrier profile, and firmware
- eSIM support varies by region and requires carrier provisioning workflow
- 5G module thermals may exceed thin enclosure budget without aggressive burst management
