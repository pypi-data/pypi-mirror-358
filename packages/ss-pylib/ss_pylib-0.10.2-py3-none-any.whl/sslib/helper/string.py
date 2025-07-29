from datetime import datetime
from stringcase import camelcase


class StringHelper:

    @staticmethod
    def to_bool(source: str) -> bool:
        return source.lower() in ('true', '1', 'yes', 'y')

    @staticmethod
    def camel_case(source: str) -> str:
        return camelcase(source)

    @staticmethod
    def datetime_or_none(source: datetime) -> str | None:
        return source.strftime('%Y-%m-%d %H:%M:%S') if source is not None else None
