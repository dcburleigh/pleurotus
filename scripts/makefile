
REPOROOT =
ETC = /usr/local/etc/deldev

PYTHON=/usr/local/bin/python3
PIP=/usr/local/bin/pip3

PYDOC = $(PYTHON) -m pydoc

#SHELL=/bin/bash

-include makefile.conf

# ................................................................

GPSOURCE = $(REPOROOT)/pleurotus

DIRS = gproject common

$(DIRS):
	mkdir -p  $@

# configuration files
MF = projects.yml

log.yml: $(GPSOURCE)/common/gp.log.yml
	cp $< $@

CONFIG = $(MF) gp.log.yml
CONFIG = $(MF) log.yml

$(MF): %: $(ETC)/%
	cp $< $@

# main script
GPSCRIPTS = gp.py makefile  example.py projects.example.yml

$(GPSCRIPTS): %: $(GPSOURCE)/scripts/%
	cp $< $@

GPFILES = LICENSE requirements.txt  NEXTRELEASE.md

$(GPFILES): %: $(GPSOURCE)/%
	cp $< $@

update-gp: $(MF)
	@rsync -a $(GPSOURCE)/gproject/ gproject/
	@rsync -a $(GPSOURCE)/common/ common/

update-files: update-gp $(GPFILES)

install-gp: $(DIRS) update-gp $(GPSCRIPTS) $(GPFILES) $(CONFIG)

python-version:
	@$(PYTHON) --version | grep 3.7

setup-python: requirements.txt  python-version
	$(PIP) install -r requirements.txt

# ................................................................

list-versions: install-gp
	$(PYTHON) gp.py --list -v  --manifest $(MF)

ifneq ($(PROJECTNAME),)

show-project: install-gp
	@$(PYTHON) gp.py -p $(PROJECTNAME) -i

show-status: install-gp
	@$(PYTHON) gp.py -p $(PROJECTNAME) -s

show-details:  show-status  show-project  show-tags show-log-m

show-tags: install-gp
	@$(PYTHON) gp.py -p $(PROJECTNAME) -t   > t.out
	@cat t.out

# all commits since last release (master)
show-log-m: install-gp
	@$(PYTHON) gp.py -p $(PROJECTNAME) -l --since master  --manifest $(MF)  > t.out
	@cat t.out

show-log-rel: install-gp
		$(PYTHON) gp.py -p $(PROJECTNAME) -l --since release  --manifest $(MF)  > t.out
		cat t.out

verify: install-gp
	$(PYTHON) gp.py -p $(PROJECTNAME) --verify release

archive-release: install-gp
	$(PYTHON) gp.py -p $(PROJECTNAME) -a

tag-release: install-gp
	$(PYTHON) gp.py -p $(PROJECTNAME) --tag-release

endif

gp-doc: update-gp
	$(PYDOC) gp
	$(PYDOC) gproject
	$(PYDOC) gproject.gproject
	$(PYDOC) gproject.repo

ALLDOCS = gpdocs.txt
write-doc: update-gp
	echo '' > $(ALLDOCS)
	$(PYDOC) gp >> $(ALLDOCS)
	$(PYDOC) gproject >> $(ALLDOCS)
	$(PYDOC) gproject.gproject >> $(ALLDOCS)
	$(PYDOC) gproject.repo >> $(ALLDOCS)
	$(PYDOC) gproject.logger >> $(ALLDOCS)
	ls -l $(ALLDOCS)

test-all: PROJECTNAME = GProject

test-all: list-versions verify show-project
# ................................................................
