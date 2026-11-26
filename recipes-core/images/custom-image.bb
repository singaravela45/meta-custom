SUMMARY = "A custom image for the face-recognition application"
LICENSE = "CLOSED"

IMAGE_INSTALL = "packagegroup-core-boot ${CORE_IMAGE_EXTRA_INSTALL}"
IMAGE_INSTALL:append = " packagegroup-custom"
IMAGE_FEATURES += " \
    ssh-server-openssh \
    allow-root-login  \ 
"
IMAGE_LINGUAS = " "
EXTRA_USERS_PARAMS = " \
    usermod -p '\$6\$jwQuEbK4sX5f4gao\$oUEeHga4ah8NquPOBTtLgoj/TsXn6vBf84dReuFwEISZK4T5qMCw00p1agl4r9MVzINi3I7eR/vrlzJCjXfR8.' root; \
"

inherit core-image extrausers
IMAGE_OVERHEAD_FACTOR ?= "1.3"
IMAGE_ROOTFS_SIZE ?= "524288"
IMAGE_ROOTFS_EXTRA_SPACE = "4096"
IMAGE_ROOTFS_EXTRA_SPACE:append = "${@bb.utils.contains("DISTRO_FEATURES", "systemd", " + 4096", "", d)}"
