import logging
from typing import Optional
from mjkit.utiles.get_logger import get_logger

class LoggingMixin:
    """
    로깅 기능만을 담당하는 Mixin 클래스.

    이 클래스를 상속하면 self.logger 인스턴스를 사용할 수 있게 됩니다.
    다른 기능은 포함하지 않으며, 단일 책임 원칙을 따릅니다.
    """
    cls_logger = get_logger(__qualname__, logging.INFO)

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        level: int = logging.INFO,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.logger = logger or get_logger(self.__class__.__name__, level=level)
        self.logger.debug(f"Initializing {self.__class__.__name__} with logger level: {level}")


if __name__ == "__main__":
    # 예시: LoggingMixin 사용법
    class ExampleClass(LoggingMixin):
        def do_something(self):
            self.logger.info("Doing something in ExampleClass")

    example = ExampleClass()
    example.do_something()  # INFO 로그 출력