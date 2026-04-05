#!/usr/bin/env python3
"""
Load 3 HuggingFace datasets vào Supabase - Legal AI Agent
Chạy: python scripts/load_hf_datasets.py --test
      python scripts/load_hf_datasets.py --full

Datasets:
1. th1nhng0/vietnamese-legal-documents (179K+ văn bản pháp lý)
2. thangvip/vietnamese-legal-qa (9,720 cặp Q&A)
"""
import os
import json
import time
import itertools
import psycopg2
from psycopg2.extras import execute_values
from datasets import load_dataset
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import List, Tuple
import argparse
try:
    from pyarrow.lib import ArrowInvalid
except Exception:
    ArrowInvalid = Exception

load_dotenv()

# === Kết nối Supabase ===
# Support both direct and pooler connections
host = os.getenv("SUPABASE_DB_HOST", "localhost")
is_pooler = "pooler" in host.lower()

DB_CONFIG = {
    "host": host,
    "port": 6543 if is_pooler else 5432,
    "dbname": "postgres",
    "user": "postgres.cjkrsnqdsfucngmrsnpm" if is_pooler else "postgres",
    "password": os.getenv("SUPABASE_DB_PASSWORD", ""),
    "sslmode": "require"
}

# Map HF dataset types to law_type enum (từ database/init.sql)
TYPE_MAP = {
    "luat": "luat",
    "nghi_dinh": "nghi_dinh",
    "quyet_dinh": "quyet_dinh",
    "thong_tu": "thong_tu",
    "chi_thi": "quyet_dinh",
    "phap_lenh": "other",
    "hien_phap": "hien_phap",
    "nghi_quyet": "nghi_quyet",
}

def load_dataset_with_retry(*args, max_retries: int = 3, **kwargs):
    """Load HuggingFace dataset with simple retry and SSL fallback."""
    # Ensure reasonable timeouts for HF metadata/downloads
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "10")
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "30")
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            return load_dataset(*args, **kwargs)
        except Exception as e:
            last_err = e
            err_msg = str(e).lower()
            # Fallback for SSL cert issues on Windows
            if "ssl" in err_msg or "certificate" in err_msg:
                os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
            if attempt < max_retries:
                time.sleep(2 * attempt)
            else:
                raise last_err

# Legal domains để phân loại
DOMAIN_KEYWORDS = {
    "lao_dong": ["lao động", "người lao động", "tiền lương", "hợp đồng"],
    "doanh_nghiep": ["doanh nghiệp", "công ty", "cổ phần", "thành lập"],
    "dan_su": ["dân sự", "hợp đồng dân sự", "thừa kế", "quyền"],
    "thuong_mai": ["thương mại", "mua bán", "xuất nhập khẩu"],
    "thue": ["thuế", "giá trị gia tăng", "thu nhập"],
    "dat_dai": ["đất đai", "bất động sản", "quyền sử dụng"],
    "dau_tu": ["đầu tư", "vốn", "nhà đầu tư"],
    "bhxh": ["bảo hiểm", "hưu trí", "y tế"],
}

def detect_domains(text: str) -> List[str]:
    """Phát hiện legal domains từ text"""
    domains = []
    text_lower = text.lower()[:5000]  # Check first 5000 chars
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            domains.append(domain)
    return domains or ["other"]

def clean_html(html: str) -> str:
    """Clean HTML to plain text"""
    if not html:
        return ""
    try:
        soup = BeautifulSoup(html, "html.parser")
        # Remove script and style
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=" ")
        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)
        return text.strip()
    except Exception as e:
        print(f"  ⚠️  Error cleaning HTML: {e}")
        return html

def chunk_text(text: str, size: int = 800, overlap: int = 150) -> List[str]:
    """Chia text thành chunks - match logic từ load_law_data.py"""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + size]
        chunk = " ".join(chunk_words)
        if len(chunk) > 50:  # Min chunk size
            chunks.append(chunk)
        i += size - overlap
    return chunks

def print_progress(msg: str):
    """Print with timestamp"""
    print(f"  {msg}")

