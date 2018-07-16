#!/usr/bin/env python3
"""Ledger

Quick task logging
"""
import re
import json
import requests as req
import click
import arrow
from ledger.utils import check_id, filter_tasks
CALLBACK_PLUGIN = 'yaml'
if CALLBACK_PLUGIN == 'yaml':
    import pyyaml as yaml

API = 'http://localhost:9000'


class Display(callback_plugin):

    def __init__(self):
        self.callback_plugin = CALLBACK_PLUGIN

    def dump(self, json_msg):
        if self.callback_plugin == 'json':
            print(json.dumps(json_msg))
        elif self.callback_plugin == 'yaml':
            print(yaml.dumps(yaml.loads(json.dumps(json_msg))))

    def print(self, msg):
        print(msg)

display = Display(CALLBACK_PLUGIN)


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
@click.option('-z', '--zefault', required=False, is_flag=True)
def list_task(long, days, status, zefault):
    """List all tasks"""
    filterkwargs = {}
    if days and not zefault:
        filterkwargs['days'] = arrow.now().timestamp - (int(days) * 86400)
    if status and not zefault:
        filterkwargs['status'] = status
    if zefault:
        filterkwargs['status'] = 'open'
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
    stamp = str(arrow.now().timestamp)
    headers = {"Content-Type": "application/json"}
    r = req.put("{}/task".format(API),
                data=json.dumps({'task': msg,
                                 'time': stamp,
                                 'status': status
                                 }),
                headers=headers)
    display.dump(r.json)


@cli.command(name='rm')
@click.argument('msg', type=click.STRING)
def del_task(msg):
    """Remove a task"""
    uri = check_id(API, msg)
    if uri:
        r = req.delete("{}/task/{}".format(API, uri))
        display.dump(r.json)


@cli.command(name='close')
@click.argument('tsk')
@click.argument('msg', nargs=-1)
def close_task(tsk, msg):
    """close a task with an optional comment"""
    headers = {"Content-Type": "application/json"}
    uri = check_id(API, tsk)
    if uri:
        r = req.put("{}/task/{}".format(API, uri), data=json.dumps({'status': 'closed'}), headers=headers)
        display.dump(r.json)


if __name__ == '__main__':
    cli()
