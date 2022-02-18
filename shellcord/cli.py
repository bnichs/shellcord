import logging
import os
import re
from pathlib import Path

import click

from shellcord.scord import Tag, ScordLog
from shellcord.config import SCORD_LOG_REGEX
from shellcord.generator import RunbookGenerator

logger = logging.getLogger(__name__)


@click.group("cli")
def cli():
    """Root cli"""
    print('ff')
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
@click.option('--file', type=str, default=None, help="The scord log file. If unset will search PWD for the most recent option")
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


if __name__ == '__main__':
    cli()
