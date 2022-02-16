#!/usr/bin/env python
from dataclasses import dataclass
import logging
from json import JSONDecodeError
from pprint import pprint
from typing import List

import click
import json

TRIPLE_TICKS = "```"

SCORD_LOG_REGEX = "scord-\w+.json"


logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)




@dataclass
class Command(object):
    cmd: str
    scord_id: str
    exit_code: int

    @classmethod
    def from_array(cls, arr: List[str]):
        cmd, scord_id, exit_str = arr

        exit_code = int(exit_str)
        cmd = Command(cmd, scord_id, exit_code)

        return cmd


@dataclass
class RunbookOptions(object):
    allow_exit_codes = None

    def __post_init__(self):
        self.allow_exit_codes = self.allow_exit_codes or [0]


@dataclass
class RunbookGenerator(object):
    cmds: List[Command]
    opts: RunbookOptions = None

    def code_part(self, s: str):
        return f"{TRIPLE_TICKS}bash\n{s}\n{TRIPLE_TICKS}"

    def make_markdown(self, fname: str):
        txt = ""

        for command in self.cmds:
            txt += self.code_part(command.cmd)
            txt += "\n"

        with open(fname, 'w') as f:
            f.write(txt)

        logger.info("Wrote runbook to %s", fname)


    return cmds


# @click.group("cli")
# @click.pass_context
@click.command()
# @click.argument("file")
@click.argument('file', type=click.File('r'))
def cli(file):
    """An example CLI for interfacing with a document"""

    cmds = parse_file(file)

    gen = RunbookGenerator(cmds)
    pprint(cmds)

    print(gen)
    gen.make_markdown("out.md")


    # _stream = open(document)
    # _dict = json.load(_stream)
    # _stream.close()
    # ctx.obj = _dict


def main():
    cli()


if __name__ == '__main__':
    main()