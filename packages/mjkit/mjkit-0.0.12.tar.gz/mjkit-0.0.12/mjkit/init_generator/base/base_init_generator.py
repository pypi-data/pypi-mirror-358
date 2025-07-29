from mjkit.init_generator.interfaces.abstract_init_generator import AbstractInitGeneratorBase

class BaseInitGenerator(AbstractInitGeneratorBase):
    """
    BaseInitGenerator는 AbstractInitGeneratorBase의 기본 구현체입니다.

    이 클래스는 추상 메서드들을 구현한 후,
    외부에서 호출할 수 있는 단일 실행 함수인 run()을 제공합니다.

    주로 walk_packages 메서드를 통해 지정한 루트 디렉토리 내의 모든 패키지를 순회하며
    __init__.py 자동 생성 작업을 수행합니다.
    """

    def run(self):
        """
        자동 __init__.py 생성 작업을 시작하는 단일 진입 함수

        보통 외부에서 이 메서드만 호출하면 내부적으로
        루트 디렉토리부터 하위 패키지까지 순회하며 __init__.py 파일을 생성합니다.

        이 메서드는 AbstractInitGeneratorBase에서 정의한 run() 추상 메서드를 구현한 것으로,
        내부적으로 walk_packages()를 호출합니다.

        Example:
            ```python
            # BaseInitGenerator 사용 예시
            generator = BaseInitGenerator(root_dir="/path/to/project/mjkit")
            generator.run()  # 지정된 root_dir부터 시작해 모든 하위 패키지를 순회하며 __init__.py 생성
            ```
        """
        self._walk_packages()
