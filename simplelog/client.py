#!/usr/bin/env python3
"""Simplelog

Quick task logging
"""
import re
import json
import requests as req
import click
import arrow
from simplelog.utils import check_id, filter_tasks

API = 'http://tlvericu16.mskcc.org:9000'

@click.group()
def cli():
    pass


@cli.command(name='report')
@click.option('-d', '--days', type=click.INT)
@click.option('-e', '--email', is_flag=True)
def report_tasks(days, email):
    """Produce a report of completed tasks"""
    filterkwargs = {'status': 'closed'}
    if days:
        filterkwargs['days'] = arrow.now().timestamp - (int(days) * 86400)
    else:
        filterkwargs['days'] = arrow.now().timestamp - (7 * 86400)
    mytasks = req.get("{}/task".format(API)).json()
    tasksbytime = sorted(mytasks.items(), key=lambda x: x[1]['time'], reverse=True)
    for entry in tasksbytime:
        if filter_tasks(entry[1], **filterkwargs):
            if email:
                print("\u2022 {}".format(entry[1]['task']))
                pass
            else:
                humantime = arrow.get(entry[1]['time']).to('local').format('MM/DD')
                print("{} {}".format(humantime, entry[1]['task']))


@cli.command(name='ls')
@click.option('-l', '--long', required=False, is_flag=True)
@click.option('-d', '--days', help="number of days before now")
@click.option('-s', '--status')
def list_task(long, days, status):
    """List all tasks"""
    filterkwargs = {}
    if days:
        filterkwargs['days'] = arrow.now().timestamp - (int(days) * 86400)
    if status:
        filterkwargs['status'] = status
    mytasks = req.get("{}/task".format(API)).json()
    tasksbytime = sorted(mytasks.items(), key=lambda x: x[1]['time'], reverse=True)
    print("{} {:>10} {:>16} {}".format(*['ID', 'TIME', 'STATUS', 'TASK']))
    for entry in tasksbytime:
        if filter_tasks(entry[1], **filterkwargs):
            if long:
                digest = entry[0] 
            else:
                digest = entry[0][:6] + ".."
            humantime = arrow.get(entry[1]['time']).to('local').format('MM/DD/YY HH:mm')
            print("{:>8} {:<14} {:>6} {}".format(digest,
                                                 humantime,
                                                 entry[1]['status'],
                                                 entry[1]['task']))

@cli.command(name='add')
@click.argument('msg', nargs=-1)
@click.option('-s', '--status', type=click.STRING)
def add_task(msg, status):
    """Add a new task"""
    if not status:
        status = 'open'
    msg = " ".join(msg)
    stamp = arrow.now().timestamp
    headers = {"Content-Type": "application/json"}
    r = req.put("{}/task".format(API), data=json.dumps({'task': msg,
                                             'time': stamp,
                                             'status': status
                                             }),
                                       headers=headers)
    print(r.text)

@cli.command(name='rm')
@click.argument('msg', type=click.STRING)
def del_task(msg):
    """Remove a task"""
    uri = check_id(API, msg)
    if uri:
        r = req.delete("{}/task/{}".format(API, uri))
        print(r.text)

@cli.command(name='close')
@click.argument('tsk')
@click.argument('msg', nargs=-1)
def close_task(tsk, msg):
    """close a task with an optional comment"""
    uri = check_id(API, tsk)
    if uri:
        r = req.put("{}/task/{}".format(API,uri), data={'status': 'closed'})
        print(r.text)



if __name__ == '__main__':
    cli()
