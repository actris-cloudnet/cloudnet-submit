import sys

from .cfg import get_config
from .utils import get_submissions, print_summary


def main() -> None:
    config = get_config()
    submissions = get_submissions(config)
    failure = False
    for sub in sorted(submissions):
        if not config.dry_run:
            sub.submit()
            if not sub.status.metadata_ok or not sub.status.data_ok:
                failure = True
        else:
            sub.dry_run()
    print_summary(submissions, config.dry_run)
    if failure:
        sys.exit(1)


if __name__ == "__main__":
    main()