def load_legal_documents(conn, limit: int = None, force_streaming: bool = False) -> Tuple[int, int]:
    """
    Dataset 1: th1nhng0/vietnamese-legal-documents
    179K Vietnamese legal documents
    """
    print("\n📥 [Dataset 1] th1nhng0/vietnamese-legal-documents")
    print_progress("Kết nối HuggingFace...")
    cur = conn.cursor()

    try:
        if os.getenv("HF_HUB_DISABLE_SSL_VERIFICATION") != "1":
            os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
            print_progress("SSL verify disabled for HF fetch (local-only)")
        # Load with optional limit for testing (fallback to streaming on Arrow errors)
        streaming = force_streaming
        try:
            if streaming:
                ds = load_dataset_with_retry(
                    "th1nhng0/vietnamese-legal-documents",
                    "content",
                    split="data",
                    streaming=True,
                    trust_remote_code=True,
                    download_mode="reuse_dataset_if_exists",
                    verification_mode="no_checks"
                )
                print_progress("Dataset loaded in streaming mode (split=data)")
            else:
                if limit:
                    ds = load_dataset_with_retry(
                        "th1nhng0/vietnamese-legal-documents",
                        "content",
                        split=f"train[:{limit}]"
                    )
                else:
                    ds = load_dataset_with_retry(
                        "th1nhng0/vietnamese-legal-documents",
                        "content",
                        split="train"
                    )
                print_progress(f"Dataset loaded: {len(ds)} rows")
        except ArrowInvalid:
            streaming = True
            ds = load_dataset_with_retry(
                "th1nhng0/vietnamese-legal-documents",
                "content",
                split="train",
                streaming=True
            )
            print_progress("Dataset loaded in streaming mode")

        batch, inserted, skipped = [], 0, 0

        iterable = itertools.islice(ds, limit) if streaming and limit else ds
        for idx, row in enumerate(iterable):
            if idx % 10000 == 0 and idx > 0:
                print_progress(f"Processing row {idx:,}...")

            # Extract and clean content
            content = clean_html(row.get("content_html", "") or row.get("content", ""))
            if len(content) < 100:
                skipped += 1
                continue

            # Map document type
            raw_type = row.get("doc_type", "").lower()
            doc_type = TYPE_MAP.get(raw_type, "bo_luat")

            # Get required fields
            title = (row.get("title", "Không rõ tiêu đề") or "Không rõ tiêu đề")[:500]
            
            # Generate law_number (HF documents may not have official numbers)
            law_id = row.get("id", str(inserted + skipped))
            law_number = f"HF_DOCS_{law_id}"[:100]

            # Detect domains
            domains = detect_domains(content)

            batch.append((
                title,
                law_number,
                doc_type,
                "HuggingFace/th1nhng0",  # issuer
                None,  # signer
                None,  # issued_date
                None,  # effective_date
                None,  # expiry_date
                "active",  # status
                domains,  # domains array
                None,  # replaces
                None,  # amended_by
                content[:50000] if len(content) > 50000 else content,  # full_text (max)
                content[:500] + "..." if len(content) > 500 else content,  # summary
                None,  # table_of_contents
                row.get("source_url", ""),
                "huggingface",  # source_site
                0,  # article_count
                len(content.split()),  # word_count
            ))

            if len(batch) >= 500:
                try:
                    execute_values(cur, """
                        INSERT INTO law_documents 
                        (title, law_number, law_type, issuer, signer, issued_date, effective_date,
                         expiry_date, status, domains, replaces, amended_by, full_text, summary,
                         table_of_contents, source_url, source_site, article_count, word_count)
                        VALUES %s
                        ON CONFLICT (law_number) DO NOTHING
                        RETURNING id
                    """, batch)
                    conn.commit()
                    inserted += len(batch)
                    print_progress(f"✅ {inserted:,} văn bản nạp")
                    batch = []
                except Exception as e:
                    print_progress(f"⚠️  Batch error: {e}")
                    conn.rollback()
                    batch = []

        # Insert remaining
        if batch:
            try:
                execute_values(cur, """
                    INSERT INTO law_documents 
                    (title, law_number, law_type, issuer, signer, issued_date, effective_date,
                     expiry_date, status, domains, replaces, amended_by, full_text, summary,
                     table_of_contents, source_url, source_site, article_count, word_count)
                    VALUES %s
                    ON CONFLICT (law_number) DO NOTHING
                    RETURNING id
                """, batch)
                conn.commit()
                inserted += len(batch)
            except Exception as e:
                print_progress(f"⚠️  Final batch error: {e}")
                conn.rollback()

        print_progress(f"🎯 Hoàn thành: {inserted:,} docs | Bỏ qua: {skipped:,}")
        cur.close()
        return inserted, skipped

    except Exception as e:
        print_progress(f"❌ Error loading Dataset 1: {e}")
        cur.close()
        return 0, 0

