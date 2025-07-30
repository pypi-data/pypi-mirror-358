import pickle
from typing import Any
import os

def save_pickle(obj: Any, path: str) -> None:
    """
    객체를 pickle 파일로 저장합니다.

    Args:
        obj (Any): 저장할 Python 객체 (예: dict, list, 사용자 정의 클래스 등)
        path (str): 저장할 파일의 경로. '.pkl' 확장자를 사용하는 것이 일반적입니다.

    Raises:
        IOError: 파일을 열거나 쓸 수 없는 경우
        pickle.PickleError: 객체를 직렬화하는 데 실패한 경우

    Example:
        >>> data = {"a": 1, "b": [1, 2, 3]}
        >>> save_pickle(data, "data.pkl")
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(obj, f)
    except (IOError, pickle.PickleError) as e:
        raise RuntimeError(f"[save_pickle] 파일 저장 실패: {e}")

def load_pickle(path: str) -> Any:
    """
    pickle 파일에서 객체를 로드합니다.

    Args:
        path (str): 불러올 pickle 파일 경로

    Returns:
        Any: 역직렬화된 Python 객체

    Raises:
        FileNotFoundError: 지정한 파일이 존재하지 않는 경우
        IOError: 파일을 열 수 없는 경우
        pickle.PickleError: 파일이 올바른 pickle 형식이 아니거나 역직렬화 실패 시

    Example:
        >>> obj = load_pickle("data.pkl")
        >>> print(obj)
    """
    try:
        with open(path, "rb") as f:
            obj = pickle.load(f)
        return obj
    except FileNotFoundError:
        raise FileNotFoundError(f"[load_pickle] 파일이 존재하지 않습니다: {path}")
    except (IOError, pickle.PickleError) as e:
        raise RuntimeError(f"[load_pickle] 파일 로드 실패: {e}")

if __name__ == "__main__":
    # 예시 객체
    sample_data = {
        "name": "mr carbonic",
        "scores": [95.5, 88.0, 76.5],
        "active": True
    }

    # 파일 경로
    file_path = "sample.pkl"

    # 저장 예제
    try:
        save_pickle(sample_data, file_path)
        print(f"✅ 객체 저장 성공: {file_path}")
    except Exception as e:
        print(f"❌ 저장 오류: {e}")

    # 불러오기 예제
    try:
        loaded_data = load_pickle(file_path)
        print("✅ 객체 로드 성공:", loaded_data)
    except Exception as e:
        print(f"❌ 로드 오류: {e}")