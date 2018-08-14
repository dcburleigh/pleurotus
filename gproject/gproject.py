"""
Class to manage a project with related git repos

Usage:
   edit projects.tsv

import gproject

 gp = GProject(name = 'NAME', repo = '/data/git/name', wiki_page='')

"""

import os.path
import re
import csv

from common import logger
log = logger.get_mod_logger( __name__ )
#import subprocess
from .repo import Repo

class GProject:
    """ represent a project
    built from one or more git repos.

    :name: Name
    :code: abbreviationg
    :prefix:  each commit for a release should be of the form <prefix><version>
    :build_path:  local directory where code is deployed
    :rel_path: path from primary repo to directory containing the release file
    :release: current version of the release in development
    :last_release: version of the previous (stable, master) release
    :next_tag: tag for the commit(s) when the current version is released
    :repo_list - list of repo objects  in this project

    """

    #wiki_url = None
    #archive_root = None

    def __init__(self, name, code=None, repo=None, wiki=None):
        self.verbose = False
        self.verbose = True

        self.name = name

        # primary repo
        self.repo_dir = ''
        # related
        self.repo_list = []
        self.project_tags = {}

        self.release = None
        self.rel_path = None
        self.release_file = None

        self.wiki_url = ''
        self.wiki_page = ''
        self.wiki_page_url = ''

        self.prefix = None
        self.build_dir = None
        self.build_target = None  # target in makefile; not used?

        self.relnotes_page = None
        self.relnotes_url = None
        self.last_tag = None
        self.next_tag = None

        if code:
            self.code = code
            self.prefix = code

        if repo:
            self.repo_dir = repo

        if wiki:
            self.wiki_url = wiki


    def set_wiki_pages(self, page_name=None, wiki_url=None ):
        """
         set the URL for the Wiki pages for the project,
        and latest release notes;
        Not all projects have a wiki page
        """

        if wiki_url:
            self.wiki_url = wiki_url

        if page_name:
            if page_name == '-' or page_name == '_':
                self.wiki_page = self.name
            else:
                self.wiki_page = page_name

        if not self.wiki_page:
            log.debug("no wiki page name")
            return

        self.wiki_page_url  = self.wiki_url + '/' + self.wiki_page

        if not self.release:
            log.error(self.name + " - release not defined")
            return

        # renotes_option
        # 1)
        self.relnotes_page = self.wiki_page + '/Release/' + self.release
        # 2)
        self.relnotes_page = self.wiki_page + '/ReleaseNotes/' + self.release

        if not self.wiki_url:
            log.error("{} - no wiki url".format(self.name))
            return
        self.relnotes_url =  self.wiki_url + '/' + self.relnotes_page

    def set_primary_repo(self, repo=None, name=None):
        if repo:
            self.repo_dir = repo

        log.debug("add primary name={}".format(name))
        r = Repo(self.repo_dir, self.prefix,name=name)
        r.is_primary = True

        self.repo_list.append(r)

        self.set_release_file();
        self.read_release()

    def add_repo(self, repo,name=None, tracking=False ):
        if not os.path.exists(repo):
            log.error('no such repo {}'.format(repo) )
            return

        r = Repo(repo, self.prefix,name=name)
        if tracking:
            r.tracking = True
        self.repo_list.append(r)

    def set_release_file(self):
        """ find the releast file for this project;
        read it if it exists
        """

        if not self.repo_dir:
            log.error("{} - no repo directory defined".foramt(self.name))
            return

        f =  self.repo_dir
        if not os.path.exists(f):
            logger.info("no such directory '{}' ".format( f ) )
            return

        if self.rel_path:
            f = os.path.join(f, self.rel_path)

        if not os.path.exists(f):
            logger.error("no such directory '{}' ".format( f ) )
            return

        f = os.path.join(f, 'release.txt')
        if not os.path.exists(f):
            log.debug("no such file: {}".format( f))
            return

        self.release_file = f

    def read_release(self):
        """ read the release file and set the release version """

        if self.release_file:
            with open(self.release_file, 'r') as rfh:
                v = rfh.read()

            v  = re.sub('\s+$', '', v)  # trim
            v = float(v)
        else:
            log.debug("No release file, using default")
            # TODO:
            #  create default release file ??
            #v = '0.1'
            v = 0.1 # DEFAULT

        self.set_release_version(v)

    def set_release_version(self, v):
        """ set the value of curernt release version

        v is a decimal (float) of the form
           <major>.<minor>

        previous version 0.1 less ?

        is version 1.1 == 1.10? or is 1.10 9 revs greater?

        current project is assumed in the develop branch
        """

        # convert to string
        self.release = str(v)

        # previous release (assumed: in master)
        #last_vf = v - 0.1000
        #last_vf = vf - 0.05
        # handle imprecise floating point math,
        #  assume minor version
        last_vf = round(v - 0.1000, 2)
        self.last_release = str(last_vf)

        log.debug("name={} v={}  last={} last={}".format(self.name, v, last_vf, self.last_release) )

        if not self.prefix:
            log.error("no prefix defined, can't set tags")
            return
        # next == next production version
        #  == current development version
        self.next_tag = self.prefix + self.release
        #self.last_tag = "%s%s" % ( self.prefix, self.last_release)
        self.last_tag = self.prefix + self.last_release

    def show(self, since=None, format='all'):
        """ display most details about this project """

        print ( "Project: {} [ {} ]  [tag: {}] ".format( self.name, self.code, self.prefix))
        #print ( "tag prefix: %s " % ( self.prefix))

        print ("    Current release: {}".format( self.current_release() ))
        if format == 'brief':
            return

        if self.next_tag:
            t = self.next_tag
        else:
            t = '???'
        print ( "    beta: {} ".format( t ))

        if self.last_tag:
            t = self.last_tag
        else:
            t = '???'
        print ( "    Last release: {} ".format( t ))
        print( "\n")

        if since:
            self.repo_log(since)

        print ("Git repos(s)")
        nr = 0
        for r in self.repo_list:
            nr += 1
            st = '.'
            if r.is_primary:
                st = 'P'
            elif r.tracking:
                st = 'T'
            print( "{:1s} {:<12s}: {} ".format(st, r.name, r.dir))
            r.list_commits()

        if nr == 0:
            print("    -NONE- ")


        if self.wiki_page_url:
            wp = self.wiki_page_url
        else:
            wp ='n/a'

        if self.relnotes_url:
            rp = self.relnotes_url
        else:
            rp = 'n/a'

        print ( "Wiki page: {} \n    release notes: {}".format( wp, rp ))

    def current_release(self):
        """ return the release version """

        if self.release:
            return self.release
        else:
            return '???'

    def set_archive_dir(self, dir):
        if not os.path.exists(dir):
            log.error("no such directory '{}' ".format(dir))
            return

        for part in [ self.code, self.release]:
            dir = os.path.join(dir, part)
            if not os.path.exists(dir):
                os.mkdir( dir )

        self.archive_dir = dir

    def archive_release(self):
        """ save all commit logs for this release """

        #print("save to " + self.archive_dir)
        #return
        self.repo_log('release', 'files')

        for r in self.repo_list:
            u = r.get_status()
            if u:
                log.warn("{} uncommitted files in '{}' \n{} ".format( len(u), r.dir, u))

            f = os.path.join( self.archive_dir,  r.name + '.txt')
            if os.path.exists(f):
                log.debug("over-writing '{}'".format(f) )

            try:
                with open(f, 'w') as lfh:
                    lfh.write( "\n".join(r.commits) )
                    log.info("wrote: {}".format(f))
            except Exception as err:
                log.error("open {} failed: {}".format(f, str(err)))

        # filter_commits()

        f = os.path.join( self.archive_dir,  'mantis' + '.txt')
        fh = open(f, 'w')
        if not fh:
            raise Exception("cannot open " + f)

        filter = re.compile('.*mantis\s*(\d+)', re.I)
        issues = {}
        for r in self.repo_list:
            fh.write("{} \n".format( r.name) )
            log.info("{}: {} commits".format( r.name,  len(r.commits)) )
            for c in r.commits:
                m = filter.match(c)
                if not m:
                    #print("no match " + c)
                    continue

                #print("match: ", m.group(1))
                if not m.group(1) in issues:
                    issues[ m.group(1) ] = []
                issues[m.group(1) ].append( r.name + '; ' + c)
                #fh.write("  " + c + " \n")

        for m in sorted(issues):
            fh.write("  {}\n".format( m ))
            for c in issues[m]:
                fh.write("     " + c + "\n")
        log.info("wrote: {}".format( f ))


    def repo_log(self, since=None, format=None):
        """ get commits logs since ...

        :since; [ master | push | release ]
        :format: ?
        """

        args = '';
        if since == 'master':
            args = ' master.. '
        elif since == 'push':
            # should be 'origin/' + r.current_branch + '.. '
            #args += ' origin/master.. '
            args += ' origin/develop.. '
        elif since == 'release':
            # TODO: verify each repo has tag

            if self.last_tag:
                args = ' ' + self.last_tag + '.. '
            else:
                args = ' master.. '

        for r in self.repo_list:
            if since == 'release':
                r.get_tags()
                t = self.last_tag
                if len(r.tags) == 0:
                    log.debug("no tags")
                    #if self.verbose:
                    #    print("no tags")
                    t = 'master'
                    # if r.current_branch == 'master'
                    #t = 'all'
                else:
                    #print(r.tags)
                    tlist = sorted(r.tags.keys())
                    #print(tlist)
                    if not self.last_tag in tlist:

                        t = tlist[-1]  # use current tag ?
                        #t = 'all'  # all commits to date ( )
                        log.debug( "tag {}not found in repo {}, using {} ".format( self.last_tag, r.name, t))

                        #if self.verbose:
                        #    print( "tag {}not found in repo {}, using {} ".format( self.last_tag, r.name, t))

                args = ' ' + t + '.. '
                if t == 'all':
                    args = ' '
                log.debug("since: {}  arg={}".format(self.last_tag,  args) )
                #if self.verbose:
                #    print("since: ", self.last_tag, " args:", args)

            r.get_log(args, format)


    def repo_status(self):
        """ get the current status of each repo """

        for r in self.repo_list:
            r.get_status()


    def verify_release(self):
        errors = []
        for r in self.repo_list:
            ufiles = r.get_status()
            # cutoff ( primary /not primary)
            if len(ufiles) > 0:
                #errors.append( str(len(ufiles)) + " uncommitted files in repo " + r.name)
                errors.append( "{} uncommitted files in repo ".format( len(ufiles), r.name) )

        self.repo_log(since='push')
        for r in self.repo_list:
            # cutoff ( primary /not primary)
            if len(r.commits) > 0:
                #errors.append( str(len(r.commits)) + " commits not pushed to remote in repo " + r.name)
                errors.append( "{} commits not pushed to remote in repo {} \n commits: {}".format(len(r.commits), r.name, r.commits)  )

        self.lookup_tags()
        for r in self.repo_list:
            #print("tags " + "\n". join(r.tags.keys() ))
            if self.next_tag in r.tags.keys() :
                errors.append( '{} is already tagged '.format( r.name))

            if not self.last_tag in r.tags.keys():
                #errors.append('%s is missing last tag, %s ' % ( r.name, self.last_tag) )
                log.info('{} is missing last tag, {}'.format( r.name, self.last_tag) )

        if errors:
            #print( "....not ready: " + "\n".join(errors))
            #log.info( "info not ready: " + "\n".join(errors))
            log.warn( "not ready: " + "\n".join(errors))
            return

        return 1

    def lookup_tags(self, all=False):
        """ populate  the list of tagged commits for each repo in this project
        by default, get the release tags (containing the tag prefix )

        :all boolean if True, get any tag for the repos
        """

        self.tags = {}
        for r in self.repo_list:
            r.get_tags()
            #print("%s tags in %s " % ( len(r.tags), r.dir) )
            for t in r.tags:
                d = r.tags[t]
                if not t in self.tags:
                    ###print("add tag: ", t)
                    self.tags[t] = []
                self.tags[t].append( r.dir + "; " + d)

        self.taglist = sorted( self.tags.keys(), reverse=True)
