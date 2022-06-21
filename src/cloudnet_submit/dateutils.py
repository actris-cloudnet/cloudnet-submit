import datetime


def date_parser(date_str: str) -> datetime.date:
    return datetime.date.fromisoformat(date_str)
