# This will build mjpg-streamer in a container for the raspberry pi
# and run it over jpeg stills produced by a pi camera
# useful for libreelec which is limited by addons
#
# docker run -d \
# --privileged \
# -p 8081:8080 <container-name-or-id>
#
# stream available at your_ip:8081
#
from resin/rpi-raspbian:stretch
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libjpeg8-dev imagemagick libv4l-dev build-essential gcc cmake
RUN apt-get install -y wget unzip subversion libraspberrypi-dev libraspberrypi-bin
RUN  wget  https://sourceforge.net/code-snapshots/svn/m/mj/mjpg-streamer/code/mjpg-streamer-code-182.zip
RUN unzip mjpg-streamer-code-182.zip
WORKDIR mjpg-streamer-code-182/mjpg-streamer/
RUN  ln -s /usr/include/linux/videodev2.h /usr/include/linux/videodev.h
RUN make mjpg_streamer input_file.so output_http.so
RUN cp mjpg_streamer /usr/local/bin
RUN cp output_http.so input_file.so /usr/local/lib/
RUN  cp -R www /usr/local/www
RUN mkdir /tmp/stream
COPY stream_from_pi.sh /
ENTRYPOINT /bin/bash /stream_from_pi.sh
