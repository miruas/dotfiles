# Optional Profile Manager

This section adapts the supplied rice guide into an English, hardware-independent setup reference. The bridge is deliberately excluded from the default installation. It runs as root because CPU limits, LACT and CoolerControl require privileged access. The UI talks to a local Unix socket; it does not receive the CoolerControl token.

## UI

Stage the desktop with `--profile-ui` to include the native card below the connectivity/audio controls in **Super + B**. Cooling offers **Silent**, **Turbo** and **BIOS Controlled**. Performance offers **Low Performance** and **Max Performance**. These are independent selections. CPU/GPU temperatures and fan speed appear on the card. Status polling runs every 2.5 seconds only while the menu is open. Pending selections survive a status request. Selection, hover and press animations use 260, 160 and 120 ms timings.

## Hardware reference

The original setup used an AMD Ryzen 7 9800X3D, NVIDIA RTX 4060, Gigabyte B850M FORCE WIFI6E and ITE IT8696E with `it87-dkms-git`, CoolerControl 5.0.1, LACT 0.10.1, amd-pstate-epp and power-profiles-daemon.

On that board, **CPU_FAN was the AIO pump**, while **CPU_OPT was the radiator fan**. The exported example uses `fan5` for the radiator and `fan1` for pump telemetry. These labels are examples, not a discovery mechanism. Verify your own physical connectors, sensor names and channels. The bridge rejects cooling modes containing devices or channels beyond the configured radiator channel. It never applies a pump curve.

## Configure manually

1. Configure LACT and CoolerControl locally. Keep CoolerControl bound to loopback and its password enabled. Confirm normal hardware control before adding the bridge.
2. Create CoolerControl modes named **Silent**, **Turbo**, and **BIOS Controlled**, each containing only the radiator channel. Mode names are configurable in `hardware.json`.
3. Copy `hardware.example.json` to `/etc/dank-profile-manager/hardware.json` in a root-owned directory with mode 700. Set your actual user UID/GID, CoolerControl device UID, hwmon names, radiator and pump channels. Review CPU and GPU low limits. The placeholder device UID prevents startup until configured.
4. Install `manager.py` to `/usr/local/lib/dank-profile-manager/manager.py`, `dank-profilectl` to `/usr/local/bin/dank-profilectl`, and the service file to `/etc/systemd/system/`. Install Python PyYAML. Preserve executable permissions on the CLI.
5. With an existing active LACT profile selected, run `sudo python -I /usr/local/lib/dank-profile-manager/manager.py --initialize`. This is an explicit privileged setup step: it backs up local LACT/CoolerControl files, adds the low GPU profile, creates a local CoolerControl token and records the CPU/GPU baseline. Do not rerun it to change hardware; inspect and migrate the baseline deliberately.
6. Run `sudo systemctl daemon-reload` and `sudo systemctl enable --now dank-profile-manager.service`. Use `dank-profilectl status` to verify mapping and telemetry before selecting modes.

The daemon uses fixed status/fan/performance operations, peer UID checks and a group-restricted socket under `/run/dank-profile-manager/`. Only root and the configured UID are accepted. Socket ownership uses the configured GID. It restores the chosen performance mode at boot; CoolerControl maintains fan state separately.

## Reference fan curve

Configure the curve in CoolerControl; the bridge selects existing modes and does not construct them.

| CPU temperature | Radiator speed |
| --- | --- |
| 20–60 °C | 10% |
| 65 °C | 20% |
| 70 °C | 35% |
| 75 °C | 55% |
| 80 °C | 80% |
| 85 °C | 100% |

The reference silent profile used 3 °C hysteresis, a 10-second/5-percentage-point downward smoothing policy and no upward delay. Verify that the fans reliably start at the minimum duty. Turbo and BIOS modes must also target only the radiator. No universal pump or motherboard configuration is shipped.

## Performance behavior

The example low profile caps CPU frequency at 3 GHz, disables boost, selects powersave/EPP power and the power-saver power profile. GPU settings are Adaptive, 210–1500 MHz and 90 W with zero memory clock offset. These values are configurable examples, not safe limits for every GPU.

Max restores the captured CPU baseline, enables the baseline boost state and selects the existing LACT profile with the performance power profile. It does not invent or distribute an overclock curve. The original active GPU tuning remains local. Failed performance changes attempt to restore the preceding mode.

Private files include `/etc/dank-profile-manager/{hardware.json,baseline.json,coolercontrol.token}`, `/etc/coolercontrol/.tokens`, LACT/CoolerControl configurations and `/var/lib/dank-profile-manager/`. Never publish them. Disable the service before reverting hardware control and restore its root-owned local backups deliberately. Revoke the bridge's CoolerControl token when removing it.
