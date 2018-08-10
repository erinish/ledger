#!/usr/bin/env python3
"""Ledger

Quick task logging
"""
import argparse
import re
import sys
import json
import requests as req
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


def config_dump():
    """Dump configuration"""
    for k, v in f_config.items():
        display.print("{0}={1}".format(k, v))


def report_tasks(args):
    """Produce a report of completed tasks"""
    filterkwargs = {'status': 'closed'}
    if args.days:
        filterkwargs['close_time'] = arrow.now().timestamp - (int(days) * 86400)
    else:
        filterkwargs['close_time'] = arrow.now().timestamp - (7 * 86400)
    mytasks = req.get("{}/task".format(API)).json()
    tasksbytime = sorted(mytasks.items(), key=lambda x: x[1]['close_time'], reverse=True)
    for entry in tasksbytime:
        if filter_tasks(entry[1], **filterkwargs):
            if not args['show-dates']:
                print("\u2022 {}".format(entry[1]['task']))
            else:
                humantime = arrow.get(entry[1]['time']).to('local').format('MM/DD')
                print("{} {}".format(humantime, entry[1]['task']))


def list_task(args):
    """List all tasks"""
    filterkwargs = {}
    if args.days and not args.closed:
        filterkwargs['days'] = arrow.now().timestamp - (int(days) * 86400)
    elif args.days:
        filterkwargs['close_time'] = arrow.now().timestamp - (int(days) * 86400)

    if args.closed:
        filterkwargs['status'] = 'closed'

    try:
        mytasks = req.get("{}/task".format(API)).json()
    except req.exceptions.ConnectionError as exc:
        display.print("Error: could not connect to server. Is it running?")
        sys.exit(1)

    # On specific runs for closed tasks, reverse sort by time closed
    # but if open tasks or all tasks, sort by time opened
    if args.closed:
        tasksbytime = sorted(mytasks.items(), key=lambda x: x[1]['close_time'], reverse=True)
    else:
        tasksbytime = sorted(mytasks.items(), key=lambda x: x[1]['time'], reverse=True)

    # Print the header
    display.print("{} {:>10} {:>16} {}".format(*['ID', 'TIME', 'STATUS', 'TASK']))
    for entry in tasksbytime:
        if filter_tasks(entry[1], **filterkwargs):
            # FIXME: overwriting a builtin
            if args.long:
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


def add_task(args):
    """Add a new task"""
    if args.closed:
        status = 'closed'
    else:
        status = 'open'
    msg = " ".join(args.msg)
    stamp = int(arrow.now().timestamp)
    headers = {"Content-Type": "application/json"}
    if status == 'closed':
        close_time = stamp
    else:
        close_time = 0
    r = req.put("{}/task".format(API), data=json.dumps({'task': msg, 'time': stamp, 'close_time': close_time, 'status': status}), headers=headers)
    display.dump(r.json())


def del_task(args):
    """Remove a task"""
    uri = check_id(API, args.hash)
    if uri:
        r = req.delete("{}/task/{}".format(API, uri))
        display.dump(r.json())


def close_task(args):
    """close a task with an optional comment"""
    headers = {"Content-Type": "application/json"}
    uri = check_id(API, args.hash)
    if uri:
        stamp = int(arrow.now().timestamp)
        r = req.put("{}/task/{}".format(API, uri), data=json.dumps({'status': 'closed', 'close_time': stamp}), headers=headers)
        display.dump(r.json())


def main():
    '''
    Logic and CLI handling
    '''

    parser = argparse.ArgumentParser(description='Ledger CLI')
    subparsers = parser.add_subparsers()

    # Conf Parser
    conf_parser = subparsers.add_parser('config')
    conf_parser.set_defaults(func=config_dump)

    # LS Parser
    ls_parser = subparsers.add_parser('ls')
    ls_parser.add_argument('-c', '--closed', action='store_true')
    ls_parser.add_argument('-l', '--long', action='store_true')
    ls_parser.add_argument('-d', '--days', nargs=1, type=int)
    ls_parser.set_defaults(func=list_task)

    # Report Parser
    report_parser = subparsers.add_parser('report')
    report_parser.add_argument('--show-dates', action='store_true')
    report_parser.add_argument('-d', '--days', nargs=1, type=int)
    report_parser.set_defaults(func=report_tasks)

    # Add Parser
    add_parser = subparsers.add_parser('add')
    add_parser.add_argument('-c', '--closed', action='store_true')
    add_parser.add_argument('msg', nargs=argparse.REMAINDER)
    add_parser.set_defaults(func=add_task)

    # RM Parser
    rm_parser = subparsers.add_parser('rm')
    rm_parser.add_argument('hash', nargs=argparse.REMAINDER)
    rm_parser.set_defaults(func=del_task)

    # Close Parser
    close_parser = subparsers.add_parser('close')
    close_parser.add_argument('hash', nargs=argparse.REMAINDER)
    close_parser.add_argument('msg', nargs=argparse.REMAINDER)
    close_parser.set_defaults(func=close_task)

    args = parser.parse_args()


if __name__ == '__main__':
    main()
