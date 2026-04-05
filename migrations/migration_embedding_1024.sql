-- Migration: Chuẩn hóa embedding cho AI semantic search (BGE-M3, 1024 chiều)
-- Chạy trên Supabase SQL Editor hoặc migration tool

-- Xóa index embedding cũ nếu có
DROP INDEX IF EXISTS idx_law_chunks_embedding;
DROP INDEX IF EXISTS idx_company_chunks_embedding;

-- Đặt NULL toàn bộ embedding cũ để tránh lỗi khi đổi số chiều
UPDATE law_chunks SET embedding = NULL;
-- Nếu có bảng company_chunks:
-- UPDATE company_chunks SET embedding = NULL;

-- Đổi schema cột embedding sang vector(1024)
ALTER TABLE law_chunks ALTER COLUMN embedding TYPE vector(1024);
-- Nếu có bảng company_chunks:
-- ALTER TABLE company_chunks ALTER COLUMN embedding TYPE vector(1024);

-- Tạo lại index cho embedding
CREATE INDEX idx_law_chunks_embedding ON law_chunks USING hnsw (embedding vector_cosine_ops);
-- Nếu có bảng company_chunks:
-- CREATE INDEX idx_company_chunks_embedding ON company_chunks USING hnsw (embedding vector_cosine_ops);
