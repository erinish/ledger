#!/usr/bin/env python3
"""Simplelog

Quick task logging
"""
import click
import arrow
import os
from subprocess import call

CURDIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE = '%s.log' % (os.path.join(CURDIR, "data", arrow.now().format('MMDDYY')))

@click.group()
def cli():
    pass


@click.command()
@click.argument('msg', nargs=-1)
def log(msg):
    """add a timestamped log entry"""
    logstring = "%s | %s\n" % (
        arrow.now().format('MM/DD/YY HH:mm:ss'),
        ' '.join([str(x) for x in msg]))
    print(logstring)
    with open(LOGFILE, 'a') as f:
        f.write(logstring)

@click.command()
def cat():
    """print raw log file"""
    with open(LOGFILE, 'r') as f:
        for line in f:
            print(line)

def print_report(filename):
    with open(filename, 'r') as f:
        firstline = f.readline()
        print(firstline[0:8])
        print('--------')
        print("\u2022 %s" % (firstline[20:]), end='')
        for line in f:
            print("\u2022 %s" % (line[20:]), end='')

@click.command()
@click.option('--filename', required=False)
@click.argument('count', nargs=1, required=False, type=click.INT)
def report(filename, count):
    """produce email-friendly report"""
    if count:
        for i in reversed(range(count)):
            curlog = '%s.log' % (os.path.join(CURDIR, 'data', arrow.now().replace(days=-i).format('MMDDYY')))
            try:
                print_report(curlog)
            except (FileNotFoundError,):
                pass
    else:
        if not filename:
            print_report(LOGFILE)
        else:
            print_report(filename)


@click.command()
def edit():
    """open log in editor"""
    enveditor = os.environ.get('enveditor', 'vim')  # vim default
    call([enveditor, LOGFILE])

cli.add_command(log)
cli.add_command(cat)
cli.add_command(report)
cli.add_command(edit)

if __name__ == '__main__':
    cli()
