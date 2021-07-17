import click
from pyparsing import *

import os
import sys
import pathlib
import subprocess
import locale
import tempfile
import shlex

locale.setlocale(locale.LC_ALL,'')
encoding = locale.getpreferredencoding()



def error(msg):
  click.echo(click.style(msg,fg='red'))

def sucess(msg):
  click.echo(click.style(msg,fg='green'))

def info(msg):
  click.echo(msg)


class parsers:
    compiler_command_modeline = Literal("snippet-compiler.compiler-command") + Literal(":") + restOfLine('compiler-command')
    exec_name_modeline = Literal("snippet-compiler.exec-name") + Literal(":") + restOfLine('exec-name')




@click.command()
@click.option("--verbose","-v",is_flag=True,help="Print verbose messages.")
@click.option('--compiler-command', default="g++ {file}", help="Compiler command line to run. This is a string.template, use {file} to reference the filename.")
@click.option('--run/--no-run', help="Run execuable after compiling.")
@click.option('--exec-name', default="./a.out", help="The execuable name that will be run if --run is given.")
@click.pass_context
def main(ctx,verbose,compiler_command,run,exec_name):
  '''
  Read code snippet from standard input and compile it.
  '''


  with tempfile.TemporaryDirectory() as dir:
      os.chdir(dir)
      sourcefile = pathlib.Path("main.cpp")
      sourcecode =  "\n".join(sys.stdin) 

      # check source code for modelines
      compiler_command_modelines = parsers.compiler_command_modeline.searchString(sourcecode)
      for line in compiler_command_modelines:
          if 'compiler-command' in line:
              compiler_command = line['compiler-command']
      exec_name_modelines = parsers.exec_name_modeline.searchString(sourcecode)
      for line in exec_name_modelines:
          if 'exec-name' in line:
              exec_name = line['exec-name']


      sourcefile.write_text(sourcecode)
      cmd = compiler_command.format(file=str(sourcefile))
      res = subprocess.run(shlex.split(cmd))
      if run and res.returncode == 0:
          subprocess.run(exec_name)



