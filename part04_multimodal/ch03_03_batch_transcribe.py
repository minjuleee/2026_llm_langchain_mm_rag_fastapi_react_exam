# 여러 개의 오디오 파일을 Whisper로 변환한 뒤 ChromaDB에 RAG용 문서로 저장합니다.
#
# 필요 패키지:
# pip install openai-whisper chromadb langchain-openai langchain-community python-dotenv

from pathlib import Path
import time

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
import whisper


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "waves"
PERSIST_DIR = BASE_DIR / "chroma_whisper_radio"
COLLECTION_NAME = "radio_transcripts"

MODEL_NAME = "base"
LANGUAGE = None  # "ko", "en"처럼 고정하거나 None으로 두면 자동 감지
EMBEDDING_MODEL = "text-embedding-3-small"
RESET_COLLECTION = True


def batch_transcribe(audio_dir: Path, model_name: str = "base") -> list[dict]:
    """
    폴더 안의 오디오 파일을 모두 변환합니다.
    모델을 한 번만 로드하고 재사용합니다.

    반환값 구조:
        [
            {
                "file": "radio_001.wav",
                "text": "전체 변환 텍스트",
                "language": "ko",
                "segments": [...]
            },
            ...
        ]
    """
    audio_files = [
        path
        for path in audio_dir.iterdir()
        if path.suffix.lower() in {".wav", ".mp3", ".mp4", ".m4a", ".flac"}
    ]

    if not audio_files:
        raise FileNotFoundError(f"오디오 파일이 없습니다: {audio_dir}")

    print(f"모델 로딩 중: {model_name}")
    model = whisper.load_model(model_name)
    print(f"변환 대상 파일: {len(audio_files)}개\n")

    results = []

    for audio_path in sorted(audio_files):
        print(f"변환 중: {audio_path.name}")
        start = time.time()

        transcribe_options = {
            "task": "transcribe",
            "fp16": False,
        }
        if LANGUAGE:
            transcribe_options["language"] = LANGUAGE

        result = model.transcribe(str(audio_path), **transcribe_options)

        elapsed = time.time() - start
        text = result["text"].strip()

        results.append(
            {
                "file": audio_path.name,
                "text": text,
                "language": result["language"],
                "segments": result["segments"],
            }
        )

        print(f"  완료: {elapsed:.1f}초")
        print(f"  내용: {text[:80]}\n")

    return results


def transcripts_to_documents(results: list[dict]) -> list[Document]:
    """
    Whisper 변환 결과를 ChromaDB에 저장할 LangChain Document로 변환합니다.
    파일 전체 텍스트 1개 + 세그먼트별 텍스트 여러 개를 함께 저장합니다.
    """
    docs = []

    for item in results:
        docs.append(
            Document(
                page_content=item["text"],
                metadata={
                    "source": item["file"],
                    "doc_type": "full_transcript",
                    "language": item["language"],
                },
            )
        )

        for index, segment in enumerate(item["segments"], 1):
            text = segment["text"].strip()
            if not text:
                continue

            docs.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": item["file"],
                        "doc_type": "segment",
                        "segment_index": index,
                        "start": float(segment["start"]),
                        "end": float(segment["end"]),
                        "language": item["language"],
                    },
                )
            )

    return docs


def save_to_chroma(docs: list[Document]) -> Chroma:
    """
    Document를 OpenAI 임베딩으로 벡터화하고 ChromaDB에 영구 저장합니다.
    """
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    if RESET_COLLECTION:
        existing = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(PERSIST_DIR),
        )
        try:
            existing.delete_collection()
        except ValueError:
            pass

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(PERSIST_DIR),
    )

    return vectorstore


def search_examples(vectorstore: Chroma, query: str, k: int = 3) -> None:
    """
    저장된 무전 텍스트에서 유사한 내용을 검색해 확인합니다.
    """
    print("=" * 60)
    print(f"검색 쿼리: {query}")
    print("=" * 60)

    docs = vectorstore.similarity_search(query, k=k)

    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        start = meta.get("start")
        end = meta.get("end")

        timestamp = ""
        if start is not None and end is not None:
            timestamp = f" [{start:.1f}s -> {end:.1f}s]"

        print(f"\n[{i}] {meta.get('source')} / {meta.get('doc_type')}{timestamp}")
        print(doc.page_content)


if __name__ == "__main__":
    results = batch_transcribe(AUDIO_DIR, model_name=MODEL_NAME)
    docs = transcripts_to_documents(results)

    print(f"ChromaDB 저장 중: {len(docs)}개 문서")
    vectorstore = save_to_chroma(docs)
    print(f"저장 완료: {PERSIST_DIR}\n")

    search_examples(
        vectorstore,
        query="출입문 개방, 침입 의심, 현장 조치가 필요한 무전",
        k=3,
    )
