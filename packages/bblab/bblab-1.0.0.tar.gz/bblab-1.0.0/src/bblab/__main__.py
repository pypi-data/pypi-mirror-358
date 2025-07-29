"""BitByteLab — Brewing Magic in Code & Logic!.

📌 Description:
    `bblab` - A namespace for BitByteLab libraries, tools, scripts, and utilities.

    It does not contain any functional logic beyond branding and identification.

    This is a bootstrap file created to reserve the `bblab` name as a namespace
    package. It allows future submodules like `bblab.cli`, `bblab.utils`, `bblab.ai`,
    and others to coexist under a unified namespace in the BitByteLab ecosystem,
    following modern Python packaging practices.

🛠️ Usage:
    This module is not intended to be used directly. It serves only for namespace
    registration and branding display when executed as a standalone script.

📜 Contents:
    - Project metadata (title, version, license, URL)
    - Terminal banner function
    - Metadata extraction from importlib
    - Execution banner for CLI usage

📎 Notes:
    To extend the namespace with actual logic or utilities, create a properly
    structured submodule or namespace package under `bblab/`.

📣 Example:
    Run directly via:
        python -m bblab

    Expected Output:
        A pretty terminal banner displaying project info.


📦 Project       : bblab (BitByteLab Namespace Package)
📜 License       : MIT
──────────────────────────────────────────────────────────────
🏢 Organization  : BitByteLab Pvt Ltd
🌍 Website       : https://bitbytelab.github.io/
🐙 GitHub        : https://github.com/bitbytelab/
📦 PyPI          : https://pypi.org/project/bblab/
──────────────────────────────────────────────────────────────
👨‍💻 Author        : Mahmudul Hasan Rasel
🐙 GitHub        : https://github.com/bitbytelab/bblab
💼 LinkedIn      : https://www.linkedin.com/in/rsmahmud
🧳 Portfolio     : https://rsmahmud.github.io/
──────────────────────────────────────────────────────────────
"""

import shutil
from importlib import metadata

try:
    __meta__ = metadata.metadata(__package__ or __name__)
    __version__ = metadata.version(__package__ or __name__) or "0.0.0"
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"
    __meta__ = {}

__project__ = "BitByteLab"
__title____ = ""
__caption__ = "Brewing Magic in Code & Logic"
__license__ = __meta__.get("License", "MIT")
__url______ = "https://github.com/bitbytelab/bblab"
__copyright = "2025 BitByteLab"

__ = ASCII_LOGO = {}
__["slant"] = r"""
    ____  _ __  ____        __       __          __
   / __ )(_) /_/ __ )__  __/ /____  / /   ____ _/ /_
  / __  / / __/ __  / / / / __/ _ \/ /   / __ `/ __ \
 / /_/ / / /_/ /_/ / /_/ / /_/  __/ /___/ /_/ / /_/ /
/_____/_/\__/_____/\__, /\__/\___/_____/\__,_/_.___/
                  /____/"""
__["standard"] = r"""
 ____  _ _   ____        _       _          _
| __ )(_) |_| __ ) _   _| |_ ___| |    __ _| |__
|  _ \| | __|  _ \| | | | __/ _ \ |   / _` | '_ \
| |_) | | |_| |_) | |_| | ||  __/ |__| (_| | |_) |
|____/|_|\__|____/ \__, |\__\___|_____\__,_|_.__/
                   |___/"""
__["big"] = r"""
 ____  _ _   ____        _       _           _
|  _ \(_) | |  _ \      | |     | |         | |
| |_) |_| |_| |_) |_   _| |_ ___| |     __ _| |__
|  _ <| | __|  _ <| | | | __/ _ \ |    / _` | '_ \
| |_) | | |_| |_) | |_| | ||  __/ |___| (_| | |_) |
|____/|_|\__|____/ \__, |\__\___|______\__,_|_.__/
                    __/ |
                   |___/"""
