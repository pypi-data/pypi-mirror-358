# Copyright © 2021 Maxime “pep” Buquet <pep@bouah.net>
# Copyright © 2025 Tim “Syndace” Henkes <me@syndace.dev>
#
# Distributed under terms of the GPLv3 license.

import argparse
import os

try:
    from poezio.xdg import DATA_HOME
except ImportError:
    from poezio.libpoezio import XDG  # pylint: disable=import-error,no-name-in-module
    DATA_HOME = XDG.data_dir

from slixmpp import JID

from .core import encode_jid_for_path


__all__ = [
    "main"
]


def main() -> None:
    # Note: This is intentionally not documented as to not encourage accessing the OMEMO data, which can lead
    # to broken sessions. Especially backup/restore of the state is explicitly forbidden as per the OMEMO
    # specificiation as it _guarantees_ breakage. This is mainly intended for developers.
    parser = argparse.ArgumentParser(
        prog="poezio-omemo",
        description="Convert a JID to its representation on the file system in poezio-omemo's storage format."
    )

    parser.add_argument("JID", type=str, help="The JID to convert.")

    args = parser.parse_args()

    print(encode_jid_for_path(JID(args.JID)))
    print(f"Storage location: {os.path.join(DATA_HOME, "omemo")}")


if __name__ == "__main__":
    main()
