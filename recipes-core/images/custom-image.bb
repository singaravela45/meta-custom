SUMMARY = "A small image just capable of allowing a device to boot."
LICENSE = "CLOSED"
IMAGE_INSTALL = "packagegroup-core-boot ${CORE_IMAGE_EXTRA_INSTALL}"
IMAGE_INSTALL:append = " \
    packagegroup \
"
IMAGE_FEATURES += "debug-tweaks"
IMAGE_LINGUAS = " "

LICENSE = "MIT"

inherit core-image
IMAGE_OVERHEAD_FACTOR ?= "1.3"
IMAGE_ROOTFS_SIZE ?= "524288"
IMAGE_ROOTFS_EXTRA_SPACE = "4096"
IMAGE_ROOTFS_EXTRA_SPACE:append = "${@bb.utils.contains("DISTRO_FEATURES", "systemd", " + 4096", "", d)}"
