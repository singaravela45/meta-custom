# meta-custom (`scarthgap` branch)

A custom [Yocto Project](https://www.yoctoproject.org/) layer for the
**Raspberry Pi 4 (64-bit)** that builds a ready-to-flash image running a
**face-recognition attendance system**.

> \[!NOTE\] This README is for the **`scarthgap`** branch . Use the matching `scarthgap` branch of every layer listed below.

------------------------------------------------------------------------

## What this layer is for

`meta-custom` turns a Raspberry Pi 4 and a USB webcam into a stand-alone
attendance and security device:

-   **Recognises known people** with OpenCV (Haar Cascade face
    detection + LBPH face recognition) using the photos maintained in
    the separate application repository.
-   **Records attendance** in a CSV file, once per person per day.
-   **Sends an email alert with a photo** (through Gmail SMTP) when an
    unknown face is seen.
-   **Automatically detects the connected USB webcam**, so no manual
    camera index configuration is required.
-   **Starts automatically on boot** through a systemd service, with no
    manual steps after the image is flashed.

### What the layer contains

  -----------------------------------------------------------------------
  Component                           Description
  ----------------------------------- -----------------------------------
  `smart-attendance.bb`               Yocto recipe that fetches the
                                      application source code from the
                                      GitHub repository

  `.env`                              Email and tuning settings (you
                                      create this, see step 4)

  `packagegroup-custom`               Python, OpenCV, USB webcam (UVC)
                                      and system runtime dependencies
  -----------------------------------------------------------------------

> \[!IMPORTANT\] **Application source code is maintained separately.**
> The `main.py`, `known_faces/`,`face-attendance.service` and `models/` directories are fetched
> from the GitHub repository during the Yocto build. They are not
> maintained directly inside this layer.
>
> The application repository is:
> https://github.com/singaravela45/smart-attendance
>
> The `face-attendance` systemd service is already configured and
> enabled in the image. Once the image is flashed, the application
> starts automatically every time the Raspberry Pi boots. You do not
> need to run `main.py` by hand.

------------------------------------------------------------------------

## Requirements

**Hardware** - Raspberry Pi 4 (64-bit) - USB webcam (UVC compatible) -
SD card - Internet connection on the Pi (for email alerts)

**Host machine** - A Linux machine that can build Yocto Project 6.0
(scarthgap); see the [Yocto system
requirements](https://docs.yoctoproject.org/)

**Layers** (all on their `scarthgap` branch)

  ---------------------------------------------------------------------------------------
  Layer                               Repository
  ----------------------------------- ---------------------------------------------------
  openembedded-core                   https://git.openembedded.org/openembedded-core

  meta-yocto (`meta-poky`,            https://git.yoctoproject.org/meta-yocto
  `meta-yocto-bsp`)                   

  meta-openembedded (`meta-oe`,       https://git.openembedded.org/meta-openembedded
  `meta-python`)                      

  meta-raspberrypi                    https://git.yoctoproject.org/meta-raspberrypi

  **meta-custom** (this layer)        https://github.com/singaravela45/meta-custom

  **smart-attendance** (application   https://github.com/singaravela45/smart-attendance
  repository)                         
  ---------------------------------------------------------------------------------------

------------------------------------------------------------------------

## Installation Guide

### 1. Clone this layer

Clone the `scarthgap` branch into your Yocto workspace, next to the other
layers:

``` bash
cd ~/projects/yocto-scarthgap
git clone -b scarthgap https://github.com/singaravela45/meta-custom.git
```

### 2. Configure `bblayers.conf`

Edit `build-rpi/conf/bblayers.conf` so the layers are listed like this
(replace `/home/singara/projects/yocto-scarthgap` with the path to your
own workspace):

``` bitbake
BBLAYERS ?= " \
  /home/singara/projects/yocto-scarthgap/openembedded-core/meta \
  /home/singara/projects/yocto-scarthgap/meta-yocto/meta-poky \
  /home/singara/projects/yocto-scarthgap/meta-yocto/meta-yocto-bsp \
  /home/singara/projects/yocto-scarthgap/meta-openembedded/meta-oe \
  /home/singara/projects/yocto-scarthgap/meta-openembedded/meta-python \
  /home/singara/projects/yocto-scarthgap/meta-raspberrypi \
  /home/singara/projects/yocto-scarthgap/meta-custom \
  "
```

### 3. Configure `local.conf`

Add the following to `build-rpi/conf/local.conf`:

``` bitbake
DISTRO = "poky"
MACHINE = "raspberrypi4-64"
INIT_MANAGER = "systemd"
VIRTUAL-RUNTIME_init_manager = "systemd"
LICENSE_FLAGS_ACCEPTED:append = " synaptics-killswitch commercial"
DISTRO_FEATURES:append = " usrmerge"
```

`INIT_MANAGER = "systemd"` is required: the application is started by a
systemd service.

### 4. Configure the application settings

The application configuration file `.env` is maintained inside the
custom Yocto layer.

Go to the application's files directory:

``` bash
cd meta-custom/recipes-core/smart-attendance/files/
```

Modify the `.env.example` file with the appropriate values and rename it
to `.env`.

  -----------------------------------------------------------------------------
  Variable                      Required                Description
  ----------------------------- ----------------------- -----------------------
  `GMAIL_APP_PASSWORD`          Yes                     A Gmail **app
                                                        password** (not your
                                                        normal password).
                                                        Requires 2-Step
                                                        Verification on the
                                                        Google account.

  `SENDER_EMAIL`                Yes                     The Gmail address that
                                                        sends the alert emails

  `RECEIVER_EMAIL`              Yes                     The address that
                                                        receives the alerts

  `FACE_CONFIDENCE_THRESHOLD`   No (default `70`)       Recognition threshold.
                                                        **Lower is stricter.**
                                                        Calibrate it with your
                                                        own photos.

  `UNKNOWN_FRAMES_REQUIRED`     No (default `5`)        Number of consecutive
                                                        frames an unknown face
                                                        must appear in before
                                                        an alert is sent

  `COOLDOWN_SECONDS`            No (default `30`)       Minimum number of
                                                        seconds between two
                                                        alert emails
  -----------------------------------------------------------------------------

> \[!NOTE\] The application automatically detects the connected USB
> webcam. You do not need to configure or modify a camera index in
> `.env`.

> \[!WARNING\] - The `.env` file is built **into the image**, so protect
> the image and the SD card. - Never commit `.env` to Git. It is listed
> in `.gitignore`. - Use a Gmail app password instead of your regular
> Gmail account password.

------------------------------------------------------------------------

### 5. Application repository and development

The face-recognition attendance application is maintained in a separate
GitHub repository:

**Application repository:**

https://github.com/singaravela45/smart-attendance

The Yocto recipe fetches the application source code directly from this
repository during the build using the following `SRC_URI`:

``` bitbake
SRC_URI = "git://github.com/singaravela45/smart-attendance.git;protocol=https;branch=main;"
```

The application repository contains:

-   `main.py` -- Face-recognition and attendance application.
-   `known_faces/` -- Photos of authorised people.
-   `models/` -- Haar Cascade face-detection model.
-   Other application-related files and dependencies.

#### How to customize and develop the application

If you want to develop or customize this application for your own
requirements, follow these steps:

**Step 1: Fork the application repository**

Open the original repository:

https://github.com/singaravela45/smart-attendance

Click the **Fork** button on GitHub to create your own copy of the
repository.

**Step 2: Clone your fork**

Replace `YOUR_USERNAME` with your GitHub username:

``` bash
git clone https://github.com/YOUR_USERNAME/smart-attendance.git
cd smart-attendance
```

**Step 3: Add your own authorised faces**

Add photos of the people you want the system to recognise inside the
`known_faces/` directory.

-   Name each file `firstname_1.jpg`, `firstname_2.jpg`, and so on.
-   For example, `john_1.jpg` and `john_2.jpg` are both recognised as
    **John**.
-   Use 5 to 10 clear, front-facing photos per person, with varied
    lighting, for better accuracy.
-   Only use photos of people who have agreed to be included.

**Step 4: Modify the application**

You can now customize the application according to your requirements:

-   Modify `main.py` to change face-recognition or attendance
    functionality.
-   Add or remove authorised face images in `known_faces/`.
-   Update the models or other application files if required.
-   Implement additional features according to your project needs.

**Step 5: Push your changes to your fork**

Commit and push your modifications:

``` bash
git add .
git commit -m "Customize face attendance application"
git push origin main
```

**Step 6: Update the Yocto recipe**

After customizing the application, you must tell Yocto to fetch your
fork instead of the original repository.

Open the `smart-attendance.bb` recipe in your `meta-custom` layer:

``` text
meta-custom/
└── recipes-core/
    └── smart-attendance/
        └── smart-attendance.bb
```

Find the existing `SRC_URI`:

``` bitbake
SRC_URI = "git://github.com/singaravela45/smart-attendance.git;protocol=https;branch=main;"
```

Replace it with your own fork's repository URL:

``` bitbake
SRC_URI = "git://github.com/YOUR_USERNAME/smart-attendance.git;protocol=https;branch=main;"
```

Replace `YOUR_USERNAME` with your actual GitHub username.

> \[!IMPORTANT\] Make sure your fork is publicly accessible or otherwise
> configured for Git access by the build environment. Also, ensure the
> branch specified in `SRC_URI` exists in your repository.

**Step 7: Rebuild the Yocto image**

After updating the recipe, return to your Yocto workspace and rebuild:

``` bash
cd ~/projects/yocto-scarthgap
source openembedded-core/oe-init-build-env build-rpi
bitbake custom-image
```

Yocto will fetch the application source code from your fork and include
it in the generated image.

> \[!NOTE\] Application source-code modifications, including changes to
> `main.py`, `known_faces/`, and `models/`, should be made in your fork
> of the `smart-attendance` repository.
>
> Email configuration and Yocto image configuration should be maintained
> in the `meta-custom` layer.

------------------------------------------------------------------------

### 6. Build the image

From your Yocto workspace, initialise the build environment and build:

``` bash
cd ~/projects/yocto-scarthgap
source openembedded-core/oe-init-build-env build-rpi
bitbake custom-image
```

The generated image is placed in:

``` text
build-rpi/tmp/deploy/images/raspberrypi4-64/
```

### 7. Flash the image

Write the image file (ending in `.wic.bz2`) to the SD
card with [Raspberry Pi Imager](https://www.raspberrypi.com/software/),
[balenaEtcher](https://etcher.balena.io/), or the command line:

``` bash
bzip2 -dc <image-file>.wic.bz2 | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync
```

> \[!CAUTION\] Replace `/dev/sdX` with your SD card device. Writing to
> the wrong device will erase its data.

### 8. Boot and use

1.  Insert the SD card, connect the USB webcam and network, and power on
    the Raspberry Pi 4.
2.  The `face-attendance` service starts automatically.
3.  The application automatically detects the connected USB webcam.
4.  Attendance is written to `/home/root/files/attendance.csv`.

------------------------------------------------------------------------

### Default login credentials

The default login credentials for the image are:

| Username | Password |
|---|---|
| `root` | `Password` |

> [!WARNING]
> Change the default password before deploying the device. The default password is intended for initial login and testing only.

### Changing the default password

The root password is configured in:

```text
meta-custom/recipes-core/images/custom-image.bb
```

The current configuration uses the following `EXTRA_USERS_PARAMS`:

```bitbake
EXTRA_USERS_PARAMS = " \
    usermod -p '\$6\$jwQuEbK4sX5f4gao\$oUEeHga4ah8NquPOBTtLgoj/TsXn6vBf84dReuFwEISZK4T5qMCw00p1agl4r9MVzINi3I7eR/vrlzJCjXfR8.' root; \
"
```

To set a different password:

1. Generate a SHA-512 password hash on your Linux build machine:

   ```bash
   openssl passwd -6
   ```

   Enter your new password when prompted. The command prints a hash beginning with `$6$`.

2. Replace the existing hash in `EXTRA_USERS_PARAMS` in `custom-image.bb` with the newly generated hash. **Escape each `$` as `\$`** in the BitBake recipe. For example:

   ```bitbake
   EXTRA_USERS_PARAMS = " \
       usermod -p '\$6\$your-salt\$your-generated-password-hash' root; \
   "
   ```

3. Save the recipe and rebuild the image:

   ```bash
   bitbake custom-image
   ```

   Flash the newly generated image to the SD card. The root account will use the password corresponding to the hash you configured.

> [!NOTE]
> Changing `EXTRA_USERS_PARAMS` affects newly built images only. To change the password on a Raspberry Pi that has already been flashed, log in as `root` and run `passwd`.

---

## Managing the service

The application runs as the `face-attendance` systemd service:

``` bash
systemctl status face-attendance        # running or failed
journalctl -u face-attendance -f        # live logs
systemctl restart face-attendance       # after editing .env
systemctl stop face-attendance          # stop it
systemctl disable face-attendance       # no autostart
```

To change settings on the board, edit `/home/root/files/.env` and run
`systemctl restart face-attendance`.

To make a change permanent, update `.env` in this layer and rebuild the
image.

To permanently change the application source code, update your fork of
the `smart-attendance` repository and modify `SRC_URI` in
`smart-attendance.bb` if necessary, then rebuild the image.

------------------------------------------------------------------------

## Troubleshooting

| Problem | What to check |
|---|---|
| No alert emails | Check `journalctl -u face-attendance -f`. Make sure all three email values are set, the Pi is online, and you are using a Gmail **app password**. |
| Wrong times in attendance | The Raspberry Pi 4 has no battery-backed clock. Check the time with `date` and make sure the Pi can reach a time server. |
| Known people not recognised | Add more varied photos per person to the `known_faces/` directory in your application repository, or adjust `FACE_CONFIDENCE_THRESHOLD`. |
| Strangers recognised as known people | Lower `FACE_CONFIDENCE_THRESHOLD` to make matching stricter. |
| Application changes are not reflected in the image | Check that your fork contains the latest changes and that `SRC_URI` in `smart-attendance.bb` points to the correct repository and branch. Rebuild the image. |------------------------------------------------------------------------

## Limitations

-   Recognition uses classic OpenCV methods (Haar Cascade + LBPH). It
    does **not** detect spoofing, so a photo held up to the camera may
    be accepted as a real person. It is suitable for a demo or low-risk
    attendance use, not for access control.
-   The device stores face photos and sends photos of unknown people by
    email. Make sure you have the consent your local data-protection
    rules require.
-   The application source code is fetched from GitHub during the Yocto
    build. An internet connection is therefore required on the build
    machine when the source is not already available in the download
    cache.
