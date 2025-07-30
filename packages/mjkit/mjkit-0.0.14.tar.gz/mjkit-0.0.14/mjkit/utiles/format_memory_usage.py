
import psutil
def format_memory_usage(
    mem_bytes: int=psutil.Process().memory_info().rss,
    threshold_warning_emoji: int = 3
) -> str:
    """
    메모리 바이트를 읽기 쉬운 형식으로 변환

    Args:
        mem_bytes (int): 메모리 바이트 수
        threshold_warning_emoji (int): GB 단위 경고 임계값 (예: 3이면 3GB 이상 시 경고 이모지)

    Returns:
        str: 형식화된 메모리 사용량 문자열 (예: '⚠️2.43 GB')
    """
    threshold_warning = threshold_warning_emoji * 1024  # 3GB → 3072MB
    mem_mb = mem_bytes / (1024 * 1024)

    is_warning = mem_mb > threshold_warning
    if mem_mb > 1024:
        mem_value = mem_mb / 1024
        unit = "GB"
    else:
        mem_value = mem_mb
        unit = "MB"

    warning_icon = "⚠️" if is_warning else ""
    return f"{warning_icon}{mem_value:.2f} {unit}"


if __name__ == "__main__":
    # 예시 사용
    mem_usage = format_memory_usage()
    print(f"현재 메모리 사용량: {mem_usage}")

    # 특정 메모리 바이트 수로 테스트
    test_mem_bytes = 4 * 1024 * 1024 * 1024  # 4GB
    formatted_usage = format_memory_usage(test_mem_bytes)
    print(f"테스트 메모리 사용량: {formatted_usage}")