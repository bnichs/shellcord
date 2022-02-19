import json
import logging
import os
import re
from abc import abstractmethod
from copy import deepcopy
from dataclasses import dataclass, asdict
from json import JSONDecodeError
from pprint import pprint
from typing import Union, List, Dict

from shellcord.config import SCORD_ID_REGEX


logger = logging.getLogger(__name__)


class ScordEl(object):
    """General representation for a json string in an scord log"""

    @classmethod
    def from_dict(cls, d: dict) -> "ScordEl":
        if "type" not in d:
            raise ValueError("Found no type in json string")

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
        return f"scord-runbook-{self.session_id}.md"

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
