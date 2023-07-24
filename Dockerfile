#FROM aiidalab/aiidalab-docker-stack:22.8.1
FROM aiidalab/full-stack:latest

# For development purposes
USER root
RUN apt-get update && \
    apt-get install -y git vim screen

USER jovyan

RUN mkdir -p /home/jovyan/work/aiida_finales
COPY --chown=jovyan:users . /home/jovyan/work/aiida_finales/.
COPY --chown=jovyan:users .docker/configs/ssh_config /home/jovyan/.ssh/config

RUN pip install -e /home/jovyan/work/aiida_finales[devs,docs]

#COPY setups/ssh/config /home/jovyan/.

#USER root
#RUN fix-permissions /home/jovyan/config

#USER jovyan
###COPY --chown=aiida:users setups/ssh/config /home/jovyan/.ssh/config
###COPY --chown=aiida:users setups/ssh/ed25519_github /home/jovyan/.ssh/ed25519_github
###COPY --chown=jovyan:users setups/ssh/ed25519_github.pub /home/jovyan/.ssh/ed25519_github.pub

###RUN chmod 600 /home/jovyan/.ssh/ed25519_github

#USER jovyan
#RUN git clone git@github.com:ramirezfranciscof/aiida-core.git /home/jovyan/work/
#USER root

#RUN echo $(ls -lhrt /home/jovyan/.ssh/)

#COPY setups/setup_ssh.sh /usr/local/bin/before-notebook.d/
