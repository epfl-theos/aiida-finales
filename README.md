[![Build Status][ci-badge]][ci-link]
[![Coverage Status][cov-badge]][cov-link]
[![Docs status][docs-badge]][docs-link]
[![PyPI version][pypi-badge]][pypi-link]

# aiida-finale

AiiDA client to interact with a finale server.

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


## License

MIT


[ci-badge]: https://github.com/aiidateam/aiida-diff/workflows/ci/badge.svg?branch=master
[ci-link]: https://github.com/aiidateam/aiida-diff/actions
[cov-badge]: https://coveralls.io/repos/github/aiidateam/aiida-diff/badge.svg?branch=master
[cov-link]: https://coveralls.io/github/aiidateam/aiida-diff?branch=master
[docs-badge]: https://readthedocs.org/projects/aiida-diff/badge
[docs-link]: http://aiida-diff.readthedocs.io/
[pypi-badge]: https://badge.fury.io/py/aiida-diff.svg
[pypi-link]: https://badge.fury.io/py/aiida-diff
