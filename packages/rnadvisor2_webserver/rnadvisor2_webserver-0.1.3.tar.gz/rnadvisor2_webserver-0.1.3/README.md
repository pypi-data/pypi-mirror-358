<div align="center">

<!-- omit in toc -->
# RNAdvisor webserver 
<strong>Fast and easy way to compute RNA 3D structural quality</strong>

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python](https://img.shields.io/pypi/pyversions/tensorflow.svg)](https://badge.fury.io/py/tensorflow)
[![DOI](https://img.shields.io/badge/DOI-10.1093/bib/bbae064-green)](https://doi.org/10.1093/bib/bbae064)
[![PyPI version](https://badge.fury.io/py/rnadvisor2-webserver.svg)](https://pypi.org/project/rnadvisor2-webserver/)


</div>

RNAdvisor is a wrapper tool for the computation of RNA 3D structural quality assessment. 
It uses [docker compose](https://docs.docker.com/compose/) to run the RNAdvisor tool in a containerized environment. 

This code is a webserver that allows users to upload RNA structures and get quality scores in return.

![img](img/rnadvisor2_screen.gif)

# Installation

To install the RNAdvisor webserver, please first make sure [Docker](https://www.docker.com/) and [docker compose](https://docs.docker.com/compose/) are 
installed on you system. 

Then, you need to clone the Docker images using: 

```bash
make install_docker_images
```
or: 
```bash
source ./installations/install_metrics.sh
```

Then, you can install the webserver using pip:
```bash
pip install rnadvisor2_webserver
```

# Usage

To run the webserver, you can use the following command:

```bash
rnadvisor2_webserver
```

Then, the webserver should be accessible in your browser at ` http://0.0.0.0:8501/RNAdvisor`.