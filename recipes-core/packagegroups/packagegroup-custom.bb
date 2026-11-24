SUMMARY = "Custom Package Group"
LICENSE = "MIT"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

RDEPENDS:${PN} = " \
    smart-attendance-files \
    python3-core \
    python3-numpy \
    python3-opencv \
    ca-certificates \
    v4l-utils \
    usbutils \
    nano \
    kernel-module-uvcvideo \
"
