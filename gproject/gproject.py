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
    
    """ 

    #wiki_url = None
    #archive_root = None 
    
    def __init__(self, name, code=None, repo=None, wiki=None):
        self.verbose = False 
        
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
        Not all projects has wiki pages 
        """
        
        if wiki_url:
            self.wiki_url = wiki_url 
        
        if page_name: 
            if page_name == '-':
                self.wiki_page = self.name 
            else:
                self.wiki_page = page_name 
      
        if not self.wiki_page:
            print "no page name"
            return
        
        self.wiki_page_url  = self.wiki_url + '/' + self.wiki_page
        
        if not self.release: 
            print "release not defined"
            return
        
        self.relnotes_page = self.wiki_page + '/Release/' + self.release
        if not self.wiki_url:
            print "ERROR no wiki url"
            return
        self.relnotes_url =  self.wiki_url + '/' + self.relnotes_page

    def set_primary_repo(self, repo=None):
        if repo:
            self.repo_dir = repo 
        
        r = Repo(self.repo_dir, self.prefix) 
        self.repo_list.append(r) 
            
        self.set_release_file();
        self.read_release()
    
    def add_repo(self, repo):
        if not os.path.exists(repo):
            print('ERROR no such repo ' + repo )
            return 
        
        r = Repo(repo, self.prefix) 
        self.repo_list.append(r) 
        
    def set_release_file(self):
        """ find the releast file for this project;
        read it if it exists
        """ 
        
        if not self.repo_dir:
            print "no repo"
            return
    
        f =  self.repo_dir
        if not os.path.exists(f):
            print ("no such directory '%s' " % ( f ) )
            return
        
        if self.rel_path:
            f = os.path.join(f, self.rel_path)

        if not os.path.exists(f):
            print ("no such directory '%s' " % ( f ) )
            return
        
        f = os.path.join(f, 'release.txt')
        if not os.path.exists(f):
            if self.verbose:
                print ("no such file: %s" % ( f))
            return
        
        self.release_file = f 
        
    def read_release(self):
        """ read the release file and set the release version """ 

        if not self.release_file:
            return 
        
        rfh = open(self.release_file, 'r')
        v = rfh.read()
        rfh.close()
        v  = re.sub('\s+$', '', v)  # trim
        self.set_release_version(v) 
        
    def set_release_version(self, v):
        """ set the value of curernt release version
        
        v is a decimal (float)
        
        current project is assumed in the develop branch 
        """
        
        self.release = v
        vf = float(v)
        
        # previous release (assumed: in master) 
        last_vf = vf - 0.1
        self.last_release = str(last_vf)
        #print name, "v=", v, "last=", vf

        if not self.prefix:
            print "no prefix defined, cant' set tags"
            return 
        
        self.next_tag = self.prefix + v
        self.last_tag = "%s%s" % ( self.prefix, last_vf)
        
        
    def show(self):
        """ display most details about this project """
        
        print ( "Project: %s [ %s ] " % ( self.name, self.code))
        print ( "tag prefix: %s " % ( self.prefix))
        
        print ("    Current release: %s"  % ( self.current_release() ))
        if self.next_tag:
            t = self.next_tag 
        else: 
            t = '???'
        print ( "    beta: %s " % ( t ))
        
        if self.repo_dir:
            print ( "Git repo: \n    Primary %s" % ( self.repo_dir) )
        else:
            print ( "No repo defined")
        
        if self.wiki_page_url:
            wp = self.wiki_page_url
        else: 
            wp ='n/a'
        
        if self.relnotes_page: 
            rp = self.relnotes_page
        else: 
            rp = 'n/a' 
        
        print ( "Wiki page: %s \n    release notes: %s " % ( wp, rp ))
    
    def current_release(self):
        """ return the release version """ 
        
        if self.release:
            return self.release
        else:
            return '???'
    
    def set_archive_dir(self, dir):
        if not os.path.exists(dir):
            print "no such directory '%s' " % (dir)
            return 
        d = os.path.join(dir, self.code, self.release)
        if not os.path.exists(d):
            os.mkdir( d ) 
        self.archive_dir = d 
        
    def archive_release(self):
        """ save all commit logs for this release """ 
        
        print "save to " + self.archive_dir 
        #return 
        self.repo_log('release') 

        for r in self.repo_list:
            u = r.get_status() 
            if u:
                print "Warning: %d uncommitted files in %s " % ( len(u), r.dir)
            
            f = os.path.join( self.archive_dir,  r.name)
            if os.path.exists(f):
                print "over-writing '%s'" % f 
           
            lfh = open(f, 'w')
            if not lfh:
                raise Exception("cannot open " + f)
            lfh.write( "\n".join(r.commits) )
            print "wrote: ",f 
            lfh.close()
       
        
    def repo_log(self, since=None):
        """ get commits logs since ... """ 
        
        args = '';        
        if since == 'master':
            args = ' master.. '
        elif since == 'push': 
            args += ' origin/develop.. '
        elif since == 'release':
            # TODO: verify each repo has tag
            print "since: ", self.last_tag 
            if self.last_tag:
                args = ' ' + self.last_tag + '.. '
            else:
                args = ' master.. '
        
        
        for r in self.repo_list: 
            r.get_log(args) 
            
        
    def repo_status(self):
        """ get the current status of each repo """ 
        
        for r in self.repo_list: 
            r.get_status()
        
    
    def verify_release(self):
        errors = []
        for r in self.repo_list:
            ufiles = r.get_status()
            if len(ufiles) > 0:
                errors.append( str(len(ufiles)) + " uncommitted files in repo " + r.name)
                print "\n".join(ufiles)
                for f in ufiles:
                    print("file: '%s'"  % (f) )
        
        if errors: 
            print  "ERROR: " + "\n".join(errors) 
            #return 
        
        self.repo_log(since='puths')
        for r in self.repo_list: 
            if len(r.commits) > 0:
                errors.append( str(len(r.commits)) + " commits not pushed to remote in repo " + r.name)
                
        if errors: 
            print  "ERROR: " + "\n".join(errors) 
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
            for d in r.tags:
                t = r.tags[d]
                if not t in self.tags: 
                    self.tags[t] = []
                self.tags[t].append( r.dir + "; " + d) 
            
                    