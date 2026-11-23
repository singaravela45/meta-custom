SUMMARY = "Face Recognition Application Files"
LICENSE = "CLOSED"

SRC_URI = "git://github.com/singaravela45/smart-attendance.git;protocol=https;branch=main;"
SRC_URI:append = " file://.env"
SRCREV = "${AUTOREV}"
S = "${WORKDIR}/git"
APP_DIR = "/home/root/files"
inherit systemd

SYSTEMD_SERVICE:${PN} = "face-attendance.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install() {

    install -d ${D}${APP_DIR}

    # Main application
    install -m 0755 ${S}/main.py ${D}${APP_DIR}/main.py

    # Known faces
    install -d ${D}${APP_DIR}/known_faces

    cp -r ${S}/known_faces/. ${D}${APP_DIR}/known_faces/

    # Haar Cascade model
    install -d ${D}${APP_DIR}/models

    cp -r ${S}/models/. ${D}${APP_DIR}/models/

    # Environment file
    install -m 0600 ${WORKDIR}/.env ${D}${APP_DIR}/.env

    #enable systemd
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${S}/face-attendance.service ${D}${systemd_system_unitdir}/
}

FILES:${PN} += "${APP_DIR}"