import re

def camel_to_snake(name: str) -> str:
    """
    CamelCase 문자열을 snake_case 문자열로 변환합니다.

    예시:
        - "MyClassName" -> "my_class_name"
        - "JSONResponseHandler" -> "json_response_handler"
        - "HTTPRequest2Handler" -> "http_request2_handler"

    동작 원리:
        1. 첫 번째 re.sub:
           - 앞이 소문자/숫자이고 뒤가 대문자+소문자 조합이면 언더스코어 삽입
           - 예: "MyClass" → "My_Class"
        2. 두 번째 re.sub:
           - 앞이 소문자/숫자이고 뒤가 대문자이면 언더스코어 삽입
           - 예: "HTTP2Handler" → "HTTP2_Handler"
        3. 전체 소문자로 변환하여 snake_case 완성

    Args:
        name (str): 변환할 CamelCase 문자열

    Returns:
        str: snake_case 형태의 문자열
    """
    # 대문자 앞에 언더스코어 삽입
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()

# 예제 실행
if __name__ == "__main__":
    examples = [
        "CamelCase",
        "MyClassName",
        "HTTPRequest2Handler",
        "JSONResponseHandler",
        "VolatilityOptimizer",
        "XGBoostModelV2"
    ]

    for example in examples:
        converted = camel_to_snake(example)
        print(f"{example} -> {converted}")
