#!/usr/bin/env python
"""
SVNIGNORE
by Jonathan Beilin (github: dongle)
A script to allow the usage of a git-like .svnignore file in the root of the
working copy.

USAGE
$ svnignore CMD

EXAMPLES
$ svnignore update
$ svnignore commit -m "boblog"

.SVNIGNORE EXAMPLE (list files, one per line)
Array.h
Array.inl
*.png

TODO
- add README.md for github
- get more immediate stdout output
- bundle?
- add --ignore option to define files to ignore on the fly
- add makechangelist command to only make changelist
- add removechangelist command to only remove changelist

THANKS
- Rich Jones (github: miserlou) for code review
- Ignacio Castano for inspiration
"""

import sys
import os
import shlex
import subprocess
import fnmatch

##
## CONFIG
##

dotfile_name = '.svnignore'

##
## END CONFIG
##

def execute(command, env=None, ignore_errors=False):
  """
  Utility function to execute a command and return the output.
  Derived from Review Board's post-review script.
  """
  if env:
    env.update(os.environ)
  else:
    env = os.environ

  p = subprocess.Popen(command,
                       stdin = subprocess.PIPE,
                       stdout = subprocess.PIPE,
                       stderr = subprocess.STDOUT,
                       shell = False,
                       close_fds = sys.platform.startswith('win'),
                       universal_newlines = True,
                       env = env)
  data = p.stdout.read()
  rc = p.wait()
  
  if rc and not ignore_errors:
    sys.stderr.write('Failed to execute command: %s\n%s\n' % (command, data))
    sys.exit(1)

  return data

def clear_changelist(wc_rootpath):
  print 'clearing old changelist'
  args = shlex.split('changelist --remove --cl svnignore --depth infinity ' + wc_rootpath + ' -R')
  data = execute(['svn'] + args, env = {'LANG': 'en_US.UTF-8'})
  
def create_changelist():
  print 'making new changelist'
  args = shlex.split('changelist svnignore ' + '.' +  ' -R')
  data = execute(['svn'] + args, env = {'LANG': 'en_US.UTF-8'})

def filter_changelist(excludes_list):
  print 'filtering changelist'
  # match items in exclude lists with paths; add to list of matches
  matches = []
  for root, dirnames, filenames in os.walk('.'):
    for i in excludes_list:
      for filename in fnmatch.filter(filenames, i):
        matches.append(os.path.join(root, filename))
  
  args = shlex.split('changelist --remove --cl svnignore') + matches
  # ignore errors since files that are in the path of the working copy yet not added to svn will generate errors when they are removed
  data = execute(['svn'] + args, env = {'LANG': 'en_US.UTF-8'}, ignore_errors = True)
  
def parse_dotfile(wc_rootpath):
  dotfile = open(wc_rootpath + '/' + dotfile_name)
  excludes_list = [i.strip() for i in dotfile.readlines()]
    
  return excludes_list
  
def find_root():
  data = execute(['svn', 'info'], env = {'LANG': 'en_US.UTF-8'})
  root = data.splitlines()[1].split(':')[1].strip()
    
  return root
  
def parse_args():
  # want to strip everything from --ignore until next arg
  # and add to separate array for ad-hoc ignores
  # also check for makechangelist in which case it will only make changelist
  pass

def main():
  args = sys.argv[1:]
  args += shlex.split("--cl svnignore")
  
  wc_rootpath = find_root()
  
  excludes_list = parse_dotfile(wc_rootpath)
  
  clear_changelist(wc_rootpath)
  
  create_changelist()
  
  filter_changelist(excludes_list)
  
  print 'executing command'
  data = execute(['svn'] + args, env = {'LANG': 'en_US.UTF-8'})

  print data

if __name__ == '__main__':
  main()