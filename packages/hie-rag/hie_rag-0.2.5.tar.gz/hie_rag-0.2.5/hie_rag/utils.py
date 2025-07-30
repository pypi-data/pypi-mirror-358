import contextlib
import io
import os
import tempfile

import numpy as np
import tiktoken
from markitdown import MarkItDown
from sklearn.metrics.pairwise import cosine_similarity

from .ai_client import AiClient


class Utils:
    def __init__(self, base_url: str):
        # self.client = OpenAI(api_key=api_key)
        self.client = AiClient(base_url=base_url)

    def extract_text(self, uploaded_bytes: bytes, file_name: str):
        """Extract text from an uploaded file using MarkItDown."""
        md = MarkItDown()

        # derive a real suffix from the filename
        suffix = os.path.splitext(file_name)[1].lower() or ".txt"

        # write to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_bytes)
            tmp_path = tmp.name

        try:
            with contextlib.redirect_stderr(io.StringIO()):
                result = md.convert(tmp_path)
        finally:
            os.remove(tmp_path)

        # depending on MarkItDown version this may return a str or an object
        return getattr(result, "text_content", result)

    def count_tokens(self, text: str, encoding="cl100k_base") -> int:
        """Count tokens in text using tiktoken"""
        tokenizer = tiktoken.get_encoding(encoding)
        return len(tokenizer.encode(text))

    def get_embedding(self, text: str, model="nomic-embed-text") -> list:
        if not self.client:
            raise RuntimeError("No embedding client configured")
        return self.client.get_embedding(text, model=model)

    def list_embeddings(self, chunks: list, model="nomic-embed-text") -> list:
        if not self.client:
            raise RuntimeError("No embedding client configured")
        return self.client.list_embeddings(chunks, model=model)

    def get_consecutive_least_similar(self, embeddings: list) -> int:
        """Find the index where consecutive similarity is lowest"""
        cs = cosine_similarity(embeddings)
        
        # Get similarities between consecutive sentences only
        consecutive_similarities = []
        for i in range(len(cs) - 1):
            consecutive_similarities.append(cs[i][i + 1])
        
        # Find the index where consecutive similarity is lowest
        split_index = np.argmin(consecutive_similarities)
        
        return split_index
    
    def get_windowed_least_similar(
        self,
        embeddings: list,
        window_size: int = 3
    ) -> int:
        """
        對 embeddings 做滑動窗口：對每個可能的分割位置 i（0 <= i < len-1），
        將 [max(0, i-window_size+1) .. i] 這 window_size 句平均後的向量
        與 [i+1 .. min(len, i+window_size)] 這 window_size 句平均後的向量做 cosine 相似度，
        回傳相似度最低的那個 i。
        """
        if len(embeddings) < 2:
            # 根本沒得分割
            return 0

        # 把 list-of-lists 轉成 numpy array (shape: [n_sentences, dim_emb])
        embs = np.array(embeddings)
        n = embs.shape[0]

        best_index = 0
        lowest_sim = float('inf')

        for i in range(n - 1):
            # 前半段：從 pre_start 到 i (inclusive)
            pre_start = max(0, i - window_size + 1)
            pre_group = embs[pre_start : i + 1]   # shape: (<=window_size, dim)

            # 後半段：從 i+1 到 post_end-1
            post_end = min(n, i + 1 + window_size)
            post_group = embs[i + 1 : post_end]   # shape: (<=window_size, dim)

            # 計算平均向量
            # （也可以改成加總：np.sum(...)；不過平均比較常見且 scale 感覺一致）
            pre_avg = np.mean(pre_group, axis=0).reshape(1, -1)   # shape: (1, dim)
            post_avg = np.mean(post_group, axis=0).reshape(1, -1) # shape: (1, dim)

            # 計算 cosine similarity
            sim = float(cosine_similarity(pre_avg, post_avg)[0][0])

            if sim < lowest_sim:
                lowest_sim = sim
                best_index = i

        return best_index