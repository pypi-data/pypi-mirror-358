# LS ELECTRIC / AX / AX Lab – Indexing Pipeline
이 프로젝트는 RAG(Retrieval-Augmented Generation) 기반 시스템에서 사용할 벡터스토어(Vectorstore)를 생성하는 인덱싱 파이프라인입니다.
PDF 문서를 입력으로 받아 이미지 변환, 텍스트 추출, 문서 청킹, 임베딩 처리까지 자동화된 일련의 프로세스를 제공합니다.

## 주요 기능
- [x] [PDF -> PNG] PDF 문서의 고해상도 이미지(PNG) 변환
- [ ] OCR 및 Markdown 변환
- [ ] 계층적 문서 청킹 및 메타데이터 태깅
- [ ] 임베딩 및 Vector DB 저장

## 예시
### PDF -> PNG 변환
```python
from lse_indexing_pipeline import convert_pdf_to_png

if __name__ == "__main__":
    convert_pdf_to_png(
        input_file_path="{your_pdf_path}",
        output_folder_dir="{your_output_dir}",
    )
```