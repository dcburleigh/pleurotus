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

from ruamel.yaml import YAML
#import logging
#from .logger import custom_logger
from common import logger
log = logger.get_mod_logger( __name__ )

from .gproject import GProject
from .repo import Repo

class ProjectList:
    pfile = 'projects.tsv'
    projects = {}
    repo_root = None
    wiki_url = None
    build_root = None
    archive_root = None

    def __init__(self, f=None, repo=None, wiki=None, select_project=None):

        log.debug('list: init')
        if repo:
            self.repo_root = repo
        if wiki:
            self.wiki_url = wiki

        if select_project:
            self.select_project = select_project
        else:
            self.select_project = None

        self.read(f)


    def read(self, f=None):
        if not f:
            return

        if not os.path.exists(f):
            log.error("no such file {}".format(f))
            return

        m = re.match('.+\.([a-z]+)$', f);
        if not m:
            log.error("no valid extension {}".format(f))
            return

        ext = m.group(1)
        if ext == 'tsv':
            self.pfile = f
            self.read_tsv()
        elif ext == 'yml':
            self.pfile = f
            self.read_yaml()
        else:
            log.error("invalid extension '{}' ".format(ext) )
        return

    def read_yaml(self,f=None, project_name=None):
        """ read the master list in YAML format
        if project_name is specified
        , only populate the list for that project """

        if self.select_project:
            project_name = self.select_project

        n = 0
        yaml=YAML(typ='safe')   # default, if not specfied, is 'rt' (round-trip)
        with open(self.pfile) as fh:
            text = fh.read()

        cfg = yaml.load(text)
        #log.debug("config={}".format(cfg) )
        if 'repo_root' in cfg:
            self.repo_root = cfg['repo_root']
        else:
            log.error("No repo root defined")

        if 'wiki_root' in cfg:
            self.wiki_url = cfg['wiki_root']

        if 'archive_root' in cfg:
            self.archive_root = cfg['archive_root']

        if 'build_root' in cfg:
            self.build_root = cfg['build_root']

        self.repo_projects = {}
        for p in cfg['projects']:
            if not 'name' in p or not p['name']:
                log.error("no name in project {} ".format(p))
                continue

            if project_name != None and project_name != p['name']:
                # filter on project name
                continue

            if  'code' in p:
                code   = p['code']
            else:
                log.debug("default code")
                code = p['name'].lower()

            gp = GProject(p['name'], code, wiki=self.wiki_url )
            if 'prefix' in p and p['prefix']:
                gp.prefix = p['prefix']

            if not 'repos' in p:
                log.error( p['name'] + " no repos")
                continue

            for r in p['repos']:
                log.debug("{} add repo={}".format(code,r['name']))
                if 'name' in r:
                    dir = os.path.join(self.repo_root, r['name'])
                else:
                    raise Exception("no repo name")

                if not r['name'] in self.repo_projects:
                    self.repo_projects[ r['name']] = []
                self.repo_projects[ r['name']].append(gp.name)


                if 'release_path' in r:
                    gp.rel_path = r['release_path']

                tr = False
                if 'tracking' in r:
                    if r['tracking']:
                        tr = True
                log.debug("details={}".format(r))
                if 'primary' in r:
                    gp.set_primary_repo(dir, r['name'])
                else:
                    gp.add_repo(dir, tracking=tr)



            if 'wikipage' in p:
                gp.set_wiki_pages( p['wikipage'])

            self.projects[ gp.name] = gp


    def read_tsv(self,f=None):
        """ read the master list of Git Projects in TSV format"""
        if f:
            self.pfile = f

        n = 0
        cols = {}
        with open(self.pfile, 'rb') as csvfile:
            freader  = csv.reader(csvfile, delimiter="\t", quotechar='|')
            for row in freader:
                if len(row) == 0:
                    continue

                n += 1
                if n == 1:
                    cols = row
                    log.debug("header".format(cols) )
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
                    build_dir = row[3]
                else:
                    # default to code
                    build_dir = row[1]

                # 4) prefix
                if len(row) >= 5 and row[4]:
                    gp.prefix = row[4]

                if n >= 3:
                    #break
                    pass
                # 7) rel
                if len(row) >= 8 and row[7]:
                    gp.rel_path  = row[7]

                gp.set_primary_repo()

                gp.set_release_file();
                gp.read_release();
                if gp.release_file:

                    pass

                if  len(row) >= 6 and row[5]:
                    gp.set_wiki_pages( row[5] )

                self.projects[name] = gp

                # remaining items in row
                # results = [gp.add_repo(os.path.join( self.repo_root, row[k] ) for k in range(8, len(row) if row[k]) ]
                for k in range(8,len(row)):
                    #print("related:", row[k])
                    if not row[k]:
                        continue
                    repo = os.path.join( self.repo_root, row[k])
                    gp.add_repo(repo )

    def get_project(self, name=None):
        """ return the specified GProject object """
        if not name:
            if not self.select_project:
                log.error("no default project name specified")
                return
            name = self.select_project

        if name in self.projects:
            return self.projects[name]

        log.debug( "project {} not found in {} projects ".format(name, len(self.projects)) )
        return None

    def num(self):
        return len(self.projects)

    def list(self):
        """ display all the GProject objects """

        for name in self.projects:
            self.projects[name].show()
            print("\n")

    def init_repo(self, repo_name):
        repo_dir = os.path.join(self.repo_root, repo_name)
        r = Repo(repo_dir, name=repo_name)
        return r
