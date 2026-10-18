"""Точка входа: python -m fruit [команды] | tray.

  python -m fruit save <имя>       — CLI-режим (см. fruit.cli)
  python -m fruit tray             — режим трея с иконкой и хоткеями
"""

import sys


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "tray":
        from . import tray
        tray.run()
        return 0
    from . import cli
    return cli.main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
