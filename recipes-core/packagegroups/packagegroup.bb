SUMMARY = "My Project Package Group"
LICENSE = "MIT"

PACKAGE_ARCH = "${TUNE_PKGARCH}"

inherit packagegroup

RDEPENDS:${PN} = " \
    python3 \
    python3-pip \
    python3-numpy \
    python3-opencv \
    python3-pillow \
    opencv \
    v4l-utils \
    usbutils \
    curl \
    nano \
    rpi-gpio \
    cmake \
    pkgconfig \
    mesa \
    libx11 \
    glib-2.0 \
    allfiles \
"
