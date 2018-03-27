
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

update-gp: gproject  
	rsync -av $(REPOROOT)/deldev-build/gproject/ gproject/

install-gp: update-gp $(GPSCRIPTS) $(CONFIG) 

gp-doc: update-gp 
	pydoc gp 
	pydoc gproject
	pydoc gproject.gproject
	pydoc gproject.repo 


# ................................................................