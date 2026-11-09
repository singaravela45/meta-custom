SUMMARY = "Face Recognition Application"
LICENSE = "CLOSED"

SRC_URI = " \
    file://main.py \
    file://known_faces \
"

S = "${WORKDIR}"

do_install() {
    # Create the target directories inside /home/root/files
    install -d ${D}${ROOT_HOME}/files/known_faces

    # Install the main Python script into the files directory
    install -m 0755 ${WORKDIR}/main.py ${D}${ROOT_HOME}/files/main.py

    # Copy the known_faces data into the files directory
    cp -r ${WORKDIR}/known_faces/* ${D}${ROOT_HOME}/files/known_faces/
}

# Tell Yocto to package the entire /home/root/files directory
FILES:${PN} += "${ROOT_HOME}/files"

RDEPENDS:${PN} += " \
    python3 \
    python3-numpy \
    python3-opencv \
"
