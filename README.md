# vec-footpedal-hid-linux

A lightweight Python implementation to map a **VEC foot pedal** to mouse or keyboard actions under Linux. Adapted from https://github.com/DeflateAwning/vec-footpedal-hid-linux using ChatGPT

## Features

- Maps foot pedal buttons to any mouse or keyboard events.
- Automatically finds the foot pedal and reconnects if unplugged.
- Supports **Wayland** and **X11**.
- Full **hardware-level drag-and-drop** support via `uinput`.
- No need for sudo if udev rules and permissions are correctly configured.

## Setup & Usage

### 1. Set permissions (no sudo needed after this)

Create a udev rule to allow access to `/dev/uinput`:

```bash
sudo nano /etc/udev/rules.d/99-uinput.rules
```

Paste in:

```bash
KERNEL=="uinput", MODE="0660", GROUP="input"
```

Save and exit, then reload udev rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Add your user to the `input` group:

```bash
sudo usermod -aG input $USER
```

⚡ **Log out and log back in** to apply group changes.

---

### 2. Install Python dependencies

```bash
python3 -m pip install -r requirements.txt
```

The `requirements.txt` should contain:

```
evdev
python-uinput
```

---

### 3. Load the uinput kernel module

Manually:

```bash
sudo modprobe uinput
```

Optional: to auto-load at boot:

```bash
echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf
```

---

### 4. Run the script

```bash
python3 vec.py
```

Or enable debug mode to see pedal events:

```bash
python3 vec.py --debug
```

---

### 5. (Optional) Autostart at login using systemd

Create a user service:

```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/footpedal.service
```

Paste:

```ini
[Unit]
Description=Foot Pedal Mapper
After=graphical-session.target

[Service]
ExecStart=/usr/bin/python3 /full/path/to/vec.py
Restart=always
Environment=DISPLAY=:0
Environment=XDG_RUNTIME_DIR=/run/user/$(id -u)

[Install]
WantedBy=default.target
```

Enable and start the service:

```bash
systemctl --user daemon-reload
systemctl --user enable footpedal.service
systemctl --user start footpedal.service
```

---

## Design Approach

1. Use `evtest` to identify button codes:
    - `256` = left pedal
    - `257` = middle pedal
    - `258` = right pedal
2. Listen for key press/release events.
3. Map each event to mouseDown/mouseUp via virtual device.
4. Send real hardware-level events to the system for maximum compatibility.

---

## Other Resources and Motivation
this script started as a fork of https://github.com/DeflateAwning/vec-footpedal-hid-linux but no longer refers to it much as far as the code goes.  Like the parent repo, I did this with ChatGPT pyton AI. I think the model improved.  

The following resources didn't fully solve this use case, so this project was created:

- https://saulalbert.net/blog/transcription-with-a-foot-pedal-under-linux/
- https://github.com/kostmo/footpedal
- https://github.com/peternewman/VECFootpedal
- https://catswhisker.xyz/log/2018/8/27/use_vecinfinity_usb_foot_pedal_as_a_keyboard_under_linux/

---

## 🛠️ Troubleshooting

### The foot pedal doesn't work after reboot

- Make sure the `uinput` module is loaded:
  ```bash
  lsmod | grep uinput
  ```
  If it's not listed, load it manually:
  ```bash
  sudo modprobe uinput
  ```

- To auto-load `uinput` on every boot, create:
  ```bash
  echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf
  ```

---

### Permission denied accessing `/dev/uinput`

- Ensure you have created the udev rule:
  ```bash
  sudo nano /etc/udev/rules.d/99-uinput.rules
  ```
  With contents:
  ```bash
  KERNEL=="uinput", MODE="0660", GROUP="input"
  ```
  Then reload rules:
  ```bash
  sudo udevadm control --reload-rules
  sudo udevadm trigger
  ```

- Verify your user is in the `input` group:
  ```bash
  groups
  ```
  If not, add yourself:
  ```bash
  sudo usermod -aG input $USER
  ```
  Then **log out and log back in**.

---

### Drag and drop still not working in Nemo or File Manager

- Confirm that the script is using **uinput** and not fallback methods like `pyautogui` or `xdotool`.
- Ensure your systemd service (if used) has access to the user session's input environment.
- If problems persist, try running the script manually with `sudo` as a test to isolate permission issues.

---

### Debugging mode

Run the script with `--debug` enabled to see detailed event logs:

```bash
python3 vec.py --debug
```

This will print pedal press and release events for troubleshooting.
