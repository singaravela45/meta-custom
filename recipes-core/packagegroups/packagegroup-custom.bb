SUMMARY = "Custom Package Group"
LICENSE = "MIT"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

RDEPENDS:${PN} = " \
    allfiles \
    python3-core \
    python3-numpy \
    python3-opencv \
    python3-datetime \
    python3-email \
    python3-netclient \
    ca-certificates \
    v4l-utils \
    usbutils \
    nano \
    kernel-module-uvcvideo \
"
