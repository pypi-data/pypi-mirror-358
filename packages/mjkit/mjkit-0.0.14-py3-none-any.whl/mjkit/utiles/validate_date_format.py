import re

def validate_date_format(date: str, sep: str = ".") -> None:
    """
    날짜 문자열이 지정된 구분자를 기준으로 "YYYY{sep}MM{sep}DD" 형식인지 확인합니다.

    Example:
        validate_date_format("2025.05.30")  # OK
        validate_date_format("2025-05-30", sep='-')  # OK
        validate_date_format("2025 05 30", sep=' ')  # OK
        validate_date_format("2025/05/30", sep='/')  # OK

        try:
            validate_date_format("2025.5.30")  # ❌ 예외 발생
        except Exception as e:
            print(f"오류발생: {e}")

        try:
            validate_date_format("2025.05-30", sep='.')  # ❌ 예외 발생
        except Exception as e:
            print(f"오류발생 2 : {e}")


    :param date: 검사할 날짜 문자열
    :param sep: 구분자 문자 (예: '.', '-', '/', ' ')
    :raises ValueError: 형식이 맞지 않을 경우 예외 발생
    """
    # 정규표현식에서 특수문자는 escape 필요하므로 처리
    escaped_sep = re.escape(sep)
    pattern = rf"^\d{{4}}{escaped_sep}\d{{2}}{escaped_sep}\d{{2}}$"

    if not re.match(pattern, date):
        raise ValueError(
            f"날짜 형식이 잘못되었습니다: '{date}' (예: 2025{sep}05{sep}30 형식이어야 함)"
        )


if __name__ == "__main__":
    # 테스트용 코드
    validate_date_format("2025.05.30")  # OK
    validate_date_format("2025-05-30", sep="-")  # OK
    validate_date_format("2025 05 30", sep=" ")  # OK
    validate_date_format("2025/05/30", sep="/")  # OK

    try:
        validate_date_format("2025.5.30")  # ❌ 예외 발생
    except Exception as e:
        print(f"오류발생: {e}")

    try:
        validate_date_format("2025.05-30", sep=".")  # ❌ 예외 발생
    except Exception as e:
        print(f"오류발생 2 : {e}")