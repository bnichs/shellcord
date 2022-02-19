from pprint import pprint

from shellcord.scord import Command, ScordID


def test_convert_scorid():
    sid = "scord-123-456"
    assert str(ScordID.from_str(sid)) == sid


def test_convert_command():
    cmd = Command(cmd="echo foo",
                  scord_id="scord-123-456",
                  exit_code=1
                  )

    d = cmd.to_dict()
    assert Command.from_dict(d) == cmd