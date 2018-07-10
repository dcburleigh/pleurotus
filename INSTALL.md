# Installation


## Prerequisites

* Git
* Python 3.6+
** module:  ruamel.yaml

## code directory

* clone this repo into GIT/pleurotus

## working s directory

mkdir gp
cd gp
cp  GIT/pleurotus/scripts/makefile .

edit makefile.conf

make install-gp

## Configuration

edit ETC/projects.yml

see projects.example.yml for details

## verify

make gp-doc

python example.py
