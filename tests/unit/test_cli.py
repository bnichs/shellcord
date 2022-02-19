import logging
import os
import shutil
from pathlib import Path
from unittest import mock
from uuid import uuid4

import tempfile
from click.testing import CliRunner, Result

from shellcord.cli import cli


TEST_LOG = "tests/scord_logs/scord-log-normal.json"

KILL_TEMP_FILES = False


logger = logging.getLogger(__name__)


class TestCli(object):
    def setup_method(self, method):
        self.runner = CliRunner()
        self.tempdir = Path(tempfile.mkdtemp())
        logger.debug("Using tempdir %s", self.tempdir)
        self.scord_log_path = self.tempdir / "scord-log.json"

        # Setup and scord log
        logger.debug("Using scord log %s copied from %s", self.scord_log_path, TEST_LOG)
        with open(self.scord_log_path, 'w') as f_out:
            with open(TEST_LOG, 'r') as f_in:
                f_out.write(f_in.read())

    def teardown_method(self, method):
        if KILL_TEMP_FILES:
            shutil.rmtree(self.tempdir)

    def load_file_text(self, fname) -> str:
        with open(fname) as f:
            return f.read()

    def check_result(self, result: Result, expect_code=0):
        try:
            assert result.exit_code == expect_code
        except AssertionError as e:
            print(f"Got  bad exit code {result.exit_code}. Stdout/err:")
            print(result.stdout)
            raise e

    def test_hhelp(self):
        result = self.runner.invoke(cli, ['-h'])
        self.check_result(result)

    def test_help(self):
        result = self.runner.invoke(cli, ['--help'])
        self.check_result(result)

    def test_generate(self):
        result = self.runner.invoke(cli, [
            '--log-file',
            self.scord_log_path,
            'generate',
        ]
                                    )
        self.check_result(result)

    def test_generate_with_find_file(self):
        # Ensure pwd has a log file in it
        pwd_log_path = "./scord-log-test.json"
        shutil.copy(self.scord_log_path, pwd_log_path)

        result = self.runner.invoke(cli, [
            'generate',
        ]
                                    )
        self.check_result(result)

    def test_generate_bad_log_file(self):
        bad_logfile = os.path.join(".", str(uuid4()))
        result = self.runner.invoke(cli, [
            '--log-file',
            bad_logfile,
            'generate',
        ]
                                    )
        self.check_result(result, expect_code=1)

    def test_tag_previous(self):
        log_text_orig = self.load_file_text(self.scord_log_path)
        tag_str = str(uuid4())
        scord_id = str(uuid4())

        assert tag_str not in log_text_orig
        assert scord_id not in log_text_orig

        env = {}
        env["LAST_SCORD_ID"] = scord_id

        result = self.runner.invoke(cli, [
            '--log-file',
            self.scord_log_path,
            'tag', 'previous',
            tag_str
        ],
                                    env=env,
                                    )
        self.check_result(result)

        log_text_new = self.load_file_text(self.scord_log_path)

        assert len(log_text_new) > len(log_text_orig)
        assert tag_str in log_text_new
        assert scord_id in log_text_new
