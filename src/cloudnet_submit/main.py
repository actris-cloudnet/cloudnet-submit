from .cfg import get_config
from .utils import get_submissions


def main() -> None:
    config = get_config()
    submissions = get_submissions(config)
    for sub in sorted(submissions):
        if not config.dry_run:
            sub.submit()
        else:
            sub.dry_run()


if __name__ == "__main__":
    main()
