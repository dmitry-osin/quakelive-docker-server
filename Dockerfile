FROM ubuntu:24.04 AS quakeliveserver

RUN set -x \
    && apt-get update \
    && apt-get -y install software-properties-common wget curl git build-essential

RUN set -x \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get -y install python3.8 python3.8-dev python3.8-distutils

RUN set -x \
    && rm /usr/bin/python3 \
    && ln -s /usr/bin/python3.8 /usr/bin/python3 \
    && ln -s /usr/bin/python3.8-config /usr/bin/python3-config \
    && python3 --version

RUN set -x \
    && apt-get -y install lib32gcc-s1

RUN set -x \
    && mkdir /root/Steam && cd /root/Steam \
    && curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf -

RUN set -x \
    && /root/Steam/steamcmd.sh +login anonymous +app_update 349090 +quit

RUN set -x \
    && ln -s "/root/Steam/steamapps/common/Quake Live Dedicated Server/" /root/Steam/steamapps/common/qlds

RUN set -x \
    && git clone https://github.com/dmitry-osin/minqlx /root/Steam/steamapps/common/qlds/minqlx \
    && cd /root/Steam/steamapps/common/qlds/minqlx \
    && make \
    && cp /root/Steam/steamapps/common/qlds/minqlx/bin/* /root/Steam/steamapps/common/qlds

RUN set -x \
    && mkdir /root/Steam/steamapps/common/qlds/minqlx-plugins \
    && cd /root/Steam/steamapps/common/qlds/minqlx-plugins \
    && wget https://bootstrap.pypa.io/get-pip.py \
    && python3 /root/Steam/steamapps/common/qlds/minqlx-plugins/get-pip.py \
    && rm /root/Steam/steamapps/common/qlds/minqlx-plugins/get-pip.py \
    && git clone https://github.com/dmitry-osin/minqlx-plugins.git /root/Steam/steamapps/common/qlds/minqlx-plugins \
    && python3 -m pip install -r /root/Steam/steamapps/common/qlds/minqlx-plugins/requirements.txt

RUN set -x \
    && mkdir /root/Steam/script \
    && cd /root/Steam/script

RUN set -x \
    && mkdir /root/Steam/steamapps/common/qlds/baseq3/workshop

COPY ./script/autodownload.sh /root/Steam/script/
COPY ./init/workshop.txt /root/Steam/steamapps/common/qlds/baseq3/

RUN set -x \
    && mkdir -p /root/Steam/steamapps/common/qlds/steamapps/workshop

RUN set -x \
    && chmod +x /root/Steam/script/autodownload.sh \
    && /root/Steam/script/autodownload.sh

RUN set -x \
    && rm /root/Steam/steamapps/common/qlds/baseq3/workshop.txt

CMD \
    INSTALLED_QLX_PLUGINS=`find /root/Steam/steamapps/common/qlds/minqlx-plugins/*.py | grep -v "__init__" | sed 's!.*/!!' | sed 's!\.py!!' | xargs | tr ' ' ', '` \
    && set -x \
    # if NET_PORT is not set then set it to the default port of 27960
    && export NET_PORT=${NET_PORT:-27960} \
    # if ZMQ_STATS_PORT is not set then set it to NET_PORT
    && export ZMQ_STATS_PORT=${ZMQ_STATS_PORT:-$NET_PORT} \
    # if ZMQ_RCON_PORT is not set then set it to NET_PORT + 1000
    && export ZMQ_RCON_PORT=${ZMQ_RCON_PORT:-$(($NET_PORT + 1000))} \
    # if SERVERSTARTUP is not set we need to set it because otherwise the server will
    # not start properly
    && export SERVERSTARTUP="${SERVERSTARTUP:-startRandomMap}" \
    # if QLX_PLUGINS is not set then set it to the list of present plugins in the minqlx-plugins directory
    && export QLX_PLUGINS=${QLX_PLUGINS:-$INSTALLED_QLX_PLUGINS} \
    # start the minqlx extended quake live server
    && /root/Steam/steamapps/common/qlds/run_server_x64_minqlx.sh \
    # only attach a cvar parameter if the environment variable is set
    ${NET_PORT:++set net_port ${NET_PORT}} \
    ${ZMQ_RCON_PORT:++set zmq_rcon_port ${ZMQ_RCON_PORT}} \
    ${ZMQ_STATS_PORT:++set zmq_stats_port ${ZMQ_STATS_PORT}} \
    ${SERVERSTARTUP:++set serverstartup ${SERVERSTARTUP}} \
    ${SV_HOSTNAME:++set sv_hostname ${SV_HOSTNAME}} \
    ${SV_TAGS:++set sv_tags ${SV_TAGS}} \
    ${G_PASSWORD:++set g_password ${G_PASSWORD}} \
    ${SV_MAXCLIENTS:++set sv_maxClients ${SV_MAXCLIENTS}} \
    ${SV_PRIVATECLIENTS:++set sv_privateClients ${SV_PRIVATECLIENTS}} \
    ${SV_PRIVATEPASSWORD:++set sv_privatePassword ${SV_PRIVATEPASSWORD}} \
    ${COM_HUNKMEGS:++set com_hunkMegs ${COM_HUNKMEGS}} \
    ${COM_ZONEMEGS:++set com_zoneMegs ${COM_ZONEMEGS}} \
    ${G_ALLOWVOTEMIDGAME:++set g_allowVoteMidGame ${G_ALLOWVOTEMIDGAME}} \
    ${ZMQ_RCON_PASSWORD:++set zmq_rcon_password ${ZMQ_RCON_PASSWORD}} \
    ${ZMQ_STATS_PASSWORD:++set zmq_stats_password ${ZMQ_STATS_PASSWORD}} \
    ${QLX_WORKSHOP_REFERENCES:++set qlx_workshopReferences ${QLX_WORKSHOP_REFERENCES}} \
    ${G_VOTEFLAGS:++set g_voteFlags ${G_VOTEFLAGS}} \
    ${G_INACTIVITY:++set g_inactivity ${G_INACTIVITY}} \
    ${QLX_OWNER:++set qlx_owner ${QLX_OWNER}} \
    ${G_TIMEOUTCOUNT:++set g_timeoutCount ${G_TIMEOUTCOUNT}} \
    ${SV_INCLUDECURRENTMAPINVOTE:++set sv_includeCurrentMapInVote ${SV_INCLUDECURRENTMAPINVOTE}} \
    ${QLX_SERVERBRANDNAME:++set qlx_serverBrandName ${QLX_SERVERBRANDNAME}} \
    ${QLX_SERVERBRANDTOPFIELD:++set qlx_serverBrandTopField ${QLX_SERVERBRANDTOPFIELD}} \
    ${QLX_CONNECTMESSAGE:++set qlx_connectMessage ${QLX_CONNECTMESSAGE}} \
    ${QLX_MMDEFAULTMAP:++set qlx_mmDefaultMap ${QLX_MMDEFAULTMAP}} \
    ${QLX_ENFORCESTEAMNAME:++set qlx_enforceSteamName ${QLX_ENFORCESTEAMNAME}} \
    ${QLX_PLUGINS:++set qlx_plugins ${QLX_PLUGINS}}


