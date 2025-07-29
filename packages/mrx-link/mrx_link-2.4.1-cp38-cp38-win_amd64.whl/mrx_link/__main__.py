#  MAKINAROCKS CONFIDENTIAL
#  ________________________
#
#  [2017] - [2022] MakinaRocks Co., Ltd.
#  All Rights Reserved.
#
#  NOTICE:  All information contained herein is, and remains
#  the property of MakinaRocks Co., Ltd. and its suppliers, if any.
#  The intellectual and technical concepts contained herein are
#  proprietary to MakinaRocks Co., Ltd. and its suppliers and may be
#  covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law. Dissemination
#  of this information or reproduction of this material is
#  strictly forbidden unless prior written permission is obtained
#  from MakinaRocks Co., Ltd.
#
import sys
from multiprocessing import freeze_support

from .cli import mrx_link_cli


def main() -> int:
    """Run mrx-link CLI commands."""
    try:
        mrx_link_cli()
        return 0
    except (Exception, KeyboardInterrupt) as exp:  # pylint: disable=broad-except
        print(str(exp), file=sys.stderr)
        return 1


if __name__ == "__main__":
    freeze_support()
    sys.exit(main())
