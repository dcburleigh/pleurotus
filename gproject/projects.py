"""

ProjectList

Class to manage my git-relatd projects

Usage:
   edit projects.tsv

from gproject.projects import ProjectList

plist = ProjectList( )

plist.read()

plist.list()

"""


import os.path
import re
import csv
import subprocess
from .gproject import GProject
from .repo import Repo

class ProjectList:
    pfile = 'projects.tsv'
    projects = {}
    repo_root = None
    wiki_url = None
    build_root = None

    def __init__(self, f=None, repo=None, wiki=None):

        if repo:
            self.repo_root = repo
        if wiki:
            self.wiki_url = wiki

        if f:
            self.pfile = f
            self.read()

    def read(self,f=None):
        """ read the master list of Git Projects"""
        if f:
            self.pfile = f

        if not self.pfile:
            print "pfile not defined"
            return

        if not os.path.exists(self.pfile):
            print "no such file ", self.pfile
            return

        n = 0
        cols = {}
        #print ("read: " + self.pfile)
        with open(self.pfile, 'rb') as csvfile:
            freader  = csv.reader(csvfile, delimiter="\t", quotechar='|')
            for row in freader:
                if len(row) == 0:
                    print "skip"
                    continue

                n += 1

                #print "row,", n
                if n == 1:
                    cols = row
                    #print "header", cols
                    continue

                # 0)
                name = row[0]

                # 1) code
                #self.projects[ name]['code'] = row[1]

                # 2)
                if row[2]:
                    rp = row[2]
                else:
                    rp = row[1]

                if self.repo_root:
                    repo = os.path.join( self.repo_root, rp)
                else:
                    repo = None

                gp = GProject(name, row[1], wiki=self.wiki_url, repo=repo)

                if row[1]:
                    gp.code = row[1]

                # 3) build dir
                if len(row) >= 4 and row[3]:
                    ###print "set b", row[3]
                    #self.projects[name]['build_path'] = row[3]
                    build_dir = row[3]
                else:
                    # default to code
                    build_dir = row[1]

                # 4) prefix
                if len(row) >= 5 and row[4]:
                    gp.prefix = row[4]

                #gp.show()

                # 5) wiki
                #print("w:" + row[5] )


                if n >= 3:
                    #break
                    pass

                # 6) target (NOT USED)

                # 7) rel
                if len(row) >= 8 and row[7]:
                    gp.rel_path  = row[7]

                gp.set_primary_repo()

                gp.set_release_file();
                gp.read_release();
                if gp.release_file:
                    #print( "file: " + gp.release_file )
                    pass

                if  len(row) >= 6 and row[5]:
                    gp.set_wiki_pages( row[5] )

                self.projects[name] = gp

                for k in range(8,len(row)):
                    #print "related:", row[k]
                    if not row[k]:
                        continue
                    repo = os.path.join( self.repo_root, row[k])
                    gp.add_repo(repo )

    def get_project(self, name):
        """ return the specified GProject object """
        if name in self.projects:
            return self.projects[name]

        print( "%d project " % (len(self.projects)) )

        return None

    def num(self):
        return len(self.projects)

    def list(self):
        """ display all the GProject objects """

        for name in self.projects:
            #print "Project: ", name
            self.projects[name].show()
            print("\n")

    def init_repo(self, repo_name):
        repo_dir = os.path.join(self.repo_root, repo_name)
        r = Repo(repo_dir, name=repo_name)
        return r
