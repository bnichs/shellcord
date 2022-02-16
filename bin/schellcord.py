#!/usr/bin/env python
import logging
from abc import abstractmethod
from copy import deepcopy
from dataclasses import dataclass, asdict
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


class ScordEl(object):
    """General representation for a json string in an scord log"""

    @classmethod
    def from_dict(cls, d: dict) -> "ScordEl":
        if "type" not in d:
            raise ValueError("Found not type in json string")

        typ = d['type']
        logger.debug("Building el for type=%s", typ)

        if typ == "cmd":
            return Command.from_dict(d)
        elif typ == "tag":
            return Tag.from_dict(d)
        else:
            raise ValueError("Unknown element type=%s", typ)

    @abstractmethod
    def to_dict(self):
        pass

    def dump(self, fname=None):
        """
        Dump this tag to the given scord log file
        :return:
        """
        fname = fname or os.environ.get("SCORD_LOG_FILE", None)

        if not fname:
            raise

        with open(fname, 'a') as f:
            jtxt = json.dumps(self.to_dict(), indent=4) + "\n"
            f.write(jtxt)


@dataclass
class Command(ScordEl):
    cmd: str
    scord_id: str
    exit_code: int

    def __post_init__(self):
        self.exit_code = int(self.exit_code)

    def to_dict(self) -> dict:
        d = asdict(self)
        d['type'] = 'cmd'
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Command":
        d = deepcopy(d)
        del d['type']

        return Command(**d)



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