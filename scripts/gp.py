#!/usr/bin/env python

"""

gp.py - display and save the commit log(s) for a product release

Usage:

All projects

gp.py  [ --list | -v ]

   list all projects

Archive Project

gp.py -p <Project Name> -a  <archive options>

    save information (commit logs) about a project to the release log archive
    Archive options
    ?

Project information

gp.py -p <Project Name > <project options>

    show information about a project

    Project Options

-t   all tags

-i   display all information,
        implies -t, s

Repo Information

gp.py -d <Repo Name>   <repo options >

    show information about all projects related to this repo

    Repo Options



Display Options


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

#from gp_init import repo_root, archive_root, wiki_url

plist = None
gp = None

def show_log(project_name, since=None, summary=True ):
    global plist

    #plist.read()

    gp = plist.get_project();
    if not gp:
        print "no such project"
        return

    gp.repo_log(since)

    for r in gp.repo_list:
        print("%s " % r.name )

        r.list_commits('all')


# TODO:
#  merge_dev_prod
#  check_dev
#  increment_release
#

def tag_release(project_name):
    global plist

    plist.read()

    gp = plist.get_project(project_name);
    if not gp:
        print "no such project"
        return

    # TODO: primary-only
    rv = gp.verify_release()
    if not rv:
        print "not ready"
        return

    print( "Release '%s' is ready" % ( gp.next_tag))
    print "OK!"

    for r in gp.repo_list:
        print( '%s: tag %s' % (r.name, gp.next_tag))
        r.add_tag( gp.next_tag )


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

    print( "Release '%s' is ready" % ( gp.next_tag))
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
        print "    " + "\n    ".join(ufiles)


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
    #plist.read()
    if name in plist.projects:
        gp = plist.projects[name]
    else:
        print( "ERROR: no such project: %s " % ( name ))
        return

    gp.show('release')

def show_repo(repo_name):
    global plist
    r = plist.init_repo(repo_name)

    print("Repo: %s"  % ( r.name) )
    out = r.get_commit('deldevdb2.0');
    print out


def archive_release():
    global plist

    gp = plist.get_project()

    gp.show()

    gp.set_archive_dir( plist.archive_root )
    #print( "root=%s  dir=%s" % ( archive_root,  gp.archive_dir) )
    #return
    gp.archive_release()


def verify_repo(repo_name):
    """ verify that this repo can be merged to production
    :repo_name:  name of a secondary repo
    """
    global plist
    plist.read()

    max_repo_commits = 10
    max_repo_ufiles = 2
    ###r = repo( repo_name);

    waiting_on_projects = []
    np = 0;
    for name in plist.projects:
        gp = plist.projects[name]
        has_repo = False
        for r in gp.repo_list:
            if r.dir == repo_name or r.name == repo_name:
                has_repo = True
                break
        if not has_repo:
            #print("%s - does not contain %s" % ( gp.name, repo_name))
            continue

        # TODO:
        #  gp.verify_repo( r )
        np +=1
        gp.show(format='brief')
        ###print("found r=%s" % ( r.name ))
        if r.name == gp.repo_list[0].name:
            print "ERROR: is primary repo"
            continue

        ready = True
        rp = gp.repo_list[0]
        print("    primary: " + rp.name)
        ufiles = rp.get_status()
        if ufiles:
            #ready = False
            print "Warning: %d uncommitted files in primary: %s " % ( len(ufiles), rp.name )
            if len(ufiles) > max_repo_ufiles:
                ready = False

        r.get_log( gp.last_tag + '..')
        if r.commits:
            #ready = False
            print("Warning: %d commits in repo since last release (%s)" % ( len(r.commits),  gp.last_tag))
            out = r.get_commit( gp.last_tag)
            print("    %s" % (out) )
            if len(r.commits) > max_repo_commits:
                ready = False

        if not ready:
            # TODO: allow user to review
            waiting_on_projects.append( gp.name )
        else:
            print "OK! "
        print "\n"

    if waiting_on_projects:
        print "waiting on projects: " + ", ".join(waiting_on_projects)




def show_repo_projects( repo_name):
    global plist
    plist.read()

    repo_projects = []
    for name in plist.projects:
        gp = plist.projects[name]
        for r in gp.repo_list:
            if r.dir != repo_name and r.name != repo_name:
                continue

            r.tag_prefix = gp.prefix
            r.get_tags()
            is_tagged = ' '
            if gp.last_tag:
                print("t=%s" % (gp.last_tag) )
                if gp.last_tag in r.tags.values():
                    is_tagged = '*'

            print( "%-15s: current release:%s %s" % ( name, is_tagged, gp.release ))
            print( "    tags: %s " % ", ".join( r.tags.values() ))

            repo_projects.append(r)

    print( "%d projects contain %s" % ( len(repo_projects), repo_name ))


def list_all(format='full'):
    global plist

    #plist.read()
    if not plist.num():
        print "No projects defined"
        return

    if format == 'full':
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
    manifest = None
    project_name = None

    try:
        opts,args = getopt.getopt(sys.argv[1:], 'fip:tlsvar:', ['manifest=', 'tag-release', 'verify=', 'test', 'list', 'since=', 'last', 'depends='])
    except getopt.GetoptError as err:
        raise Exception("invalid arguments " + str(err) )

    for o,a in opts:
        if o == '-p':
            project_name = a
        elif o == '-r':
            repo_name = a
        elif o == '--manifest':
            manifest = a

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
            if a == 'release':
                action = 'verify'
            elif a == 'repo':
                action = 'verify-repo'
            else:
                raise Exception("invalid verify option " + a )
        elif o =='--tag-release':
            action = 'tag-release'

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

    #plist = ProjectList( repo=repo_root, wiki=wiki_url)

    #print("TEsTING m=" + manifest + " archive=" + plist.archive_root )
    #return
    plist = ProjectList(manifest, select_project=project_name)

    if action == 'list_projects':
        #plist = ProjectList(manifest)
        list_all()
    elif action == 'list_versions':
        #plist = ProjectList(manifest)
        list_all('versions')

    elif action == 'repo_depends':
        #plist = ProjectList(manifest)
        show_repo_projects( repo_name )
    elif action == 'verify-repo':
        verify_repo(repo_name)
    elif repo_name:
        show_repo(repo_name)

    elif action == 'show_info':
        show_project(project_name);
    elif action == 'show_tags':
        show_tags(project_name);
    elif action == 'show_status':
        show_status(project_name);
    elif action == 'show_log':
        show_log(project_name, since=since);
    elif action == 'archive':
        archive_release( );
    elif action == 'verify':
        verify_release(project_name)
    elif action == 'tag-release':
        tag_release(project_name)
    else:
        print("ERROR: invalid action: %s" % ( action ) )

    #test1()
    #test2()
    #test4()
    #test3()

if __name__ == '__main__':
    status = main()
    sys.exit(status)
