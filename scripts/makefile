
REPOROOT =
ETC =

-include makefile.conf


# ................................................................

GPSOURCE = $(REPOROOT)/pleurotus

gproject:
	mkdir -p  $@

# configuration files
CONFIG = projects.tsv gp_init.py
CONFIG = projects.yml gp_init.py

# main script
GPSCRIPTS = gp.py makefile gp_init.example.py   example.py

$(GPSCRIPTS): %: $(GPSOURCE)/scripts/%
	cp $< $@

update-gp:
	rsync -av $(GPSOURCE)/gproject/ gproject/

install-gp: gproject  update-gp $(GPSCRIPTS) $(CONFIG)

# ................................................................

MF = projects.yml
list-versions: install-gp $(MF)
	python gp.py --list -v  --manifest $(MF)

ifneq ($(PROJECTNAME),)

show-project: install-gp $(MF)
	python gp.py -p $(PROJECTNAME) -i  --manifest $(MF)

show-status: install-gp $(MF)
	python gp.py -p $(PROJECTNAME) -s  --manifest $(MF)

show-tags: install-gp $(MF)
	python gp.py -p $(PROJECTNAME) -t  --manifest $(MF)  > t.out
	cat t.out

show-log-m: install-gp $(MF)
	python gp.py -p $(PROJECTNAME) -l --since master  --manifest $(MF)  > t.out
	cat t.out

show-log-rel: install-gp $(MF)
		python gp.py -p $(PROJECTNAME) -l --since release  --manifest $(MF)  > t.out
		cat t.out


endif

gp-doc: update-gp
	pydoc gp
	pydoc gproject
	pydoc gproject.gproject
	pydoc gproject.repo


# ................................................................
