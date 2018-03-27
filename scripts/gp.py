#!/usr/bin/env python

"""

gp.py - display and save the commit log(s) for a product release

Usage:

gp.py  [ --list | -v ]

   list all projects


gp.py -p <Project Name > <project options>

    show information about a project

Project Options

-a    save information (commit logs) about a project to the release log archive

-t   all tags


gp.py -d <Repo Name>   <repo options >

    show information about all projects related to this repo

Repo Options



Display Options

-i   display all information,
        implies -t, s

-s   project status

Output options

-a  save commit logs to central archive

Log Range Options

--since master   changes since master

--since release   changes in this release, since the last release

--since <date> - logs since given date




"""

#
# global
#

import sys
import re
import getopt

from gproject.gproject import GProject 
from gproject.projects import ProjectList 

from gp_init import repo_root, archive_root, wiki_url

plist = None 
gp = None

def show_log(project_name, since=None):
    global plist 
    
    plist.read() 
    
    gp = plist.get_project(project_name);
    if not gp:
        print "no such project"
        return 
    
    gp.repo_log(since) 
    
    for r in gp.repo_list:  
        
        nc = len(r.commits)
        print( "%s: %s commits" % ( r.dir, nc ))
        if nc == 0:
            print "    None "
        elif nc == 1: 
            print( "    %s " % ( r.commits[0]))
        else:     
            print( "    %s\n    %s " % ( r.commits[0], r.commits[-1]))


def verify_release(project_name):
    global plist 
    
    plist.read() 
    
    gp = plist.get_project(project_name);
    if not gp:
        print "no such project"
        return 
    rv = gp.verify_release()
    if not rv:
        print "not ready"
        return 
    
    print "OK!"
    
  
def show_status(project_name ):
    global plist 
    
    plist.read() 
    
    gp = plist.get_project(project_name);
    if not gp:
        print "no such project"
        return 
    
    for r in gp.repo_list:  
        ufiles = r.get_status() 
        print( "%s: %s files " % ( r.dir, len(ufiles) ))


def show_tags(project_name ):
    global plist 
    
    plist.read() 
    print ( "%d projects " % ( plist.num() ))
    gp = plist.get_project(project_name);
    if not gp:
        print "no such project"
        return 
    
    print( "current tag: %s " % ( gp.next_tag  ) )
    print( "   last tag: %s " % ( gp.last_tag  ) )
    
    #gp.project_tags(project_name, True);
    gp.lookup_tags();
    for r in gp.repo_list: 
        print(">Repo: %s  (%s): " %  (r.name, r.dir) ) 
        if len(r.tags) == 0:
            print "    No releases"
            
        for d in sorted(r.tags, reverse=True): 
            if r.tags[d] == gp.last_tag:
                st = '*'
            else:
                st = ' '
            print( "   %s %s) %s" % ( st, d, r.tags[d]) )
           
    
    print "\nTag -> repo"
    for t in gp.tags: 
        print( "%s: \n    %s" % ( t, "\n    ".join(gp.tags[t]) ) )
    
    return 
  
def show_project(name):
    global plist 
    #plist = ProjectList(repo=repo_root, wiki=wiki_url)
    plist.read()
    if name in plist.projects:
        gp = plist.projects[name] 
    else:
        print( "ERROR: no such project: %s " % ( name ))
        return 

    gp.show()
    

def archive_release(name):
    global plist 
    plist.read()
    if name in plist.projects:
        gp = plist.projects[name] 
    else:
        print( "ERROR: no such project: %s " % ( name ))
        return 
    
    gp.set_archive_dir( archive_root ) 
    gp.archive_release()
    

def show_repo_projects( repo_name): 
    global plist 
    plist.read() 
    
    repo_projects = []
    for name in plist.projects:
        gp = plist.projects[name]
        for r in gp.repo_list: 
            if r.dir == repo_name or r.name == repo_name: 
                print( "repo in %s " % ( name ))
                repo_projects.append(r) 
    
    print( "%d projects contain %s" % ( len(repo_projects), repo_name ))
                
    
def list_all(format='full'):
    global plist 
    
    plist.read()
    if format == 'flull':
        plist.list()
    else:
        for name in plist.projects: 
            gp = plist.get_project(name) 
            print("%-20s:  %s " % ( name,  gp.current_release() ))

def main():
    global gp, plist 
    action = None 
    since = None 
    repo_name = None 

    try:
        opts,args = getopt.getopt(sys.argv[1:], 'fip:tlsva:', ['verify', 'test', 'list', 'since=', 'last', 'depends='])
    except getopt.GetoptError as err:
        raise Exception("invalid arguments " + str(err) )

    for o,a in opts:
        if o == '-p':
            project_name = a
        elif o == '-a':
            action = 'archive'
        elif o == '--last':
            archive_last_release = True
        elif o == '--test':
            action = 'test1' 
        elif o == '--depends':
            action = 'repo_depends'
            repo_name = a 
        elif o == '--verify':
            action = 'verify' 
            
        elif o == '-t':
            action = 'show_tags'
        elif o == '-i':
            action = 'show_info'
        elif o == '-l':
            action = 'show_log'
        elif o == '-v':
            action = 'list_versions'
        elif o == '-s':
            action = 'show_status'
        elif o == '--since':
            if a == 'push' or a == 'local':
                since  = 'push'
            elif a == 'master':
                since = a 
            elif a == 'release':
                since = a 
        
            else:
                action = 'logs_since_date'
                since_date = a
        elif o == '--list':
            action = "list_projects"
        elif o == '-f':
            force_update_archive = True
        else:
            print "invalid argument: ", o

  
    plist = ProjectList(repo=repo_root, wiki=wiki_url)
    
    if action == 'list_projects':
        list_all()
    elif action == 'list_versions':
        list_all('versions')
    elif action == 'repo_depends':
        show_repo_projects( repo_name ) 
    elif action == 'show_info': 
        show_project(project_name);
    elif action == 'show_tags': 
       
        show_tags(project_name);
    elif action == 'show_status': 
       
        show_status(project_name);
    elif action == 'show_log': 
       
        show_log(project_name, since=since);
    elif action == 'archive':
        archive_release(project_name );
    elif action == 'verify':
        verify_release(project_name)
    else: 
        print("ERROR: invalid action: %s" % ( action ) )
    
    #test1()
    #test2() 
    #test4() 
    #test3() 

if __name__ == '__main__':
    status = main()
    sys.exit(status)


