######## INSTALL ########

# Set the base image
FROM ubuntu:24.04

# Set environment variables
ENV USER root
ENV HOME /root

ENV QLDS_DIR /root/Steam/steamapps/common/qlds
ENV MINQLX_PLUGINS_DIR /root/Steam/steamapps/common/qlds/minqlx-plugins
ENV WORKSHOP_DIR /root/Steam/steamapps/common/qlds/baseq3/workshop
ENV SCRIPTS_DIR /root/Steam/script
ENV STEAMCMD /usr/bin/steamcmd

ENV MINQLX_REPO_URL https://github.com/dmitry-osin/minqlx.git
ENV MINQLX_PLUGINS_REPO_URL https://github.com/dmitry-osin/minqlx-plugins.git

# Set working directory
WORKDIR $HOME

# Insert Steam prompt answers
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN echo steam steam/question select "I AGREE" | debconf-set-selections \
 && echo steam steam/license note '' | debconf-set-selections

# Update the repository and install SteamCMD
ARG DEBIAN_FRONTEND=noninteractive
RUN dpkg --add-architecture i386 \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends ca-certificates locales steamcmd lib32stdc++6 lib32gcc-s1 \
 && rm -rf /var/lib/apt/lists/*

# Add unicode support
RUN locale-gen en_US.UTF-8
ENV LANG 'en_US.UTF-8'
ENV LANGUAGE 'en_US:en'

# Create symlink for executable
RUN ln -s /usr/games/steamcmd /usr/bin/steamcmd

# Update SteamCMD and verify latest version
RUN steamcmd +quit

# Fix missing directories and libraries
RUN mkdir -p $HOME/.steam \
 && ln -s $HOME/.local/share/Steam/steamcmd/linux32 $HOME/.steam/sdk32 \
 && ln -s $HOME/.local/share/Steam/steamcmd/linux64 $HOME/.steam/sdk64 \
 && ln -s $HOME/.steam/sdk32/steamclient.so $HOME/.steam/sdk32/steamservice.so \
 && ln -s $HOME/.steam/sdk64/steamclient.so $HOME/.steam/sdk64/steamservice.so

RUN set -x \
    && apt-get update \
    && apt-get -y install software-properties-common wget curl git build-essential mc nano unzip zip

RUN set -x \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update -y \
    && apt-get -y install python3.8 python3.8-dev python3.8-distutils

RUN set -x \
    && rm /usr/bin/python3 \
    && ln -s /usr/bin/python3.8 /usr/bin/python3 \
    && ln -s /usr/bin/python3.8-config /usr/bin/python3-config

RUN set -x \
    && /usr/bin/steamcmd +login anonymous +force_install_dir $QLDS_DIR +app_update 349090 validate +quit

RUN set -x \
    && git clone $MINQLX_REPO_URL $QLDS_DIR/minqlx \
    && cd $QLDS_DIR/minqlx \
    && make \
    && cp $QLDS_DIR/minqlx/bin/* $QLDS_DIR

RUN set -x \
    && mkdir $MINQLX_PLUGINS_DIR \
    && cd $MINQLX_PLUGINS_DIR \
    && wget https://bootstrap.pypa.io/get-pip.py \
    && python3 $MINQLX_PLUGINS_DIR/get-pip.py \
    && rm $MINQLX_PLUGINS_DIR/get-pip.py \
    && git clone $MINQLX_PLUGINS_REPO_URL $MINQLX_PLUGINS_DIR \
    && python3 -m pip install -r $MINQLX_PLUGINS_DIR/requirements.txt

# Install GeoIP for player_location plugin
RUN set -x \
    && python3 -m pip install geoip2

RUN set -x \
    && mkdir $SCRIPTS_DIR

RUN set -x \
    && mkdir $QLDS_DIR/baseq3/workshop

COPY ./config/script/autodownload.py $SCRIPTS_DIR/autodownload.py
COPY ./config/init/workshop.txt $QLDS_DIR/baseq3/workshop.txt

RUN set -x \
    && mkdir -p $QLDS_DIR/steamapps/workshop

RUN set -x \
    && python3 $SCRIPTS_DIR/autodownload.py --steamcmd $STEAMCMD --workshop_file $QLDS_DIR/baseq3/workshop.txt

RUN set -x \
    && rm $QLDS_DIR/baseq3/workshop.txt

CMD \
    INSTALLED_QLX_PLUGINS=`find $MINQLX_PLUGINS_DIR/*.py | grep -v "__init__" | sed 's!.*/!!' | sed 's!\.py!!' | xargs | tr ' ' ', '` \
        && set -x \
        # if NET_PORT is not set then set it to the default port of 27960
        && export NET_PORT=${NET_PORT:-27960} \
        # if ZMQ_STATS_PORT is not set then set it to NET_PORT
        && export ZMQ_STATS_PORT=${ZMQ_STATS_PORT:-$NET_PORT} \
        # if ZMQ_RCON_PORT is not set then set it to NET_PORT + 1000
        && export ZMQ_RCON_PORT=${ZMQ_RCON_PORT:-$(($NET_PORT + 1000))} \
        # if SV_FPS is not set then set it to the default
        && export SV_FPS=${SV_FPS:-40} \
        # if SERVERSTARTUP is not set we need to set it because otherwise the server will
        # not start properly
        && export SERVERSTARTUP="${SERVERSTARTUP:-startRandomMap}" \
        # if QLX_PLUGINS is not set then set it to the list of present plugins in the minqlx-plugins directory
        && export QLX_PLUGINS=${QLX_PLUGINS:-$INSTALLED_QLX_PLUGINS} \
        # if QLX_BALANCEAPI is not set then set it to the default
        && export QLX_BALANCEAPI=${QLX_BALANCEAPI:-elo} \
        # start the minqlx extended quake live server
        && $QLDS_DIR/run_server_x64_minqlx.sh \
        # only attach a cvar parameter if the environment variable is set
        ${NET_PORT:++set net_port ${NET_PORT}} \
        ${ZMQ_RCON_PORT:++set zmq_rcon_port ${ZMQ_RCON_PORT}} \
        ${ZMQ_STATS_PORT:++set zmq_stats_port ${ZMQ_STATS_PORT}} \
        ${ZMQ_RCON_PASSWORD:++set zmq_rcon_password ${ZMQ_RCON_PASSWORD}} \
        ${ZMQ_STATS_PASSWORD:++set zmq_stats_password ${ZMQ_STATS_PASSWORD}} \
        ${SERVERSTARTUP:++set serverstartup ${SERVERSTARTUP}} \
        ${SV_HOSTNAME:++set sv_hostname ${SV_HOSTNAME}} \
        ${SV_TAGS:++set sv_tags ${SV_TAGS}} \
        ${SV_FPS:++set sv_fps ${SV_FPS}} \
        ${SV_SERVERTYPE:++set sv_serverType ${SV_SERVERTYPE}} \
        ${G_PASSWORD:++set g_password ${G_PASSWORD}} \
        ${SV_MAXCLIENTS:++set sv_maxClients ${SV_MAXCLIENTS}} \
        ${SV_PRIVATECLIENTS:++set sv_privateClients ${SV_PRIVATECLIENTS}} \
        ${SV_PRIVATEPASSWORD:++set sv_privatePassword ${SV_PRIVATEPASSWORD}} \
        ${QLX_WORKSHOPREFERENCES:++set qlx_workshopReferences ${QLX_WORKSHOPREFERENCES}} \
        ${COM_ZONEMEGS:++set com_zoneMegs ${COM_ZONEMEGS}} \
        ${COM_HUNKMEGS:++set com_hunkMegs ${COM_HUNKMEGS}} \
        ${G_ALLOWVOTEMIDGAME:++set g_allowVoteMidGame ${G_ALLOWVOTEMIDGAME}} \
        ${G_VOTEFLAGS:++set g_voteFlags ${G_VOTEFLAGS}} \
        ${G_INACTIVITY:++set g_inactivity ${G_INACTIVITY}} \
        ${QLX_OWNER:++set qlx_owner ${QLX_OWNER}} \
        ${G_TIMEOUTCOUNT:++set g_timeoutCount ${G_TIMEOUTCOUNT}} \
        ${SV_INCLUDECURRENTMAPINVOTE:++set sv_includeCurrentMapInVote ${SV_INCLUDECURRENTMAPINVOTE}} \
        ${QLX_SERVERBRANDNAME:++set qlx_serverBrandName ${QLX_SERVERBRANDNAME}} \
        ${QLX_SERVERBRANDTOPFIELD:++set qlx_serverBrandTopField ${QLX_SERVERBRANDTOPFIELD}} \
        ${QLX_SERVERBRANDBOTTOMFIELD:++set qlx_serverBrandBottomField ${QLX_SERVERBRANDBOTTOMFIELD}} \
        ${QLX_LOADEDMESSAGE:++set qlx_loadedMessage ${QLX_LOADEDMESSAGE}} \
        ${QLX_COUNTDOWNMESSAGE:++set qlx_countdownMessage ${QLX_COUNTDOWNMESSAGE}} \
        ${QLX_ENDOFGAMEMESSAGE:++set qlx_endOfGameMessage ${QLX_ENDOFGAMEMESSAGE}} \
        ${QLX_CONNECTMESSAGE:++set qlx_connectMessage ${QLX_CONNECTMESSAGE}} \
        ${QLX_BALANCEAPI:++set qlx_balanceApi ${QLX_BALANCEAPI}} \
        ${QLX_PLUGINS:++set qlx_plugins ${QLX_PLUGINS}}
