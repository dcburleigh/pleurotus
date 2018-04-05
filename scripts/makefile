
REPOROOT =
ETC =

-include makefile.conf


# ................................................................

GPSOURCE = $(REPOROOT)/pleurotus

gproject:
	mkdir -p  $@

# configuration files
MF = projects.yml
CONFIG = projects.tsv gp_init.py
CONFIG = projects.yml gp_init.py

# main script
GPSCRIPTS = gp.py makefile  example.py projects.example.yml

$(GPSCRIPTS): %: $(GPSOURCE)/scripts/%
	cp $< $@

update-gp:
	rsync -av $(GPSOURCE)/gproject/ gproject/

install-gp: gproject  update-gp $(GPSCRIPTS) $(MF)

# ................................................................

list-versions: install-gp
	python gp.py --list -v  --manifest $(MF)

ifneq ($(PROJECTNAME),)

show-project: install-gp
	python gp.py -p $(PROJECTNAME) -i  --manifest $(MF)

show-status: install-gp
	python gp.py -p $(PROJECTNAME) -s  --manifest $(MF)

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
	python gp.py -p $(P) --verify  release

archive-release: install-gp
	python gp.py -p $(P) -a   --manifest $(MF)

tag-release: install-gp
	python gp.py -p $(P) --tag-release  --manifest $(MF)

endif

gp-doc: update-gp
	pydoc gp
	pydoc gproject
	pydoc gproject.gproject
	pydoc gproject.repo


# ................................................................
