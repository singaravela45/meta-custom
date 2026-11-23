# meta-custom (`wrynose` branch)

A custom [Yocto Project](https://www.yoctoproject.org/) layer for the **Raspberry Pi 4 (64-bit)** that builds a ready-to-flash image running a **face-recognition attendance system**.

> [!NOTE]
> This README is for the **`wrynose`** branch (Yocto Project 6.0). Use the matching `wrynose` branch of every layer listed below.

---

## What this layer is for

`meta-custom` turns a Raspberry Pi 4 and a USB webcam into a stand-alone attendance and security device:

- **Recognises known people** with OpenCV (Haar Cascade face detection + LBPH face recognition) using the photos you place in the layer.
- **Records attendance** in a CSV file, once per person per day.
- **Sends an email alert with a photo** (through Gmail SMTP) when an unknown face is seen.
- **Starts automatically on boot** through a systemd service, with no manual steps after the image is flashed.

### What the layer contains

| Component | Description |
|---|---|
| `main.py` | The face-recognition and attendance application |
| `face-attendance.service` | systemd unit that starts the application at boot and restarts it on failure |
| `known_faces/` | Photos of authorised people |
| `models/` | Haar Cascade face-detection model |
| `.env` | Email and tuning settings (you create this, see step 4) |
| `packagegroup-custom` | Python, OpenCV, USB webcam (UVC) and system runtime dependencies |
| `custom-image` | The Yocto image that ties everything together |

> [!IMPORTANT]
> **Before you start:** a systemd service named `face-attendance` is already set up by this layer and is enabled in the image. Once the image is flashed, the application **starts automatically every time the Raspberry Pi boots**. You do not need to run `main.py` by hand.

---

## Requirements

**Hardware**
- Raspberry Pi 4 (64-bit)
- USB webcam (UVC compatible)
- SD card
- Internet connection on the Pi (for email alerts)

**Host machine**
- A Linux machine that can build Yocto Project 6.0 (wrynose); see the [Yocto system requirements](https://docs.yoctoproject.org/)

**Layers** (all on their `wrynose` branch)

| Layer | Repository |
|---|---|
| openembedded-core | https://git.openembedded.org/openembedded-core |
| meta-yocto (`meta-poky`, `meta-yocto-bsp`) | https://git.yoctoproject.org/meta-yocto |
| meta-openembedded (`meta-oe`, `meta-python`) | https://git.openembedded.org/meta-openembedded |
| meta-raspberrypi | https://git.yoctoproject.org/meta-raspberrypi |
| **meta-custom** (this layer) | https://github.com/singaravela45/meta-custom |

---

## Installation Guide

### 1. Clone this layer

Clone the `wrynose` branch into your Yocto workspace, next to the other layers:

```bash
cd ~/projects/yocto-wrynose
git clone -b wrynose https://github.com/singaravela45/meta-custom.git
```

### 2. Configure `bblayers.conf`

Edit `build-rpi/conf/bblayers.conf` so the layers are listed like this (replace `/home/singara/projects/yocto-wrynose` with the path to your own workspace):

```bitbake
BBLAYERS ?= " \
  /home/singara/projects/yocto-wrynose/openembedded-core/meta \
  /home/singara/projects/yocto-wrynose/meta-yocto/meta-poky \
  /home/singara/projects/yocto-wrynose/meta-yocto/meta-yocto-bsp \
  /home/singara/projects/yocto-wrynose/meta-openembedded/meta-oe \
  /home/singara/projects/yocto-wrynose/meta-openembedded/meta-python \
  /home/singara/projects/yocto-wrynose/meta-raspberrypi \
  /home/singara/projects/yocto-wrynose/meta-custom \
  "
```

### 3. Configure `local.conf`

Add the following to `build-rpi/conf/local.conf`:

```bitbake
DISTRO = "poky"
MACHINE = "raspberrypi4-64"
INIT_MANAGER = "systemd"
```

`INIT_MANAGER = "systemd"` is required: the application is started by a systemd service.

### 4. Configure the application settings

After configuring the two files above, go to the application's files directory:

```bash
cd meta-custom/recipes-core/smart-attendance/files/
```
Modify the .env.example file with the appropriate values and rename it to .env

| Variable | Required | Description |
|---|---|---|
| `GMAIL_APP_PASSWORD` | Yes | A Gmail **app password** (not your normal password). Requires 2-Step Verification on the Google account. |
| `SENDER_EMAIL` | Yes | The Gmail address that sends the alert emails |
| `RECEIVER_EMAIL` | Yes | The address that receives the alerts |
| `CAMERA_INDEX` | No (default `1`) | Index of the USB webcam. Try `0` if the camera cannot be opened. |
| `FACE_CONFIDENCE_THRESHOLD` | No (default `70`) | Recognition threshold. **Lower is stricter.** Calibrate it with your own photos. |
| `UNKNOWN_FRAMES_REQUIRED` | No (default `5`) | Number of consecutive frames an unknown face must appear in before an alert is sent |
| `COOLDOWN_SECONDS` | No (default `30`) | Minimum number of seconds between two alert emails |

> [!WARNING]
> - The `.env` file is built **into the image**, so protect the image and the SD card.
> - Never commit `.env` to Git. It is listed in `.gitignore`.

#### Add the authorised faces

Put photos of the people who should be recognised in `meta-custom/recipes-core/smart-attendance/files/known_faces/`:

- Name each file `firstname_1.jpg`, `firstname_2.jpg`, and so on. `john_1.jpg` and `john_2.jpg` are both recognised as **John**.
- Use 5 to 10 clear, front-facing photos per person, with varied lighting, for better accuracy.
- Only use photos of people who have agreed to be included.

### 5. Build the image

From your Yocto workspace, initialise the build environment and build:

```bash
cd ~/projects/yocto-wrynose
source openembedded-core/oe-init-build-env build-rpi
bitbake custom-image
```

The generated image is placed in:

```
build-rpi/tmp/deploy/images/raspberrypi4-64/
```

### 6. Flash the image

Write the image file (ending in `.wic.bz2` or `.rpi-sdimg`) to the SD card with [Raspberry Pi Imager](https://www.raspberrypi.com/software/), [balenaEtcher](https://etcher.balena.io/), or the command line:

```bash
bzip2 -dc <image-file>.wic.bz2 | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync
```

> [!CAUTION]
> Replace `/dev/sdX` with your SD card device. Writing to the wrong device will erase its data.

### 7. Boot and use

1. Insert the SD card, connect the USB webcam and network, and power on the Raspberry Pi 4.
2. The `face-attendance` service starts automatically.
3. Attendance is written to `/home/root/files/attendance.csv`.

---

## Managing the service

The application runs as the `face-attendance` systemd service:

```bash
systemctl status face-attendance        # running or failed
journalctl -u face-attendance -f        # live logs
systemctl restart face-attendance       # after editing .env
systemctl stop face-attendance          # stop it
systemctl disable face-attendance       # no autostart
```

To change settings on the board, edit `/home/root/files/.env` and run `systemctl restart face-attendance`. To make a change permanent, update `.env` in this layer and rebuild the image.

---

## Troubleshooting

| Problem | What to check |
|---|---|
| Camera cannot be opened | Run `v4l2-ctl --list-devices` and set `CAMERA_INDEX` in `.env` to the correct number (try `0` or `1`) |
| No alert emails | Check `journalctl -u face-attendance -f`. Make sure all three email values are set, the Pi is online, and you are using a Gmail **app password**. |
| Wrong times in attendance | The Raspberry Pi 4 has no battery-backed clock. Check the time with `date` and make sure the Pi can reach a time server. |
| Known people not recognised | Add more varied photos per person, or adjust `FACE_CONFIDENCE_THRESHOLD`. |
| Strangers recognised as known people | Lower `FACE_CONFIDENCE_THRESHOLD` to make matching stricter. |

---

## Limitations

- Recognition uses classic OpenCV methods (Haar Cascade + LBPH). It does **not** detect spoofing, so a photo held up to the camera may be accepted as a real person. It is suitable for a demo or low-risk attendance use, not for access control.
- The device stores face photos and sends photos of unknown people by email. Make sure you have the consent your local data-protection rules require.