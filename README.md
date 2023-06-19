# aiida-finale

AiiDA client to interact with a [finale server](https://github.com/BIG-MAP/finale).

Currently this is a test model.

## Installation

Requires AiiDA, so make sure you have the necessary services (PostgreSQL and RabbitMQ) installed and running.

```shell
  pip install -e .
  verdi quicksetup  # better to set up a new profile
```

## Usage

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
