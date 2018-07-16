"""

Class to manage a git repo

Usage:

  from gproject.repo import Repo

  r = Repo(dir)

  ufiles = r.get_status()

  print( "{} uncommitted files in repo {} ".format( len(ufiles), r.dir)

"""

import re
import subprocess

from common import logger
log = logger.get_mod_logger( __name__ )

class Repo:

    log_format = {}
    log_format['oneline']= "  --pretty=format:'%ad %h | %s ' --date=short"
    log_format['files'] = " --name-only --pretty=format:'%ad %h | %s ' --date=short"

    show_format_brief1 =  ' -s  --pretty="format:%ci %d %h %b" '
    show_format_brief2 =  ' -s  --pretty="format:%cD %d %h %b" '
    show_format_brief =  ' -s --date=short  --pretty="format:%cd (%cr) %d %h %b" '

    dir_name_pattern  = re.compile('.*/([^\/]+)$')
    #dir_name_pattern  = re.compile('([a-z\-\_]+)$')
    #dir_name_pattern  = re.compile('.*/([^A-Z]+)$')

    max_commits_primary = 0
    max_commits_associated = 5
    max_ufiles_primary = 0
    max_ufiles_associated = 2

    def __init__(self, dir=None, prefix=None, name=None):

        self.tags = {}
        if dir:
            self.dir = dir

        if prefix:
            self.tag_prefix = prefix

        if name:
            self.name = name
        else:
            #re.match('/([^\/]+)$', dir)
            # get project name from repo directory
            m = self.dir_name_pattern.match(dir)
            if not m:
                log.error("no name in " + dir)
                return
            self.name = m.group(1)

        log.debug("got name: %s" % ( self.name))

        self.is_primary = False
        self.tracking = False
        self.commits = []

    def git_command_rows(self, command):
        out = self.git_command(command)
        if not out:
            return []

        out = re.sub('\s+$', '', out) # trim
        if not out:
            return []
        return out.split("\n")

    def git_command(self, git_args):
        clist =  [ 'cd ' + self.dir + '; git ' + git_args ]

        out = None
        serr = None

        #print("try " + git_args)
        try:
            # to use shell = False,
            #  split into args
            #proc = subprocess.Popen(clist, stdout=subprocess.PIPE, shell=False)
            # assume command is sanitized
            proc = subprocess.Popen(clist, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (out, serr) = proc.communicate()
        except  Exception as err:
            log.error("git command failed: \n{}\n err={} ").format(clist,err)
            return

        if serr:
            log.error("git command error: {}".format(serr) )
            #print("err:", serr)
            self.last_error = serr
            return

        return out.decode() # as string

    def list_commits(self, format='summary'):
        nc = len(self.commits)
        ###print( "%s: %s commits" % ( self.dir, nc ))
        if format == 'summary':
            if nc == 0:
                print("    None ")

            elif nc == 1:
                print( "    {} ".format( self.commits[0]))
            else:
                print("    {} commits ".format( nc) )
                print( "    {}\n    {} ".format( self.commits[0], self.commits[-1]))
            return

        # format = all
        clist = sorted( self.commits, reverse=True);
        for c in clist:
            print("    {}".format( c ) )


    def get_log(self, log_args='', format='oneline'):
        args = ''
        #command = "log "  + log_args + self.log_format_oneline
        if not format in self.log_format:
            format = 'oneline'
        command = "log "  + log_args + self.log_format[format]
        self.commits = self.git_command_rows(command)

    def get_status(self):
        return self.git_command_rows('status --short')

    def describe(self):
        return self.git_command('describe --tags --long ').strip()

    def get_commit(self, commit):
        return self.git_command( 'show ' + commit + ' ' + self.show_format_brief)
        #return self.git_command( 'show ' + commit + ' -s  --pretty="format:%ci {} %h %b" ')

    def taglist(self):
        return sorted(self.tags.keys(), reverse=True)
        #tlist = sorted(self.tags, key=self.tags.get)
        #print("tlist", tlist)
        #return sorted(tlist)

    def get_tags(self, all=False):
        """ get commit tags
        by default, only get tags associated with a given project release,
        identified by the tag_prefix

        :all: boolean - if True, get all tags in this repo

        This method populates the 'tags' attribute,
        a dict of   Tag => CommitDate

        """
        if all:
            #pattern = re.compile('^(.+)\s+\(tag:\s+([^\,\)]+)', re.I)
            pattern = re.compile('.*tag:\s+([^\,\)]+)', re.I)
        else:
            #pattern = re.compile('^(\S+)\s+\(.*tag:\s+(' + self.tag_prefix + '[^\,\)]+)', re.I)
            pattern = re.compile('tag:\s+(' + self.tag_prefix + '[^\,\)]+)', re.I)
            #pattern = re.compile('tag:\s+(' + self.tag_prefix + '[\d\.]+)', re.I)

        # format: date tag
        command =  'log --tags --simplify-by-decoration --date=short --pretty="format:%cd %d" '

        rows = self.git_command_rows(command)
        nx = 0
        for row in rows:
            cdate = row[:10]
            for m in pattern.finditer(row):
                #print("got:", m.groups())
                t = m.group(1)
                self.tags[t] = cdate



    def is_ready(self, log_range):
        """ check that the repo is ready for release
        - no uncommitted files
        - all files pushed to remote
        """

        ok = True
        warnings = ''
        ufiles = self.get_status()
        nu = len(ufiles)
        if nu:
            log.warn("{} uncommitted files in primary: {} ".format( nu, self.name ))

            if self.is_priamry:
                if nu > self.max_ufiles_primary:
                    ok  = False
            else:
                if nu > self.max_ufiles_associated:
                    ok = False
        self.get_log(log_range)
        nr = len(self.commits)
        if nr:
            log.warn("{} commits in repo since last release ({})".format( len(r.commits),  log_range))
            if self.is_primary:
                if nr > max_commits_primary:
                    ok = False
            else:
                if nr > max_commits_associated:
                    ok = False
        return ok

    def add_tag(self, tag, message=None):
        """ tag the current commit in this repo """

        command = 'tag ' + tag
        if message:
            command += ' -m ' + message

        out = self.git_command( command )
        log.debug("got: " + out)
        log.info("result={}".format(out))
