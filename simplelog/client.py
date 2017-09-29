#!/usr/bin/env python3
"""Simplelog

Quick task logging
"""
import click
import arrow
import re
import os
import requests as req
import hashlib
from sys import exit
from subprocess import call

CURDIR = os.path.dirname(os.path.abspath(__file__))
LOGFILE = '%s.log' % (os.path.join(CURDIR, "data", arrow.now().format('MMDDYY')))
TASKFILE = '%s/tasks.log' % (os.path.join(CURDIR, "data"))
API = 'http://tlvericu16.mskcc.org:9000'


@click.group()
def cli():
    pass


def dated_to_file(msg, filepath):
    logstring = "%s | %s\n" % (
        arrow.now().format('MM/DD/YY HH:mm:ss'),
        ' '.join([str(x) for x in msg]))
    print(logstring)
    with open(filepath, 'a') as f:
        f.write(logstring)


@cli.command()
@click.argument('sub', type=click.STRING)
@click.argument('msg', nargs=-1)
@click.option('-l','--long', required=False, is_flag=True)
def tasks(sub, msg, long):
    mytasks = req.get("{}/task".format(API)).json()
    if sub == 'list':
        print("ID       TIME       STATUS TASK")
        for k, v in mytasks.items():
            if long:
                digest = k
            else:
                digest = k[:6] + ".."
            print("{} {} {} {}".format(digest,
                                       v['time'],
                                       v['status'].ljust(6),
                                       v['task']))

    elif sub == 'add':
        msg = " ".join(msg)
        stamp = arrow.now().timestamp
        digest = hashlib.sha256(msg.encode()).hexdigest()
        req.put("{}/task/{}".format(API, digest), data={'task': msg,
                                                        'time': stamp,
                                                        'status': 'open'
                                                        }).json()
    elif sub == 'del':
        check = []
        for k in mytasks:
            fuzz = re.match(msg[0], k)
            if fuzz:
                check.append(k)
        if len(check) > 1:
            print('error: hash matched multiple tasks. provide more characters')
            raise SystemExit(1)
        elif len(check) == 0:
            print('error: no tasks match that hash')
        else:
            req.delete("{}/task/{}".format(API, check[0]))




@cli.command()
@click.argument('msg', nargs=-1)
def log(msg):
    """add a timestamped log entry"""
    if not msg:
        try:
            with open(LOGFILE, 'r') as f:
                for line in f:
                    print(line)
        except FileNotFoundError:
            print('No logs for today.')
    else:
        dated_to_file(msg, LOGFILE)



@cli.command()
@click.argument('msg', nargs=-1)
def todo(msg):
    """add a timestamped task"""
    if not msg:
        with open(TASKFILE, 'r') as f:
            for line in f:
                print(line)
    else:
        dated_to_file(msg, TASKFILE)


def print_report(filename):
    with open(filename, 'r') as f:
        firstline = f.readline()
        print(firstline[0:8])
        print('--------')
        print("\u2022 %s" % (firstline[20:]), end='')
        for line in f:
            print("\u2022 %s" % (line[20:]), end='')


def print_email_report(filename):
    with open(filename, 'r') as f:
        for line in f:
            print("\u2022 %s" % (line[20:]), end='')


@cli.command()
@click.option('--filename', required=False)
@click.option('--dated/--no-dated', required=False)
@click.argument('count', nargs=1, required=False, type=click.INT)
def report(filename, dated, count):
    """produce email-friendly report"""
    if count:
        for i in reversed(range(count)):
            curlog = '%s.log' % (os.path.join(CURDIR, 'data', arrow.now().replace(days=-i).format('MMDDYY')))
            try:
                if dated:
                    print_report(curlog)
                else:
                    print_email_report(curlog)
            except (FileNotFoundError,):
                pass
    else:
        if not filename:
            if dated:
                print_report(LOGFILE)
            else:
                print_email_report(LOGFILE)
        else:
            if dated:
                print_report(filename)
            else:
                print_email_report(filename)


@cli.command()
@click.argument('subcommand', nargs=1, required=False)
def edit(subcommand):
    """open log or tasklist in editor"""
    enveditor = os.environ.get('enveditor', 'vim')  # vim default
    if not subcommand or subcommand == 'log':
        call([enveditor, LOGFILE])
    elif subcommand == 'todo':
        call([enveditor, TASKFILE])
    else:
        print("Unknown subcommand: %s" % subcommand)
        exit(1)


if __name__ == '__main__':
    cli()
