from mjkit.utiles.get_logger import logging

class AttributePrinterMixin:
    """
    공개된 인스턴스 속성(언더스코어로 시작하지 않는)을 문자열로 포맷팅하여 출력하는 기능을 제공하는 믹스인 클래스입니다.

    주요 기능:
    - 인스턴스 변수 중 공개된 속성을 문자열 목록으로 반환
    - None 값, 예외 처리, 출력 길이 제한 지원
    - 로거가 있으면 로거를 통해 출력, 없으면 기본 로거를 생성하여 출력

    Example:
        ```python
        class MyClass(AttributePrinterMixin):
            def __init__(self):
                self.name = "Example"
                self.count = 42
                self.data = [1, 2, 3]
                self.print_public_attributes()

        obj = MyClass()
        # 출력 예시 (logger 또는 콘솔):
        # <MyClass> 초기화 완료, 초기화된 속성:
        #   - name = 'Example'
        #   - count = 42
        #   - data = [1, 2, 3]
        ```
    """

    def get_public_attributes_str(self) -> str:
        """
        인스턴스 변수 중 `_`로 시작하지 않는 속성들을 문자열로 반환합니다.
        - 속성 접근 중 예외가 발생하면 오류 내용을 출력합니다.
        - 값이 None이면 'None'으로 출력됩니다.
        - repr 문자열이 100자 초과 시 축약 표시(...)를 덧붙입니다.

        Returns:
            str: "<클래스명> 초기화 완료, 초기화된 속성:" 다음 줄부터
                 "  - key = value" 형식의 속성 문자열 목록
        """
        lines = [f"<{self.__class__.__name__}> 초기화 완료, 초기화된 속성:"]
        for key in self._get_public_attribute_keys():
            lines.append(self._format_attribute_line(key))
        return "\n".join(lines)

    def _get_public_attribute_keys(self) -> list[str]:
        """
        인스턴스 딕셔너리에서 언더스코어로 시작하지 않는 공개 속성 키 리스트를 반환합니다.

        Returns:
            list[str]: 공개 속성 키 목록
        """
        return [key for key in self.__dict__ if not key.startswith("_")]

    def _format_attribute_line(self, key: str) -> str:
        """
        단일 속성 키에 대해 '  - key = value' 형식의 문자열을 반환합니다.
        - 속성 접근 중 예외 발생 시 예외 메시지를 포함해 반환합니다.

        Args:
            key (str): 출력할 속성명

        Returns:
            str: 포맷팅된 속성 문자열 (예: "  - a = 123")
        """
        try:
            value = self.__dict__[key]
            display_value = self._format_value(value)
        except Exception as e:
            display_value = f"<오류: {type(e).__name__}: {e}>"
        return f"  - {key} = {display_value}"

    def _format_value(self, value: object) -> str:
        """
        값에 대해 다음 처리를 수행합니다:
        - None 값은 "None" 문자열로 변환
        - repr() 문자열로 변환
        - 100자 초과 시 앞 100자만 표시 후 "..." 추가

        Args:
            value (object): 속성 값

        Returns:
            str: 안전하게 포맷된 문자열 값
        """
        if value is None:
            return "None"
        safe_repr = repr(value)
        if len(safe_repr) > 100:
            safe_repr = safe_repr[:100] + "..."
        return safe_repr

    def print_public_attributes(self) -> None:
        """
        get_public_attributes_str()로 속성 문자열을 얻은 뒤,
        인스턴스에 logger가 있으면 logger.info()로 출력하고, 없으면 기본 logger를 생성해 출력합니다.
        """
        attr_str = self.get_public_attributes_str()

        if hasattr(self, "logger") and isinstance(self.logger, logging.Logger):
            self.logger.info(attr_str)
        else:
            print(f"⚠️ Warning: {self.__class__.__name__}에 logger가 없습니다. 기본 로거를 사용합니다.")


if __name__ == "__main__":
    class ExampleClass(AttributePrinterMixin):
        def __init__(self, a: int, b: str):
            self.a = a
            self.b = b
            self.c = [1, 2, 3]
            self.print_public_attributes()

    example = ExampleClass(10, "test")
    example.print_public_attributes()
