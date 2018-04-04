
REPOROOT = 
ETC = 

-include makefile.conf 


# ................................................................

GPSOURCE = $(REPOROOT)/pleurotus

gproject: 
	mkdir -p  $@ 

# configuration files 
CONFIG = projects.tsv gp_init.py 

# main script 
GPSCRIPTS = gp.py makefile gp_init.example.py   example.py 

$(GPSCRIPTS): %: $(GPSOURCE)/scripts/%
	cp $< $@ 

update-gp: 
	rsync -av $(GPSOURCE)/gproject/ gproject/

install-gp: gproject  update-gp $(GPSCRIPTS) $(CONFIG) 

# ................................................................
list-versions: install-gp
	python gp.py --list -v 


gp-doc: update-gp 
	pydoc gp 
	pydoc gproject
	pydoc gproject.gproject
	pydoc gproject.repo 


# ................................................................