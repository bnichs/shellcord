import logging
import os
import re
from pathlib import Path
from pprint import pprint

import click
from click import pass_context

from shellcord.scord import Tag, ScordLog
from shellcord.config import SCORD_LOG_REGEX, FORCE_DEBUG, DEFAULT_LOG_LEVEL
from shellcord.generator import RunbookGenerator

logger = logging.getLogger()


CLI_CONTEXT = dict(help_option_names=["-h", "--help"])


# @click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option('--debug/--no-debug', type=bool, default=False)
@click.option('--log-file', type=str, default=None,
              help="The scord log file. If unset will search PWD for the most recent option")
@click.group("cli", context_settings=CLI_CONTEXT)
@click.pass_context
def cli(ctx, debug, log_file: str):
    """Root cli"""
    ctx.ensure_object(dict)

    global logger
    if debug or FORCE_DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(DEFAULT_LOG_LEVEL)

    # logger = logging.getLogger()
    logging.basicConfig()

    log_file = log_file or os.environ.get("SCORD_LOG_FILE", None)
    logger.debug("Getting commands from scord file %s", log_file)

    if not log_file:
        log_file = find_file()

    if not log_file:
        raise FileNotFoundError("No scord log file found. Has shellcord been run yet?")
    scord_log = ScordLog.parse_file(log_file)

    ctx.obj['scord_log'] = scord_log
    ctx.obj['scord_log_path'] = log_file
    # print(scord_log)


def find_file():
    """Try and find a file that looks like an scord log"""
    cwd = os.getcwd()
    logger.debug("Searching cwd=%s for an scord log file", cwd)
    fils = []
    for fil in os.listdir(cwd):
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
# @click.option('--log-file', type=str, default=None, help="The scord log file. If unset will search PWD for the most recent option")
@click.option('--out-file', type=click.File('w'), default=None, help="Where to write the runbook file")
@click.pass_context
def generate(ctx, out_file):
    # if not file:
    #     file = find_file()
    # scord_log = ScordLog.parse_file(file)
    scord_log = ctx.obj['scord_log']

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
@pass_context
def tag_previous(ctx, tag_str):
    """
    Tag the last command run with this string
    """
    if 'LAST_SCORD_ID' not in os.environ:
        raise ValueError("Can't find the last command, is shellcord initialized?")
    scord_id = os.environ['LAST_SCORD_ID']
    logger.debug("Tagging previous command %s with %s", scord_id, tag_str)

    t = Tag(scord_id=scord_id,
            tag_str=tag_str)

    fpath = ctx.obj.get('scord_log_path')
    logger.debug("Saving tag value %s in logfile %s", t, fpath)
    t.dump(fname=fpath)


if __name__ == '__main__':
    cli(obj={})
