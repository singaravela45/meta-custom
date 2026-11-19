
SUMMARY = "Face Recognition Application Files"
LICENSE = "CLOSED"

SRC_URI = " \
    file://main.py \
    file://.env \
    file://known_faces/ \
    file://models/ \
    file://face-attendance.service \
"

S = "${WORKDIR}"

APP_DIR = "/home/root/files"

# Enable systemd integration
inherit systemd

SYSTEMD_SERVICE:${PN} = "face-attendance.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

do_install() {

    install -d ${D}${APP_DIR}

    # Main application
    install -m 0755 \
        ${WORKDIR}/main.py \
        ${D}${APP_DIR}/main.py

    # Environment file
    install -m 0600 \
        ${WORKDIR}/.env \
        ${D}${APP_DIR}/.env

    # Known faces
    install -d ${D}${APP_DIR}/known_faces

    cp -r ${WORKDIR}/known_faces/. \
        ${D}${APP_DIR}/known_faces/

    # Haar Cascade model
    install -d ${D}${APP_DIR}/models

    cp -r ${WORKDIR}/models/. \
        ${D}${APP_DIR}/models/

    # Install systemd service
    install -d ${D}${systemd_system_unitdir}

    install -m 0644 \
        ${WORKDIR}/face-attendance.service \
        ${D}${systemd_system_unitdir}/face-attendance.service
}

FILES:${PN} += " \
    ${APP_DIR} \
    ${systemd_system_unitdir}/face-attendance.service \
"