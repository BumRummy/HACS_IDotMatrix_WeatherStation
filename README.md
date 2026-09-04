# iDotMatrix Weather Matrix — beta

A Home Assistant custom integration for 32×32 and 64×64 iDotMatrix BLE displays.

## Included default pack

The integration ships with the animated **Giraffe Weather** 64×64 pack. If you leave the animation-pack setting at its default, no separate GIF files are required.

Included scenes include rain, sun, thunderstorm, snow, wind, clear night, fog, extreme heat, and freezing.

## What it does

- Uses a Home Assistant `weather.*` entity for weather condition and temperature.
- Uses Home Assistant local time for the clock.
- Selects the matching animated GIF.
- Paints the clock/temperature/condition rectangles with a solid background (black by default).
- Draws the live values with built-in pixel-matrix fonts.
- Uploads the resulting 64×64 GIF to the iDotMatrix over Bluetooth.

## Install with HACS

1. In HACS, open **Custom repositories**.
2. Add this repository as category **Integration**.
3. Install **iDotMatrix Weather Matrix**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and search for **iDotMatrix Weather Matrix**.
6. Choose your `weather.*` entity and your iDotMatrix Bluetooth address.

The integration defaults to the bundled giraffe animation pack.

## Custom animation packs

A custom pack can provide 64×64 GIFs such as `sunny.gif`, `rain.gif`, `thunderstorm.gif`, `snow.gif`, `windy.gif`, `fog.gif`, `clear_night.gif`, and `default.gif`, plus an optional `manifest.json` defining region coordinates and colors.

## Current beta limitation

The reverse-engineered protocol does not yet prove that arbitrary overlays can be modified while a native GIF continues playing. This beta therefore caches the source animation and re-encodes/re-uploads it when a displayed value changes. It does **not** regenerate the artwork.

Bluetooth behavior can vary by iDotMatrix firmware revision, so the 64×64 transport still needs testing on real hardware.
