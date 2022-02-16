#!/usr/bin/env python
import logging
import os
import re
from abc import abstractmethod
from copy import deepcopy
from dataclasses import dataclass, asdict
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from pprint import pprint
from typing import List, Dict, Union

import click
import json

TRIPLE_TICKS = "```"

SCORD_LOG_REGEX = r"scord-log-\w+.json"
SCORD_ID_REGEX = r"scord-(\w+)-(\w+)"


DEFAULT_OUT_FILE = "scord-out.md"


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
class ScordID(object):
    session_id: str
    cmd_id: str = None

    @classmethod
    def from_str(cls, sid: Union[str, "ScordID"]) -> "ScordID":
        if isinstance(sid, ScordID):
            return sid

        m = re.match(SCORD_ID_REGEX, sid)
        session_id, cmd_id = m.groups()
        return ScordID(session_id, cmd_id)

    def __hash__(self):
        return hash((self.session_id, self.cmd_id))


@dataclass
class Command(ScordEl):
    cmd: str
    scord_id: ScordID
    exit_code: int

    def __post_init__(self):
        self.exit_code = int(self.exit_code)
        self.scord_id = ScordID.from_str(self.scord_id)

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
class Tag(ScordEl):
    scord_id: str
    tag_str: str

    @classmethod
    def from_dict(cls, d: dict) -> "Tag":
        d = deepcopy(d)
        del d['type']
        return Tag(**d)

    def to_dict(self):
        d = asdict(self)
        d['type'] = 'tag'
        return d


@dataclass
class RunbookOptions(object):
    allow_exit_codes = None

    def __post_init__(self):
        self.allow_exit_codes = self.allow_exit_codes or [0]

    def include_command(self, command: Command):
        if command.exit_code not in self.allow_exit_codes:
            return False

        return True


class DefaultRunbookOptions(RunbookOptions):
    pass



@dataclass
class ScordLog(object):
    """Wrap cmds.log"""
    cmds: List[Command]  # All the commadns run
    tags: Dict[ScordID, Tag]  # scord_id -> Tag

    def __post_init__(self):
        self.clean_commands()

    def clean_commands(self):
        """
        Our shell wrappers will include the first command run which is us invoking shellcord (source init.sh)

        Ensure the first session command's ID doesn't match the others then remove it
        """
        first, second, *_ = self.cmds

        if first.scord_id.session_id == second.scord_id.session_id:
            logger.warning("Found the first command's session to match the second's. We expect the first command to not be a part of this session")
        else:
            logger.debug("Removing the first command as its from a previous session")
            self.cmds = self.cmds[1:]

    @property
    def session_id(self):
        session_ids = {s.scord_id.session_id for s in self.cmds}
        if len(session_ids) > 1:
            raise ValueError("Found multiple session ids in the same log")
        elif len(session_ids) == 0:
            raise ValueError("Found no session ids")
        else:
            return session_ids.pop()

    def out_fname(self):
        """The fname for the outputted markdown file"""
        print(self.session_id)

        return f"scord-runbook-{self.session_id}.md"

        for cmd in self.cmds:
            print(cmd.scord_id)
        raise

    @classmethod
    def fix_json(cls, jtext):
        """
        Add surrounding [ ... ] and commas to a list of json strings
        :param jtext:
        :return:
        """
        logger.debug("Fixing badly formatted json")

        jtext = jtext.replace("}\n{", "},\n{")
        jtext = f"[\n{jtext}\n]"

        return jtext

    @classmethod
    def from_els(cls, els: List[ScordEl]) -> "ScordLog":
        pprint(els)
        cmds = []
        tags = {}

        for el in els:
            if isinstance(el, Command):
                cmds.append(el)
            elif isinstance(el, Tag):
                tags[el.scord_id] = el
            else:
                raise ValueError

        return ScordLog(cmds, tags)

    @classmethod
    def from_dict(cls, full_d: dict) -> "ScordLog":
        logger.debug("Building a full ScordLog from dict with %d elements in it", len(full_d))
        els = []
        for d in full_d:
            el = ScordEl.from_dict(d)
            els.append(el)

        return cls.from_els(els)

    @classmethod
    def parse_file(cls, file: str) -> "ScordLog":
        logger.debug("Building a full log from json")
        with open(file) as f:
            jtext = f.read()

            try:
                j = json.loads(jtext, strict=False)
            except JSONDecodeError as e:
                jtext = cls.fix_json(jtext)
                j = json.loads(jtext, strict=False)

        return cls.from_dict(j)


