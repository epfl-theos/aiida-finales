# aiida-finales

This is the AiiDA tenant for the [FINALES server](https://github.com/BIG-MAP/FINALES2).

It has the following capabilities:

- `conductivity` / `estimation` ([schema](https://github.com/BIG-MAP/FINALES2_schemas/tree/schemas_update/src/FINALES2_schemas/classes_input)):
  provides an estimation for the conductivity in solutions of LiPF6 in EC+PC mixtures
  (based on the model of [DOI:10.1002/batt.202200228](https://doi.org/10.1002/batt.202200228))


## Installation

The tenant must be installed in an environment that is already running AiiDA.
To set this up manually in a custom environment, check the [AiiDA](https://github.com/aiidateam/aiida-core) repository and documentation.
For an easy setup, you can use the Dockerfile included in this repository and launch the tenant in a container.

In any case, you will always have to download the latest [release](https://github.com/ramirezfranciscof/aiida-finales/releases) or clone the repository (better for development):

```console
(env) user@box:dir$ git clone git@github.com:ramirezfranciscof/aiida-finales.git
```

For launching the tenant in a container, you only need to have [Docker](https://docker.com/) installed in your system.
We include some useful bashscripts to facilitate the use of Docker in UNIX systems.
You can find them inside of the `.docker/control` folder.

First you will need to create the docker image (the template used to launch the container from).
For this you can use the `cmdrun_build.sh` script or go to the root folder (where the `Dockerfile` is) and run:

```console
(env) user@box:aiida-finales$ docker build -t "aiida_finales_image"
```
You can replace `aiida_finales_image` by the name you want to use for the image,
but you will need to be consistent in the folowing commands.

Next you need to launch the container for the first time and set all connections using `cmdrun_init.sh`.
Manually, this means running:

```console
(env) user@box:aiida-finales$ docker run \
        --name finales_tenant \
        -p 8888:8888 \
        -p 13371:13371 \
        --add-host=host.docker.internal:host-gateway \
        aiida_finales_image
```

As last time, you can change `finales_tenant` by the name you want the container to have.
The command to `--add-host` is only necessary if you are running the FINALES server locally in (another container in) your host system.
You can leave it out if you are going to connect with a remote deployment.

Note that the previous command should have locked your terminal.

## Usage (to update)

Put requests for the test in the finale server:

```shell
  aiida-finale test populate -c config_file.yaml
```

The `config_file.yaml` requires the following content:

```yaml
---
 ip_url: "localhost" # ip or url address of the finale server
 port: 13371 # port used to connect to the finale server
 username: "other" # username in the finale server
 aiida_profile: "aiida_finale" # name of the local aiida profile to use for running the calculations
```

You will be prompted for a password to validate your credentials.

Note that the `aiida_profile` is not necessary for submitting the requests, but it is for running the client.

Start running the server (it blocks the terminal, you can exit by ctrl+C)

```shell
  aiida-finale client start -c config_file.yaml
```
