"""

Class to manage a git repo

Usage:

  from gproject.repo import Repo

  r = Repo(dir)

  ufiles = r.get_status()

  print( "%d uncommitted files in repo %s " % ( len(ufiles), r.dir)

"""

import re
import subprocess
from test.warning_tests import outer

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
            m = self.dir_name_pattern.match(dir)
            if not m:
                print "ERROR no name in " + dir
                return
            self.name = m.group(1)
            #print("got name: %s" % ( self.name))

        self.is_primary = False
        self.commits = []

    def git_command_rows(self, command):
        out = self.git_command(command)
        if not out:
            return []
        out = re.sub('\s+$', '', out)
        #print( "'%s'  " % out )
        if not out:
            return []
        return out.split("\n")

    def git_command(self, git_args):
        clist =  [ 'cd ' + self.dir + '; git ' + git_args ]

        out = None
        serr = None

        #print "try " + git_args
        try:
            # to use shell = False,
            #  split into args
            #proc = subprocess.Popen(clist, stdout=subprocess.PIPE, shell=False)
            # assume command is sanitized
            proc = subprocess.Popen(clist, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (out, serr) = proc.communicate()
        except  Exception as err:
            print("ERROR: command failed: \n%s\n err=%s ") % (clist,err)
            return

        if serr:
            #print "err:", serr
            self.last_error = serr
            return

        return out

    def list_commits(self, format='summary'):
        nc = len(self.commits)
        ###print( "%s: %s commits" % ( self.dir, nc ))
        if format == 'summary':
            if nc == 0:
                print "    None "
            elif nc == 1:
                print( "    %s " % ( self.commits[0]))
            else:
                print("    %d commits " % ( nc) )
                print( "    %s\n    %s " % ( self.commits[0], self.commits[-1]))
            return

        # format = all
        clist = sorted( self.commits, reverse=True);
        for c in clist:
            print("    %s" % ( c ) )


    def get_log(self, log_args='', format='oneline'):
        args = ''
        #command = "log "  + log_args + self.log_format_oneline
        if not format in self.log_format:
            format = 'oneline'
        command = "log "  + log_args + self.log_format[format]
        self.commits = self.git_command_rows(command)

    def get_status(self):
        return self.git_command_rows('status --short')

    def get_commit(self, commit):
        return self.git_command( 'show ' + commit + ' ' + self.show_format_brief)
        #return self.git_command( 'show ' + commit + ' -s  --pretty="format:%ci %d %h %b" ')

    def get_tags(self, all=False):
        """ get commit tags
        by default, only get tags associated with a given project release,
        identified by the tag_prefix

        :all: boolean - if True, get all tags in this repo

        This method populates the 'tags' attribute,
        a dict of   CommitDate => Tag

        """
        if all:
            pattern = re.compile('^(.+)\s+\(tag:\s+([^\,\)]+)', re.I)
        else:
            pattern = re.compile('^(\S+)\s+\(.*tag:\s+(' + self.tag_prefix + '[^\,\)]+)', re.I)

        command =  'log --tags --simplify-by-decoration --date=short --pretty="format:%cd %d" '

        rows = self.git_command_rows(command)
        nx = 0
        for row in rows:
            m = pattern.search( row )
            if m:
                self.tags[ m.group(1)] = m.group(2)
            else:
                #print( "no match " + row )
                nx += 1


    def add_tag(self, tag, message=None):
        """ tag the current commit in this repo """

        command = 'tag ' + tag
        if message:
            command += ' -m ' + message

        out = self.git_command( command )
        print "got: ", out
