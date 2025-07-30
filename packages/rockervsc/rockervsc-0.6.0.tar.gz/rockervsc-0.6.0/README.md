# rockervsc

## Continuous Integration Status

[![Ci](https://github.com/blooop/rockervsc/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/blooop/rockervsc/actions/workflows/ci.yml?query=branch%3Amain)
[![Codecov](https://codecov.io/gh/blooop/rockervsc/branch/main/graph/badge.svg?token=Y212GW1PG6)](https://codecov.io/gh/blooop/rockervsc)
[![GitHub issues](https://img.shields.io/github/issues/blooop/rockervsc.svg)](https://GitHub.com/blooop/rockervsc/issues/)
[![GitHub pull-requests merged](https://badgen.net/github/merged-prs/blooop/rockervsc)](https://github.com/blooop/rockervsc/pulls?q=is%3Amerged)
[![GitHub release](https://img.shields.io/github/release/blooop/rockervsc.svg)](https://GitHub.com/blooop/rockervsc/releases/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/rockervsc)](https://pypistats.org/packages/rockervsc)
[![License](https://img.shields.io/github/license/blooop/rockervsc)](https://opensource.org/license/mit/)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/downloads/)
[![Pixi Badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json)](https://pixi.sh)

# Intro

[Rocker](https://github.com/osrf/rocker) is an alternative to docker-compose that makes it easier to run containers with access to features of the local environment and add extra capabilities to existing docker images.  I do most of my development in vscode with the devcontainers extension so this wrapper simplifies that workflow.  Rather than calling rocker and then attaching vscode, this wrapper combines those actions into one command. 

## Installation

First, install [pipx](https://pypa.github.io/pipx/) if you don't have it already:

```
sudo apt update && sudo apt install -y pipx
pipx ensurepath
```

Then install rockervsc with pipx:

```
pipx install --include-deps rockervsc
```

This will install `rockervsc` ,`rockerc` and `rocker` as a globally available tool on your system. 
```

## Usage

To run rocker and automatically launch and attach a vscode instance, run this command:

```
rockervsc 
```

You can pass all the normal rocker arguments to rockervsc and it will forward them to rocker, e.g.:

```
rockervsc --x11 --nvidia
```

by default rockervsc calls [rockerc](https://github.com/blooop/rockerc) so instead of passing arguments explicitly you can have a rockerc.yaml file in your workspace

```yaml
image: ubuntu:22.04
args:
  - nvidia
  - x11 
  - user 
  - git 

```

and running:
```bash
rockervsc
```

will launch and attach vscode to the container with nvidia, x11, the current user id and git set up for you.

## Caveats

I'm not sure this is the best way of implementing rockervsc like functionality.  It might be better to implement it as a rocker extension, or in rocker itself.  This was just the simplest way to get started. I may explore those other options in more detail in the future.

