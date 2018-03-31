
FROM monroe/base
MAINTAINER Ana Custura <ana@netstat.org.uk>

RUN apt-get update
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y tcpdump patch
RUN echo "deb http://ftp.debian.org/debian testing main" >> /etc/apt/sources.list
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y -t testing python-pyroute2 python-ipaddress python-scapy && apt-get clean
COPY files/* /opt/monroe/
ENTRYPOINT ["dumb-init", "--", "./opt/monroe/trace-wr.py"]