def load_qa_pairs(conn, limit: int = None) -> Tuple[int, int]:
    """
    Dataset 2: thangvip/vietnamese-legal-qa
    9,720 Q&A pairs
    """
    print("\n📥 [Dataset 2] thangvip/vietnamese-legal-qa")
    print_progress("Kết nối HuggingFace...")
    cur = conn.cursor()

    try:
        # Proactively disable SSL verification if needed on Windows
        if os.getenv("HF_HUB_DISABLE_SSL_VERIFICATION") != "1":
            os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
            print_progress("SSL verify disabled for HF fetch (local-only)")
        # Load dataset
        if limit:
            ds = load_dataset_with_retry(
                "thangvip/vietnamese-legal-qa",
                split=f"train[:{limit}]"
            )
        else:
            ds = load_dataset_with_retry(
                "thangvip/vietnamese-legal-qa",
                split="train"
            )

        print_progress(f"Dataset loaded: {len(ds)} rows")

        batch, inserted, skipped = [], 0, 0

        for idx, row in enumerate(ds):
            if idx % 1000 == 0 and idx > 0:
                print_progress(f"Processing row {idx:,}...")

            article_content = row.get("article_content", "")
            if len(article_content) < 50:
                skipped += 1
                continue

            qa_pairs = row.get("generated_qa_pairs", [])
            if not qa_pairs:
                skipped += 1
                continue

            # Create document entry for article
            domains = detect_domains(article_content)
            title = f"Q&A Pháp lý: {article_content[:100]}"
            
            for qa_idx, qa in enumerate(qa_pairs):
                if not qa.get("question"):
                    continue

                qa_text = f"Câu hỏi: {qa['question']}\n\nTrả lời: {qa['answer']}"
                law_number = f"HF_QA_{idx}_{qa_idx}"

                batch.append((
                    title[:500],
                    law_number,
                    "bo_luat",  # Q&A docs marked as documents
                    "HuggingFace/thangvip",
                    None,
                    None,
                    None,
                    None,
                    "active",
                    domains,
                    None,
                    None,
                    qa_text,
                    qa_text[:500],
                    None,
                    "",
                    "huggingface",
                    0,
                    len(qa_text.split()),
                ))

            if len(batch) >= 500:
                try:
                    execute_values(cur, """
                        INSERT INTO law_documents 
                        (title, law_number, law_type, issuer, signer, issued_date, effective_date,
                         expiry_date, status, domains, replaces, amended_by, full_text, summary,
                         table_of_contents, source_url, source_site, article_count, word_count)
                        VALUES %s
                        ON CONFLICT (law_number) DO NOTHING
                    """, batch)
                    conn.commit()
                    inserted += len(batch)
                    print_progress(f"✅ {inserted:,} Q&A nạp")
                    batch = []
                except Exception as e:
                    print_progress(f"⚠️  Batch error: {e}")
                    conn.rollback()
                    batch = []

        if batch:
            try:
                execute_values(cur, """
                    INSERT INTO law_documents 
                    (title, law_number, law_type, issuer, signer, issued_date, effective_date,
                     expiry_date, status, domains, replaces, amended_by, full_text, summary,
                     table_of_contents, source_url, source_site, article_count, word_count)
                    VALUES %s
                    ON CONFLICT (law_number) DO NOTHING
                """, batch)
                conn.commit()
                inserted += len(batch)
            except Exception as e:
                print_progress(f"⚠️  Final batch error: {e}")
                conn.rollback()

        print_progress(f"🎯 Hoàn thành: {inserted:,} Q&A")
        cur.close()
        return inserted, skipped

    except Exception as e:
        print_progress(f"❌ Error loading Dataset 2: {e}")
        cur.close()
        return 0, 0

def create_chunks_from_hf(conn) -> int:
    """
    Tạo law_chunks từ documents HuggingFace vừa nạp
    """
    print("\n⚙️  [Chunking] Tạo chunks từ HF documents")
    cur = conn.cursor()

    try:
        total = 0
        while True:
            # Get unprocessed HF documents in batches
            cur.execute("""
                SELECT id, title, full_text FROM law_documents
                WHERE source_site = 'huggingface'
                AND id NOT IN (SELECT DISTINCT law_id FROM law_chunks WHERE law_id IS NOT NULL)
                LIMIT 10000
            """)
            docs = cur.fetchall()
            if not docs:
                break

            print_progress(f"Tìm thấy {len(docs):,} docs chưa có chunks")
            batch = []

            for doc_idx, (doc_id, title, content) in enumerate(docs):
                if doc_idx % 1000 == 0 and doc_idx > 0:
                    print_progress(f"Processing doc {doc_idx:,}...")

                if not content:
                    # Insert a minimal placeholder chunk to mark as processed
                    batch.append((
                        doc_id,
                        title,
                        title or "[EMPTY]",
                    ))
                    continue

                chunks = chunk_text(content)
                if not chunks:
                    batch.append((
                        doc_id,
                        title,
                        title or "[EMPTY]",
                    ))
                else:
                    for chunk in chunks:
                        batch.append((
                            doc_id,  # law_id FK
                            title,
                            chunk,
                        ))

                # Insert in batches
                if len(batch) >= 1000:
                    try:
                        execute_values(cur, """
                            INSERT INTO law_chunks (law_id, title, content)
                            VALUES %s
                            ON CONFLICT DO NOTHING
                        """, batch)
                        conn.commit()
                        total += len(batch)
                        print_progress(f"✅ {total:,} chunks tạo")
                        batch = []
                    except Exception as e:
                        print_progress(f"⚠️  Chunk batch error: {e}")
                        conn.rollback()
                        batch = []

            # Insert remaining
            if batch:
                try:
                    execute_values(cur, """
                        INSERT INTO law_chunks (law_id, title, content)
                        VALUES %s
                        ON CONFLICT DO NOTHING
                    """, batch)
                    conn.commit()
                    total += len(batch)
                except Exception as e:
                    print_progress(f"⚠️  Final chunk error: {e}")
                    conn.rollback()

        print_progress(f"🎯 Tổng chunks mới: {total:,}")
        cur.close()
        return total

    except Exception as e:
        print_progress(f"❌ Error chunking: {e}")
        cur.close()
        return 0

