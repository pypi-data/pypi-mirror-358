import re
from datetime import date, datetime
from typing import Optional

_DEFAULT_DATE_FORMAT_ = '%Y-%m-%d'

# 날짜 찾는 정규식 미리 컴파일
_DATE_EXTRACTOR_ = re.compile(r'(\d{4})[\s년/.-]*(\d{1,2})[\s월/.-]*(\d{1,2})[\s일]*')


class DatetimeUtil:
    @staticmethod
    def format_date(src: str, date_format: str = _DEFAULT_DATE_FORMAT_) -> Optional[str]:
        '''문자열 날짜를 형식화된(기본:YYYY-MM-DD) 문자열로 변경'''
        if not src:
            return None

        match = _DATE_EXTRACTOR_.search(src)
        if not match:
            return None

        try:
            # 정수 변환 후 datetime 객체 생성하면 자동으로 제로 패딩 적용
            year, month, day = map(int, match.groups())
            dt = datetime(year=year, month=month, day=day)
        except ValueError:
            return None

        return dt.strftime(date_format)

    @staticmethod
    def to_date(src: str, date_format: str = _DEFAULT_DATE_FORMAT_) -> date:
        '''문자열 날짜(기본:YYYY-MM-DD)를 date 객체로 응답'''
        return datetime.strptime(src, date_format).date()

    @staticmethod
    def to_date_or_none(src: Optional[str], date_format: str = _DEFAULT_DATE_FORMAT_) -> Optional[date]:
        return DatetimeUtil.to_date(src, date_format=date_format) if src else None


if __name__ == '__main__':
    TEST_DATE = '1976년1월20일'
    print(DatetimeUtil.format_date(src=TEST_DATE, date_format='%Y/%m/%d'))
    print(DatetimeUtil.to_date('1976-01-20'))
