# Kalico Line Purge

Adaptive purge module for Kalico with placement control, extrusion ramp testing, and purge behavior logging.

## Overview

The `kalico_purge` module is a flexible, extensible purge system for the Kalico firmware ecosystem. It allows users to dynamically place purge lines based on mesh bounds, execute spiral or "blob" purges, and run calibration tests for extrusion limits and heater response.

This addon logs every purge event and optionally performs diagnostics to optimize print start quality across filaments. It also supports saving new default purge values to the printer configuration via `SET_PURGE_DEFAULTS`.

---

## Features

* ✅ Line purging with flexible placement (front, side, mesh bounds, or absolute)
* 🔁 Optional blob-style purge mode (`BLOB=1`)
* 🧪 Extrusion ramp test to evaluate thermal response and feed rate limits
* 📋 Automatic logging of purge parameters and context to per-instance config folder
* 💾 Update default purge settings with `SET_PURGE_DEFAULTS`
* 🔒 Compatible with multi-instance KIAUH setups (resolves config paths dynamically)

---

## Example Command

```gcode
PURGE LENGTH=35 SPEED=900 Z_HOP=0.4 PLACEMENT=front EXT_TEST=1 BLOB=1
```

## Save New Defaults

To update the default purge parameters:

```gcode
SET_PURGE_DEFAULTS LENGTH=35 SPEED=900 Z_HOP=0.4 BLOB=1
SAVE_CONFIG
```

This updates the `[kalico_purge]` config section with the new values.

---

## Supported Parameters

| Parameter   | Type  | Default    | Description                                                                    |
| ----------- | ----- | ---------- | ------------------------------------------------------------------------------ |
| `LENGTH`    | float | 30.0       | Purge line length in mm                                                        |
| `SPEED`     | float | 1000.0     | Movement speed in mm/min                                                       |
| `Z_HOP`     | float | 0.3        | Height to lift before and after purge                                          |
| `PLACEMENT` | str   | `mesh_min` | Placement type: `mesh_min`, `mesh_max`, `front`, `center_side`, or use `X`/`Y` |
| `X` / `Y`   | float | —          | Explicit coordinates (overrides PLACEMENT)                                     |
| `EXT_TEST`  | int   | 0          | Run extrusion ramp test if set to 1                                            |
| `BLOB`      | int   | 0          | Run blob-style purge if set to 1                                               |

---

## Configuration Template

Place in `printer_data/config/kalico_purge.cfg`:

```ini
[kalico_purge]

# Default purge line length (mm)
default_length: 30.0

# Default purge move speed (mm/min)
default_speed: 1000.0

# Default Z-hop height (mm)
default_z_hop: 0.3

# Enable blob-style purge mode when BLOB=1
enable_blob_mode: False

# Enable extrusion ramp test when EXT_TEST=1
enable_ext_test: True
```

---

## Log Output

Each run logs the following:

* Timestamp
* X/Y coordinates
* Purge length, speed, z-hop
* `blob` and `ext_test` flags

Location (auto-detected):

```
<printer_instance>/config/kalico_purge/purge_log.csv
```

---

## Roadmap

* [ ] Auto-detect mesh bounds from `bed_mesh`
* [ ] Heater telemetry logging in `EXT_TEST`
* [ ] Visualization tools (plot flow vs temp)
* [ ] Spiral purge G-code pattern for blob mode

---

## License

This module is released under the **[Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/)**.

© 2025 [Arcturis144](https://github.com/Arcturis144)

You are free to:

* Share — copy and redistribute the material in any medium or format
* Adapt — remix, transform, and build upon the material

Under the following terms:

* **Attribution** — You must give appropriate credit and link to the license.
* **NonCommercial** — You may not use the material for commercial purposes.
