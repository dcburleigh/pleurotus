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

    log_format1 = "  --pretty=format:'%ad %h | %s ' --date=short"
    log_format_files = " --name-only --pretty=format:'%ad %h | %s ' --date=short"
    
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

            
    
    def git_command_rows(self, command):
        out = self.git_command(command)
        out = re.sub('\s+$', '', out) 
        #print( "'%s'  " % out )
        if not out:
            return []
        return out.split("\n")
    
    def git_command(self, git_args):
        clist =  [ 'cd ' + self.dir + '; git ' + git_args ]

        out = None
        serr = None

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
    
    def get_log(self, log_args=''):
        args = ''
        command = "log "  + log_args + self.log_format1 
        self.commits = self.git_command_rows(command)
    
    def get_status(self):
        return self.git_command_rows('status --short')
        
    def get_tags(self, all=False):
        
        pattern = re.compile('^(.+)\s+\(tag:\s+([^\,\)]+)', re.I)
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
    
    
            