def print_stats(conn):
    """Print final statistics"""
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM law_documents")
        total_docs = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM law_documents WHERE source_site = 'huggingface'")
        hf_docs = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM law_chunks")
        total_chunks = cur.fetchone()[0]
        
        cur.execute("""
            SELECT law_type, COUNT(*) FROM law_documents 
            WHERE source_site = 'huggingface'
            GROUP BY law_type ORDER BY 2 DESC
        """)
        types = cur.fetchall()

        print(f"""
╔════════════════════════════════════════╗
║    📊 THỐNG KÊ SAU KHI NẠPDATA         ║
╠════════════════════════════════════════╣
║  Tổng law_documents : {total_docs:>13,} ║
║  Từ HuggingFace     : {hf_docs:>13,} ║
║  Tổng law_chunks    : {total_chunks:>13,} ║
╠════════════════════════════════════════╣
║  Phân loại văn bản (HF):               ║""")
        for dtype, count in types[:5]:
            print(f"║    {dtype:<10} : {count:>13,} ║")
        print("╚════════════════════════════════════════╝")
        
    except Exception as e:
        print(f"Error printing stats: {e}")
    finally:
        cur.close()

def main():
    parser = argparse.ArgumentParser(description="Load HuggingFace datasets to Supabase")
    parser.add_argument("--test", action="store_true", help="Test mode: 500 rows per dataset")
    parser.add_argument("--full", action="store_true", help="Full mode: load all datasets")
    parser.add_argument(
        "--skip-dataset-1",
        action="store_true",
        help="Skip th1nhng0/vietnamese-legal-documents (Dataset 1)"
    )
    parser.add_argument(
        "--stream-dataset-1",
        action="store_true",
        help="Force streaming mode for Dataset 1"
    )
    parser.add_argument(
        "--skip-dataset-2",
        action="store_true",
        help="Skip thangvip/vietnamese-legal-qa (Dataset 2)"
    )
    args = parser.parse_args()

    if not (args.test or args.full):
        parser.print_help()
        return

    limit = 500 if args.test else None
    mode = "TEST" if args.test else "FULL"

    print(f"\n{'='*50}")
    print(f"  🚀 HuggingFace Data Loading - {mode} MODE")
    print(f"{'='*50}")

    print("\n🔌 Kết nối Supabase...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Kết nối thành công!")
    except Exception as e:
        print(f"❌ Kết nối thất bại: {e}")
        return

    start_time = time.time()
    
    try:
        # Load datasets
        if args.skip_dataset_1:
            print("\n⏭️  Skipping Dataset 1 by request")
            docs_inserted, docs_skipped = 0, 0
        else:
            docs_inserted, docs_skipped = load_legal_documents(
                conn,
                limit=limit,
                force_streaming=args.stream_dataset_1
            )
        if args.skip_dataset_2:
            print("\n⏭️  Skipping Dataset 2 by request")
            qa_inserted, qa_skipped = 0, 0
        else:
            qa_inserted, qa_skipped = load_qa_pairs(conn, limit=limit)
        
        # Create chunks
        chunks_created = create_chunks_from_hf(conn)
        
        # Print stats
        print_stats(conn)
        
        # Summary
        elapsed = time.time() - start_time
        print(f"\n⏱️  Tổng thời gian: {elapsed/60:.1f} phút ({elapsed:.0f}s)")
        print(f"\n✅ SUMMARY:")
        print(f"   Documents: {docs_inserted:,} inserted | {docs_skipped:,} skipped")
        print(f"   Q&A Pairs: {qa_inserted:,} inserted | {qa_skipped:,} skipped")
        print(f"   Chunks: {chunks_created:,} created")
        
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
        print("\n🔌 Kết nối đóng\n")

if __name__ == "__main__":
    main()
