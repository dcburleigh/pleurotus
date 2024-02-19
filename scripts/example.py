
import sys
#import re

#from gproject.gproject import GProject 
from gproject.projects import ProjectList 

def ex3():
    manifest = 'dummy.yml'
    project_name = 'Discdungeon'
    plist = ProjectList(manifest, select_project=project_name)

    print(f"instance vars: {plist.__dict__}")  

def ex2():
    manifest = 'projects.yml' 
    project_name = 'DiscDungeon'
    plist = ProjectList(manifest, select_project=project_name)
    plist.read()

    print(f"instance vars: {plist.__dict__}")  

def ex1():
    #plist = ProjectList(repo=repo_root, wiki=wiki_url)

    manifest = 'projects.yml'
    plist = ProjectList(manifest)
    plist.read()
    print ( "%d projects " % ( plist.num() ))
    plist.list() 
    
def main():
#    ex1() 
    ex2()
#    ex3()


if __name__ == '__main__':
    status = main()
    sys.exit(status)