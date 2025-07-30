import re
from typing import List


def extract_delimited_blocks(text: str, sep: str) -> List[str]:
    """
    주어진 문자열(text)에서 sep 문자열로 둘러싸인 블록들을 모두 찾아
    sep을 포함한 형태로 리스트로 반환합니다.

    Example:
        blob =

            ```
            첫 번째 triple backtick 블록입니다.
            여러 줄이 들어올 수 있습니다.
            ```

            ```text
            두 번째 블록: 언어 태그가 'text'인 예시입니다.
            ```

            <<<CUSTOM>>>
            커스텀 구분자로 둘러싸인 블록.
            여러 줄을 포함해도 됩니다.
            <<<CUSTOM>>>

            # triple backtick 블록 추출
            backtick_blocks = extract_delimited_blocks(blob, sep="```")
            for i, block in enumerate(backtick_blocks, start=1):
                print(f"--- Backtick Block {i} ---")
                print(block)
                print()

            # 커스텀 구분자 블록 추출
            custom_blocks = extract_delimited_blocks(blob, sep="<<<CUSTOM>>>")
            for i, block in enumerate(custom_blocks, start=1):
                print(f"--- Custom Block {i} ---")
                print(block)
                print()

    :param text: 블록을 포함할 수 있는 긴 문자열
    :param sep: 블록 구분자로 사용할 문자열 (예: "```", "<<<", "~~~" 등)
    :return: sep으로 둘러싸인 블록 전체(구분자 포함)를 요소로 갖는 문자열 리스트.
             블록이 없으면 빈 리스트 반환.
    """
    # sep을 정규표현식 특수문자로부터 보호
    esc_sep = re.escape(sep)
    # 패턴: sep으로 시작, 그 뒤에 비어 있든 언어 태그가 있든 무시하고 개행,
    #       내용(공백 포함)을 non-greedy로 캡처, 마지막에 다시 sep으로 종료
    pattern = rf"{esc_sep}(?:[^\n]*\n)?[\s\S]*?{esc_sep}"

    # 매칭되는 모든 블록을 찾아 리스트로 반환
    return re.findall(pattern, text)


# ─────────────────────────────────────────────────────────────
# 사용 예시
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    blob = """
    ```
    첫 번째 triple backtick 블록입니다.
    여러 줄이 들어올 수 있습니다.
    ```

    ```text
    두 번째 블록: 언어 태그가 'text'인 예시입니다.
    ```

    <<<CUSTOM>>>
    커스텀 구분자로 둘러싸인 블록.
    여러 줄을 포함해도 됩니다.
    <<<CUSTOM>>>
    """

    # triple backtick 블록 추출
    backtick_blocks = extract_delimited_blocks(blob, sep="```")
    for i, block in enumerate(backtick_blocks, start=1):
        print(f"--- Backtick Block {i} ---")
        print(block)
        print()

    # 커스텀 구분자 블록 추출
    custom_blocks = extract_delimited_blocks(blob, sep="<<<CUSTOM>>>")
    for i, block in enumerate(custom_blocks, start=1):
        print(f"--- Custom Block {i} ---")
        print(block)
        print()
