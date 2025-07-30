from abc import ABC, abstractmethod
from mjkit.mixin import LoggingMixin, AttributePrinterMixin
import logging

class AbstractInitGeneratorBase(ABC, LoggingMixin, AttributePrinterMixin):
    """
    추상 클래스: __init__.py 자동 생성기를 위한 베이스 클래스

    이 클래스는 주어진 루트 디렉토리 내에서 하위 패키지를 순회하며,
    각 패키지 폴더에 대해 __init__.py 파일을 생성하는 기능을 추상화합니다.

    LoggingMixin과 AttributePrinterMixin을 상속받아
    로깅 기능 및 객체 상태 출력 기능을 제공합니다.

    하위 클래스는 다음 추상 메서드를 반드시 구현해야 합니다:
    - extract_symbols_from_file: 단일 파이썬 파일에서 export할 심볼(클래스, 함수 등) 추출
    - process_package: 단일 패키지 폴더에서 __init__.py 생성 로직 구현
    - walk_packages: 루트 디렉토리부터 하위 모든 패키지 순회 로직 구현
    - run: 외부에서 호출하는 단일 실행 함수 구현
    """

    def __init__(self, root_dir: str, log_level: int = logging.INFO):
        """
        초기화

        Args:
            root_dir (str): 자동 __init__.py 생성을 시작할 최상위 루트 디렉토리 경로
            log_level (int): 로깅 레벨 (기본값: logging.INFO)
        """
        super().__init__(level=log_level)
        self.root_dir = root_dir
        self.logger.info(f"InitGenerator 시작, root_dir={root_dir}")

    @abstractmethod
    def _extract_symbols_from_file(self, filepath: str):
        """
        한 개의 파이썬 파일에서 export할 심볼(클래스, 함수, Enum 등)을 추출하는 추상 메서드

        Args:
            filepath (str): 심볼을 추출할 .py 파일의 절대 또는 상대 경로

        Returns:
            List[str]: 해당 파일에서 추출된 공개 심볼 이름 리스트
        """
        raise NotImplementedError(f"{self.__class__.__name__}는 추상 메서드 extract_symbols_from_file을 구현해야 합니다.")

    @abstractmethod
    def _process_package(self, package_dir: str):
        """
        단일 패키지 폴더 내에서 __init__.py 파일을 생성하는 추상 메서드

        Args:
            package_dir (str): __init__.py를 생성할 패키지 폴더 경로

        Returns:
            None
        """
        raise NotImplementedError(f"{self.__class__.__name__}는 추상 메서드 process_package을 구현해야 합니다.")

    @abstractmethod
    def _walk_packages(self):
        """
        루트 디렉토리부터 시작해 모든 하위 패키지를 재귀적으로 순회하며
        각 패키지 폴더에 대해 process_package를 호출하는 추상 메서드

        Returns:
            None
        """
        raise NotImplementedError(f"{self.__class__.__name__}는 추상 메서드 walk_packages을 구현해야 합니다.")

    def run(self):
        """
        외부에서 호출하는 단일 실행 함수

        일반적으로 walk_packages를 호출하도록 구현하며,
        하위 클래스에서 구체적인 실행 로직을 정의해야 합니다.

        Returns:
            None
        """
        # 실제 동작은 하위 클래스에서 구현
        raise NotImplementedError(f"{self.__class__.__name__}는 추상 메서드 run을 구현해야 합니다.")
