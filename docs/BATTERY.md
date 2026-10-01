# Battery, switch, and charging

The developer's battery label is **JH 702030, 3.7 V, 300 mAh, 1.11 Wh, 25C**. This is consistent with a single-cell lithium pack; confirm it is rechargeable, its protection circuit, connector polarity, and permitted charge current from its supplier. The 25C marking describes discharge capability; it is not permission to charge at 25C.

For a genuine nice!nano, the manufacturer specifies a 3.7 V rechargeable lithium battery connected at B+ and B−. [Manufacturer battery instructions](https://nicekeyboards.com/docs/nice-nano/getting-started/). The prototype is a compatible-looking board; confirm its terminal labels and charger specification before applying these instructions. Do not infer charger limits from its USB name.

## Connection, after terminal confirmation

Disconnect USB and the battery before assembling a connector/switch harness. Use an insulated, polarity-checked connector rather than repeatedly handling loose live wires.

```text
Battery positive (+) ── on/off switch ── board B+ / BAT+
Battery negative (−) ────────────────── board B− / BAT−
LED cathodes ────────────────────────── board GND
```

A simple SPST switch goes in the positive lead. On a three-terminal SPDT slide switch, use common plus one outer contact; identify common with a continuity meter, do not assume pin orientation. Insulate the unused contact. Keep the board-specific battery negative terminal distinct until the supplier confirms it is common with GND.

Check connector polarity using a meter: red/black wire color and JST shape alone are not enough. Never connect this battery to a GPIO, VCC/3V3, or a pin assumed to be a battery input. Do not solder directly to a cell's foil tabs/body. Use its existing leads or a suitable connector, with the battery disconnected from the harness while soldering.

## Off and on

With **USB unplugged**, switch off disconnects the battery supply and all LEDs should go dark; switch on boots the saved firmware and begins BLE advertising. The Mac's saved configuration reconnects automatically while its helper is running and Bluetooth access remains allowed. No reflash or reapproval should be needed for ordinary battery switching.

USB can still power the board when the battery switch is off. For a true power-off, remove USB as well. A switch placed between battery and B+ also disconnects the battery from the board's charger, so charging normally requires the switch to be on. Verify the actual board's power path.

## Charging

Before charging through USB, verify the clone's charger current, lithium charging voltage, battery minimum charge rating, and protection arrangement. The 300 mAh capacity alone is insufficient to approve the charger's current. If those details are unknown, use an appropriate external charger for this exact battery; do not assume the board is a safe charger.

Do not attach AA/AAA alkaline cells, non-rechargeable cells, multiple cells in series, or a 7.4 V pack to a lithium charging input. Avoid damaged/swollen packs and exposed conductors that can short. Secure the battery without crushing/puncturing it or pressing it against sharp pins.

Battery duration and repeated battery-switch cycles have not been measured on this build. Use docs/TESTING.md to record them; do not infer endurance from keyboard firmware benchmarks.
