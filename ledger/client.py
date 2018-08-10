#!/usr/bin/env python3
"""Ledger

Quick task logging
"""
import re
import sys
import json
import requests as req
import click
import arrow
from ledger.utils import check_id, filter_tasks, ConfigBoss
from stain import Stain

configboss = ConfigBoss()
stain = Stain()
f_config = {}

DEFAULT_CONFIG = {"api": "http://localhost:9000",
                  "callback_plugin": "yaml",
                  "debug": False
                  }

if 'client' in configboss.config_data.sections():
    for k, v in DEFAULT_CONFIG.items():
        if k in configboss.config_data['client']:
            if k == 'debug':
                f_config[k] = configboss.config_data['client'].getboolean(k)
            else:
                f_config[k] = v
        else:
            f_config[k] = DEFAULT_CONFIG[k]
else:
    f_config = DEFAULT_CONFIG

API = f_config['api']
CALLBACK_PLUGIN = f_config['callback_plugin']

if CALLBACK_PLUGIN == 'yaml':
    import yaml


class Display():

    def __init__(self, callback_plugin):
        self.callback_plugin = callback_plugin

    def dump(self, json_msg):
        """
        Print a JSON object to the display.
        Defaults to printing as YAML since this is easier for humans,
        but supports direct dumping as well.
        """
        if self.callback_plugin == 'json':
            print(json.dumps(json_msg))
        elif self.callback_plugin == 'yaml':
            print(yaml.dump(yaml.load(json.dumps(json_msg)), default_flow_style=False))

    def print(self, msg):
        print(msg)

    def debug(self, msg):
        if DEBUG:
            print(msg)

display = Display(CALLBACK_PLUGIN)


@click.group()
def cli():
    pass


@cli.command(name='config')
def config_dump():
    """Dump configuration"""
    for k, v in f_config.items():
        display.print("{0}={1}".format(k, v))


@cli.command(name='report')
@click.option('-d', '--days', type=click.INT)
@click.option('-e', '--email', is_flag=True)
def report_tasks(days, email):
    """Produce a report of completed tasks"""
    filterkwargs = {'status': 'closed'}
    if days:
        filterkwargs['close_time'] = arrow.now().timestamp - (int(days) * 86400)
    else:
        filterkwargs['close_time'] = arrow.now().timestamp - (7 * 86400)
    mytasks = req.get("{}/task".format(API)).json()
    tasksbytime = sorted(mytasks.items(), key=lambda x: x[1]['close_time'], reverse=True)
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
@click.option('-c', '--closed', required=False, is_flag=True)
def list_task(long, days, closed):
    """List all tasks"""
    filterkwargs = {}
    if days and not closed:
        filterkwargs['days'] = arrow.now().timestamp - (int(days) * 86400)
    elif days:
        filterkwargs['close_time'] = arrow.now().timestamp - (int(days) * 86400)

    if closed:
        filterkwargs['status'] = 'closed'

    try:
        mytasks = req.get("{}/task".format(API)).json()
    except req.exceptions.ConnectionError as exc:
        display.print("Error: could not connect to server. Is it running?")
        sys.exit(1)
    
    # On specific runs for closed tasks, reverse sort by time closed
    # but if open tasks or all tasks, sort by time opened
    if closed:
        tasksbytime = sorted(mytasks.items(), key=lambda x: x[1]['close_time'], reverse=True)
    else:
        tasksbytime = sorted(mytasks.items(), key=lambda x: x[1]['time'], reverse=True)

    # Print the header
    display.print("{} {:>10} {:>16} {}".format(*['ID', 'TIME', 'STATUS', 'TASK']))
    for entry in tasksbytime:
        if filter_tasks(entry[1], **filterkwargs):
            #FIXME: overwriting a builtin
            if long:
                digest = entry[0]
            else:
                digest = entry[0][:6] + ".."
            if entry[1]['status'] == 'closed':
                humantime = arrow.get(entry[1]['close_time']).to('local').format('MM/DD/YY HH:mm')
                with stain.dim():
                    display.print("{:>8} {:<14} {:>6} {}".format(digest, humantime, entry[1]['status'], entry[1]['task'])) 
            else:
                humantime = arrow.get(entry[1]['time']).to('local').format('MM/DD/YY HH:mm')
                with stain.bold():
                    display.print("{:>8} {:<14} {:>6} {}".format(digest, humantime, entry[1]['status'], entry[1]['task']))


@cli.command(name='add')
@click.argument('msg', nargs=-1)
@click.option('-c', '--closed', required=False, is_flag=True)
def add_task(msg, closed):
    """Add a new task"""
    if closed:
        status = 'closed'
    else:
        status = 'open'
    msg = " ".join(msg)
    stamp = int(arrow.now().timestamp)
    headers = {"Content-Type": "application/json"}
    if status == 'closed':
        close_time = stamp
    else:
        close_time = 0
    r = req.put("{}/task".format(API), data=json.dumps({'task': msg, 'time': stamp, 'close_time': close_time, 'status': status}), headers=headers)
    display.dump(r.json())


@cli.command(name='rm')
@click.argument('msg', type=click.STRING)
def del_task(msg):
    """Remove a task"""
    uri = check_id(API, msg)
    if uri:
        r = req.delete("{}/task/{}".format(API, uri))
        display.dump(r.json())


@cli.command(name='close')
@click.argument('tsk')
@click.argument('msg', nargs=-1)
def close_task(tsk, msg):
    """close a task with an optional comment"""
    headers = {"Content-Type": "application/json"}
    uri = check_id(API, tsk)
    if uri:
        stamp = int(arrow.now().timestamp)
        r = req.put("{}/task/{}".format(API, uri), data=json.dumps({'status': 'closed', 'close_time': stamp}), headers=headers)
        display.dump(r.json())


if __name__ == '__main__':
    cli()
