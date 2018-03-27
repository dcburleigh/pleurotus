
import sys
import re

from gproject.gproject import GProject 
from gproject.projects import ProjectList 

from gp_init import repo_root, archive_root, wiki_url

plist = ProjectList(repo=repo_root, wiki=wiki_url)
plist.read()
print ( "%d projects " % ( plist.num() ))
plist.list() 
    