__["block"] = r"""
_|_|_|    _|    _|      _|_|_|                _|                _|                  _|
_|    _|      _|_|_|_|  _|    _|  _|    _|  _|_|_|_|    _|_|    _|          _|_|_|  _|_|_|
_|_|_|    _|    _|      _|_|_|    _|    _|    _|      _|_|_|_|  _|        _|    _|  _|    _|
_|    _|  _|    _|      _|    _|  _|    _|    _|      _|        _|        _|    _|  _|    _|
_|_|_|    _|      _|_|  _|_|_|      _|_|_|      _|_|    _|_|_|  _|_|_|_|    _|_|_|  _|_|_|
                                        _|
                                    _|_|"""
__["lean"] = r"""
    _/_/_/    _/    _/      _/_/_/                _/                _/                  _/
   _/    _/      _/_/_/_/  _/    _/  _/    _/  _/_/_/_/    _/_/    _/          _/_/_/  _/_/_/
  _/_/_/    _/    _/      _/_/_/    _/    _/    _/      _/_/_/_/  _/        _/    _/  _/    _/
 _/    _/  _/    _/      _/    _/  _/    _/    _/      _/        _/        _/    _/  _/    _/
_/_/_/    _/      _/_/  _/_/_/      _/_/_/      _/_/    _/_/_/  _/_/_/_/    _/_/_/  _/_/_/
                                       _/
                                  _/_/"""
__["block"] = r"""
_|_|_|    _|    _|      _|_|_|                _|                _|                  _|
_|    _|      _|_|_|_|  _|    _|  _|    _|  _|_|_|_|    _|_|    _|          _|_|_|  _|_|_|
_|_|_|    _|    _|      _|_|_|    _|    _|    _|      _|_|_|_|  _|        _|    _|  _|    _|
_|    _|  _|    _|      _|    _|  _|    _|    _|      _|        _|        _|    _|  _|    _|
_|_|_|    _|      _|_|  _|_|_|      _|_|_|      _|_|    _|_|_|  _|_|_|_|    _|_|_|  _|_|_|
                                        _|
                                    _|_|"""
__["bubble"] = r"""
  _   _   _   _   _   _   _   _   _   _
 / \ / \ / \ / \ / \ / \ / \ / \ / \ / \
( B | i | t | B | y | t | e | L | a | b )
 \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/
"""
__["mini"] = r"""
 _      _
|_)o_|_|_) _|_ _ |  _.|_
|_)| |_|_)\/|_(/_|_(_||_)
          /"""
__["script"] = r"""
 , __       , __                 _         _
/|/  \o    /|/  \             \_|_)       | |
 | __/  _|_ | __/     _|_  _    |     __, | |
 |   \|  |  |   \|   | |  |/   _|    /  | |/ \_
 |(__/|_/|_/|(__/ \_/|/|_/|__/(/\___/\_/|_/\_/
                    /|
                    \|"""
__["shadow"] = r"""
 __ ) _) |   __ )        |        |           |
 __ \  | __| __ \  |   | __|  _ \ |      _` | __ \
 |   | | |   |   | |   | |    __/ |     (   | |   |
____/ _|\__|____/ \__, |\__|\___|_____|\__,_|_.__/
                  ____/"""


def banner() -> None:  # noqa: D103
    terminal_size = shutil.get_terminal_size(fallback=(80, 24))
    w = min(terminal_size.columns, 80) - 2
    # fmt: off
    print("\n"
        f"+{'~~~~~~~~~~~~~~~~~~~~~~~~~~~~':{'~'}^{w}}+\n"
        f"│{__title____ + '' + __project__:{' '}^{w}}│\n"
        f"│{'    ' + __caption__ + '     ':{' '}^{w}}│\n"
        f"+{('~' * (len(__caption__) + 2)):{' '}^{w}}+\n"
        f"│{'  Version :  v' + __version__:{' '}^{w}}│\n"
        f"│{'  Copyright © ' + __copyright:{' '}^{w}}│\n"
        f"+{'~~~~~~~~~~~~~~~~~~~~~~~~~~~~':{'~'}^{w}}+\n",
    )


if __name__ == "__main__":
    banner()
