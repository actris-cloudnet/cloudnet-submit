from .cfg import get_config
from .utils import get_submissions


def main() -> None:
    config = get_config()
    submissions = get_submissions(config)
    for s in sorted(submissions):
        if not config.dry_run:
            s.submit()
        else:
            s.dry_run()


if __name__ == "__main__":
    main()
