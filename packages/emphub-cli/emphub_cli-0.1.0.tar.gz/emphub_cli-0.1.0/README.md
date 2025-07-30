# emphub-cli

CLI tools to interface with EMPHub.

## Installation

First, install the package:
```sh
python3 -m pip install emphub-cli
```
then add a configuration file to connect to the EMPHub instance at `~/.emp/config.yaml`

The configuration file has the following format:
```yaml
---
registry:
    host: <S3 HOST>
    access_key: <S3 ACCESS KEY>
    secret_key: <S3 SECRET KEY>
    secure: false  # set to true if using HTTPS
    bucket: emp-packages

local-storage:
    path: ~/.emp/packages
    connections_file: ~/.emp/connections.xml
```

## Usage

To view all packages available on EMPHub, use the following command:
```sh
emp packages
```
To see the tags for a given package, use the `tags` command:
```sh
emp tags <PACKAGE>
```
Then to pull a specific tag use the following command:
```sh
emp pull <PACKAGE>:<TAG>
```
The bitfile will then be available at `~/.emp/packages/<PACKAGE>/<TAG>/package/top.bit`, along with the address table and a pre-made `connections.xml` for the Serenity card.
