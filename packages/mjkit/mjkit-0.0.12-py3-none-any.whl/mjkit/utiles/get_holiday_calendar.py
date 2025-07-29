from functools import lru_cache
import holidays

@lru_cache(maxsize=None)
def get_holiday_calendar(years: tuple, country: str = "kr") -> holidays.HolidayBase:
    """
    주어진 연도들에 해당하는 특정 국가의 공휴일 캘린더를 반환합니다.
    반환된 공휴일 캘린더 객체는 'in' 연산자를 사용해 특정 날짜가 공휴일인지 쉽게
    확인할 수 있습니다. 이 함수는 호출 결과를 메모리에 캐시하여 동일한 인자에 대해
    반복 계산을 방지합니다.

    Args:
        years (tuple): 공휴일을 조회할 연도들의 튜플 (예: (2023, 2024))
        country (str, optional): 국가 코드 (기본값: "kr" - 대한민국)
            ISO 3166-1 alpha-2 국가 코드를 사용합니다. 대소문자 구분 없이 입력 가능.

    Returns:
        holidays.HolidayBase: 해당 연도 및 국가에 대한 공휴일 캘린더 객체

    Example:
        >>> calendar = get_holiday_calendar((2023, 2024), country="kr")
        >>> print("2023-01-01" in calendar)
        True  # 새해 첫날
        >>> print("2024-10-03" in calendar)
        True  # 개천절
    """
    return holidays.country_holidays(country=country.upper(), years=list(years))


if __name__ == "__main__":
    # 예시: 2023년과 2024년의 한국 공휴일 캘린더를 가져오기
    calendar = get_holiday_calendar((2023, 2024), country="kr")
    print(calendar)
    print("2023-01-01" in calendar)  # True, 새해 첫날
    print("2024-10-03" in calendar)  # True, 개천절