@dataclass
class RunbookGenerator(object):
    scord_log: ScordLog
    opts: RunbookOptions = DefaultRunbookOptions()

    @classmethod
    def heading(cls, level: int, s: str):
        pre = "#" * level
        return f"{pre} {s}"

    @classmethod
    def linebreak(cls, lines: int = 1):
        br = "<br/>"
        return "\n".join(br for i in range(lines))

    @property
    def footer_str(self):
        now = datetime.now()
        return f"Generated by shellcord session={self.scord_log.session_id} at {now}"

    def footer(self):
        txt = ""
        txt += self.linebreak(lines=5) + "\n\n"
        txt += self.heading(6, self.footer_str)
        return txt

    def code_part(self, s: str):
        return f"{TRIPLE_TICKS}bash\n{s}\n{TRIPLE_TICKS}"

    def make_command(self, command: Command, cmd_num: int):
        txt = ""

        if command.scord_id in self.scord_log.tags:
            tag = self.scord_log.tags[command.scord_id]
            txt += self.heading(3, tag.tag_str)
        else:
            d = cmd_num
            txt += self.heading(3, f"Command #{d}")
        txt += "\n"
        txt += self.code_part(command.cmd)
        return txt

    def make_markdown(self, fname: str):
        txt = ""

        for cmd_num, command in enumerate(self.scord_log.cmds):
            if not self.opts.include_command(command):
                logger.debug("Skipping command %s", command)
            txt += self.make_command(command, cmd_num=cmd_num)
            txt += "\n\n"

        txt += self.footer()

        with open(fname, 'w') as f:
            f.write(txt)

        logger.info("Wrote runbook to %s", fname)


@click.group("cli")
def cli():
    """Root cli"""
    pass


def find_file():
    """Try and find a file that looks like an scord log"""
    fils = []
    for fil in os.listdir(os.getcwd()):
        if re.match(SCORD_LOG_REGEX, fil):
            logger.debug("File %s matches", fil)
            fil = Path(fil)
            create_time = fil.stat().st_ctime
            fils.append((fil, create_time))

    if not fils:
        raise ValueError("Found no scord log files. Has shellcord ever run?")

    fils = sorted(fils, key=lambda x: x[1], reverse=True)
    fil, _ = fils[0]
    logger.debug("Found %d files that match, taking the newest one, %s", len(fils), fil)
    return str(fil.absolute())


@cli.command()
@click.option('--file', type=click.File('r'), default=None, help="The scord log file. If unset will search PWD for the most recent option")
@click.option('--out-file', type=click.File('w'), default=None, help="Where to write the runbook file")
def generate(file, out_file):
    if not file:
        file = find_file()
    scord_log = ScordLog.parse_file(file)

    gen = RunbookGenerator(scord_log)

    out_file = out_file or scord_log.out_fname()
    gen.make_markdown(out_file)


@cli.group()
def tag():
    pass


@tag.command("next")
@click.argument('tag_str', type=str)
def tag_next(tag_str):
    """
    Tag the next command run with this string
    """
    # Idk how to do this one yet.
    raise
    # scord_cmd = os.environ['SCORD_CMD']
    # logger.debug("Tagging next command %s with %s", scord_cmd, tag_str)
    # print(tag_str)


@tag.command("previous")
@click.argument('tag_str', type=str)
def tag_previous(tag_str):
    """
    Tag the last command run with this string
    """
    if 'LAST_SCORD_ID' not in os.environ:
        raise ValueError("Can't find the last command, is shellcord initialized?")
    scord_id = os.environ['LAST_SCORD_ID']
    logger.debug("Tagging previous command %s with %s", scord_id, tag_str)

    t = Tag(scord_id=scord_id,
            tag_str=tag_str)

    logger.debug("Saving tag value %s", t)
    t.dump()


def main():
    cli()


if __name__ == '__main__':
    main()
