
REPOROOT =
ETC = /usr/local/etc/deldev

PYDOC = python -m pydoc

-include makefile.conf

# ................................................................

GPSOURCE = $(REPOROOT)/pleurotus

gproject:
	mkdir -p  $@

# configuration files
MF = projects.yml
CONFIG = projects.tsv gp_init.py
CONFIG = $(MF) gp_init.py
CONFIG = $(MF)

$(CONFIG): %: $(ETC)/%
	cp $< $@

# main script
GPSCRIPTS = gp.py makefile  example.py projects.example.yml

$(GPSCRIPTS): %: $(GPSOURCE)/scripts/%
	cp $< $@

GPFILES = LICENSE requirements.txt

$(GPFILES): %: $(GPSOURCE)/%
	cp $< $@

update-gp:
	rsync -a $(GPSOURCE)/gproject/ gproject/

install-gp: gproject  update-gp $(GPSCRIPTS) $(GPFILES) $(CONFIG)

setup-python: requirements.txt
	pip install -r requirements.txt


# ................................................................

list-versions: install-gp
	python gp.py --list -v  --manifest $(MF)

ifneq ($(PROJECTNAME),)

show-project: install-gp
	python gp.py -p $(PROJECTNAME) -i  --manifest $(MF)

show-status: install-gp
	python gp.py -p $(PROJECTNAME) -s

show-tags: install-gp
	python gp.py -p $(PROJECTNAME) -t  --manifest $(MF)  > t.out
	cat t.out

show-log-m: install-gp
	python gp.py -p $(PROJECTNAME) -l --since master  --manifest $(MF)  > t.out
	cat t.out

show-log-rel: install-gp
		python gp.py -p $(PROJECTNAME) -l --since release  --manifest $(MF)  > t.out
		cat t.out

verify: install-gp
	python gp.py -p $(PROJECTNAME) --verify release --manifest $(MF)

archive-release: install-gp
	python gp.py -p $(PROJECTNAME) -a   --manifest $(MF)

tag-release: install-gp
	python gp.py -p $(PROJECTNAME) --tag-release  --manifest $(MF)

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
