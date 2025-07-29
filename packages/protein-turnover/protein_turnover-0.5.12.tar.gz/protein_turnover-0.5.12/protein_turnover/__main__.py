from __future__ import annotations

from . import background_ui  # noqa:
from . import pymz_ui  # noqa:
from . import web_ui  # noqa:
from .cli import cli
from .sqla import iso_peaks_ui  # noqa:

# pylint: disable=unused-import


# REM: imports should *not* import scipy,pandas,numpy!!!! Just click and .cli
# and a few system modules os, sys, typing... BE CAREFUL! otherwise load
# times might slow user interaction.

if __name__ == "__main__":
    cli.main(prog_name="turnover")
