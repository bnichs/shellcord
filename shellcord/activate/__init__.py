# from __future__ import absolute_import, unicode_literals
import os.path


script = "shellcord/activate/init.sh"


def main():
    path = os.path.abspath(script)
    print(path)


if __name__ == '__main__':
    main()
