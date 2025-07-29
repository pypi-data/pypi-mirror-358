import logging
import traceback
from pathlib import Path

import fitz  # PyMuPDF
from tqdm import tqdm

from lse_indexing_pipeline.utils import timeit

logger = logging.getLogger(__name__)


def hello():
    pass


@timeit(label="PDF → PNG 변환 소요 시간")
def convert_pdf_to_png(
    input_file_path: str | Path,
    output_folder_dir: str | Path,
    dpi: int = 300,
    prefix: str = "page",
) -> None:
    """
    PDF 파일을 지정된 해상도(DPI)로 변환하여 각 페이지를 PNG 이미지로 저장합니다.

    입력된 PDF 파일의 각 페이지는 지정된 DPI 해상도로 렌더링되며,
    지정한 출력 폴더에 PNG 이미지로 저장됩니다.
    출력 파일명은 `{prefix}_###.png` 형식을 따르며, 전체 페이지 수에 따라
    자동으로 자리수를 계산하여 zero-padding이 적용됩니다.

    Args:
        input_file_path (str | Path): 변환할 PDF 파일 경로.
        output_folder_dir (str | Path): PNG 이미지가 저장될 디렉토리 경로.
        dpi (int, optional): 출력 이미지의 해상도(DPI). 기본값은 300으로, OCR 및 문서 시각화에 적합합니다.
        prefix (str, optional): 출력 이미지 파일명 접두어. 기본값은 "page"입니다.

    Notes:
        - 출력 폴더가 존재하지 않으면 자동으로 생성됩니다.
        - 출력 파일명은 페이지 수에 따라 zero-padding이 적용되어 정렬 및 가독성이 향상됩니다.
          예: 9페이지 문서는 'page_01.png' ~ 'page_09.png'로 저장됩니다.
        - 예외가 발생할 경우, 에러 메시지와 전체 스택 트레이스를 `logging.error` 수준으로 기록합니다.
          함수 내부에서 예외를 직접 발생시키지 않습니다.

    Example:
        >>> convert_pdf_to_png("보고서.pdf", "./이미지", dpi=200, prefix="scan")
        # 출력 예시: scan_01.png, scan_02.png, ...
    """
    # 한 자리 추가로 zero-padding 보정
    input_file_path = Path(input_file_path)
    output_folder_dir = Path(output_folder_dir)
    output_folder_dir.mkdir(parents=True, exist_ok=True)

    try:
        with fitz.open(input_file_path) as pdf_file:

            total_pages = len(pdf_file)

            # 한 자리 추가로 zero-padding 보정 (예: 1 → 01, 99 → 099)
            digit_count = len(str(total_pages)) + 1

            scale = dpi / 72
            matrix = fitz.Matrix(scale, scale)

            for i in tqdm(
                iterable=range(total_pages), desc="PDF → PNG 변환 진행중", unit="page"
            ):
                page = pdf_file.load_page(i)
                pix_map = page.get_pixmap(matrix=matrix)

                file_name = f"{prefix}_{str(i + 1).zfill(digit_count)}.png"
                output_path = output_folder_dir / file_name

                pix_map.save(output_path)

    except Exception:
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    convert_pdf_to_png(
        input_file_path="data/input/기계구조_NextEra_고객시방서원본_NEER MDCR-101-2024 R0.pdf",
        output_folder_dir="data/output",
    )
