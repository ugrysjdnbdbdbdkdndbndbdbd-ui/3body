"""
RAG 知识注入：扫描 data 目录下的 .txt，切片后写入 ChromaDB.
可离线执行：python -m backend.rag.ingest（需在项目根目录 3body 下运行）
"""
import os
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 路径：backend/rag/ingest.py -> 项目根 = rag 的 parent.parent
RAG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = RAG_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = RAG_DIR / "db"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"
COLLECTION_NAME = "three_body"


def main() -> None:
    if not DATA_DIR.is_dir():
        print(f"数据目录不存在: {DATA_DIR}，请先创建并放入 .txt 文件")
        return

    txt_files = sorted(DATA_DIR.glob("**/*.txt"))
    if not txt_files:
        print(f"在 {DATA_DIR} 下未找到任何 .txt 文件")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )

    all_docs = []
    for fp in txt_files:
        name = fp.stem
        print(f"正在加载: {fp.name} ...")
        loader = TextLoader(str(fp), encoding="utf-8", autodetect_encoding=True)
        docs = loader.load()
        for d in docs:
            d.metadata["source_file"] = fp.name
            d.metadata["source_title"] = name
        splits = text_splitter.split_documents(docs)
        all_docs.extend(splits)
        print(f"  已处理《{name}》，本文件生成 {len(splits)} 个向量切片")

    if not all_docs:
        print("没有可入库的文档")
        return

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"正在写入向量库: {CHROMA_DIR} (共 {len(all_docs)} 个切片) ...")
    Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name=COLLECTION_NAME,
    )
    print(f"完成。已处理 {len(txt_files)} 个文件，共生成 {len(all_docs)} 个向量切片。")


if __name__ == "__main__":
    main()
