#!/usr/bin/env python3
import logging

from shellcord.cli import cli

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def main():
    cli()


if __name__ == '__main__':
    main()
