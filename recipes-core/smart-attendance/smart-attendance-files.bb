SUMMARY = "Face Recognition Application Files"
LICENSE = "CLOSED"

SRC_URI = "git://github.com/singaravela45/meta-custom.git;protocol=https;branch=wrynose;subpath=recipes-core/smart-attendance/files"
SRCREV = "${AUTOREV}"

S = "${UNPACKDIR}/files"

APP_DIR = "/home/root/files"
inherit systemd

SYSTEMD_SERVICE:${PN} = "face-attendance.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install() {

    install -d ${D}${APP_DIR}

    # Main application
    install -m 0755 ${UNPACKDIR}/main.py ${D}${APP_DIR}/main.py

    # Environment file
    install -m 0600 ${UNPACKDIR}/.env ${D}${APP_DIR}/.env

    # Known faces
    install -d ${D}${APP_DIR}/known_faces

    cp -r ${UNPACKDIR}/known_faces/. ${D}${APP_DIR}/known_faces/

    # Haar Cascade model
    install -d ${D}${APP_DIR}/models

    cp -r ${UNPACKDIR}/models/. ${D}${APP_DIR}/models/

    #enable systemd
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${S}/face-attendance.service ${D}${systemd_system_unitdir}/
}

FILES:${PN} += "${APP_DIR}"
