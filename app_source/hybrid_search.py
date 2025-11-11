#!/usr/bin/env python3
"""
Hybrid Search Engine for Quran & Hadith
========================================
Combines semantic search (FAISS) with keyword search (FTS5) for best results

This is optimized for mobile deployment - uses pre-computed FAISS indices
No model needed on device!
"""

import sqlite3
import numpy as np
import faiss
import json
import os
from typing import List, Dict, Tuple


class HybridSearch:
    """
    Mobile-optimized hybrid search engine
    Combines:
    - Semantic search via FAISS indices (no model needed!)
    - Keyword search via SQLite FTS5
    - Reciprocal Rank Fusion for result merging
    """

    def __init__(self, quran_db_path, hadith_db_path, assets_dir='../mobile_assets'):
        self.quran_db_path = quran_db_path
        self.hadith_db_path = hadith_db_path
        self.assets_dir = assets_dir

        # FAISS indices and mappings (loaded on demand)
        self.quran_index = None
        self.quran_id_mapping = None
        self.hadith_index = None
        self.hadith_id_mapping = None

    def load_quran_index(self):
        """Lazy load Quran FAISS index"""
        if self.quran_index is None:
            index_path = os.path.join(self.assets_dir, 'quran.index')
            mapping_path = os.path.join(self.assets_dir, 'quran_id_mapping.json')

            self.quran_index = faiss.read_index(index_path)
            with open(mapping_path, 'r') as f:
                self.quran_id_mapping = json.load(f)

            print(f"✓ Loaded Quran index: {self.quran_index.ntotal} verses")

        return self.quran_index, self.quran_id_mapping

    def load_hadith_index(self):
        """Lazy load Hadith FAISS index"""
        if self.hadith_index is None:
            index_path = os.path.join(self.assets_dir, 'hadith.index')
            mapping_path = os.path.join(self.assets_dir, 'hadith_id_mapping.json')

            self.hadith_index = faiss.read_index(index_path)
            with open(mapping_path, 'r') as f:
                self.hadith_id_mapping = json.load(f)

            print(f"✓ Loaded Hadith index: {self.hadith_index.ntotal} hadiths")

        return self.hadith_index, self.hadith_id_mapping

    def semantic_search_quran(self, query_embedding: np.ndarray, top_n: int = 10) -> List[Tuple[int, float]]:
        """
        Semantic search in Quran using FAISS
        Returns: List of (id, similarity_score) tuples
        """
        index, id_mapping = self.load_quran_index()

        # Search FAISS index
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = index.search(query_embedding, top_n)

        # Convert distances to similarity scores (L2 distance -> similarity)
        # Lower distance = higher similarity
        max_distance = distances[0].max() if len(distances[0]) > 0 else 1.0
        similarities = 1 - (distances[0] / (max_distance + 1e-6))

        # Map FAISS indices to actual database IDs
        results = []
        for idx, sim in zip(indices[0], similarities):
            if idx != -1:  # Valid result
                db_id = id_mapping[int(idx)]
                results.append((db_id, float(sim)))

        return results

    def semantic_search_hadith(self, query_embedding: np.ndarray, top_n: int = 10, topic: str = None) -> List[Tuple[int, float]]:
        """
        Semantic search in Hadith using FAISS
        Returns: List of (id, similarity_score) tuples
        """
        index, id_mapping = self.load_hadith_index()

        # For now, search all. Topic filtering happens in SQL
        # In production, you'd want separate indices per topic for efficiency
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = index.search(query_embedding, top_n * 2)  # Get extra for filtering

        # Convert to similarity scores
        max_distance = distances[0].max() if len(distances[0]) > 0 else 1.0
        similarities = 1 - (distances[0] / (max_distance + 1e-6))

        # Map to database IDs
        results = []
        for idx, sim in zip(indices[0], similarities):
            if idx != -1:
                db_id = id_mapping[int(idx)]
                results.append((db_id, float(sim)))

        return results[:top_n]

    def keyword_search_quran(self, query: str, top_n: int = 10) -> List[Tuple[int, float]]:
        """
        Keyword search in Quran using FTS5
        Returns: List of (id, rank_score) tuples
        """
        conn = sqlite3.connect(self.quran_db_path)
        cursor = conn.cursor()

        try:
            # FTS5 search with BM25 ranking
            cursor.execute('''
                SELECT id, rank
                FROM quran_fts
                WHERE quran_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            ''', (query, top_n))

            results = []
            for row_id, rank in cursor.fetchall():
                # Convert rank to similarity score (rank is negative in FTS5)
                similarity = abs(1.0 / (1.0 + abs(rank)))
                results.append((row_id, similarity))

        except sqlite3.OperationalError:
            # No matches found
            results = []

        finally:
            conn.close()

        return results

    def keyword_search_hadith(self, query: str, top_n: int = 10, collection: str = None, topic: str = None) -> List[Tuple[int, float]]:
        """
        Keyword search in Hadith using FTS5
        Returns: List of (id, rank_score) tuples
        """
        conn = sqlite3.connect(self.hadith_db_path)
        cursor = conn.cursor()

        try:
            # Build query with filters
            fts_query = query
            where_clauses = []

            if collection and collection != 'all':
                where_clauses.append(f"collection = '{collection}'")

            if topic:
                where_clauses.append(f"topic = '{topic}'")

            sql = 'SELECT id, rank FROM hadiths_fts WHERE hadiths_fts MATCH ?'

            if where_clauses:
                sql += ' AND ' + ' AND '.join(where_clauses)

            sql += ' ORDER BY rank LIMIT ?'

            cursor.execute(sql, (fts_query, top_n))

            results = []
            for row_id, rank in cursor.fetchall():
                similarity = abs(1.0 / (1.0 + abs(rank)))
                results.append((row_id, similarity))

        except sqlite3.OperationalError:
            results = []

        finally:
            conn.close()

        return results

    def reciprocal_rank_fusion(self, semantic_results: List[Tuple[int, float]],
                                keyword_results: List[Tuple[int, float]],
                                k: int = 60) -> List[Tuple[int, float]]:
        """
        Merge semantic and keyword results using Reciprocal Rank Fusion
        k=60 is the standard RRF parameter

        Returns: List of (id, fused_score) tuples, sorted by score descending
        """
        scores = {}

        # Add semantic results
        for rank, (doc_id, _) in enumerate(semantic_results):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)

        # Add keyword results
        for rank, (doc_id, _) in enumerate(keyword_results):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)

        # Sort by fused score
        fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return fused

    def hybrid_search_quran(self, query: str, query_embedding: np.ndarray, top_n: int = 10) -> List[Dict]:
        """
        Hybrid search: Combines semantic + keyword search for Quran
        """
        # Get results from both search methods
        semantic_results = self.semantic_search_quran(query_embedding, top_n)
        keyword_results = self.keyword_search_quran(query, top_n)

        # Fuse results
        fused_results = self.reciprocal_rank_fusion(semantic_results, keyword_results)[:top_n]

        # Fetch actual verse data
        conn = sqlite3.connect(self.quran_db_path)
        cursor = conn.cursor()

        results = []
        for doc_id, score in fused_results:
            cursor.execute('''
                SELECT id, Name, Surah, Ayat, "Saheeh International"
                FROM quran_db10_translations
                WHERE id = ?
            ''', (doc_id,))

            row = cursor.fetchone()
            if row:
                results.append({
                    'source': 'Quran',
                    'id': row[0],
                    'name': row[1],
                    'surah': row[2],
                    'ayat': row[3],
                    'text': row[4],
                    'reference': f"Surah {row[2]}:{row[3]}",
                    'similarity': float(score),
                    'search_method': 'hybrid'
                })

        conn.close()
        return results

    def hybrid_search_hadith(self, query: str, query_embedding: np.ndarray,
                             top_n: int = 10, collection: str = 'all', topic: str = None) -> List[Dict]:
        """
        Hybrid search: Combines semantic + keyword search for Hadith
        """
        # Get results from both methods
        semantic_results = self.semantic_search_hadith(query_embedding, top_n, topic)
        keyword_results = self.keyword_search_hadith(query, top_n, collection, topic)

        # Fuse results
        fused_results = self.reciprocal_rank_fusion(semantic_results, keyword_results)[:top_n]

        # Fetch actual hadith data
        conn = sqlite3.connect(self.hadith_db_path)
        cursor = conn.cursor()

        results = []
        for doc_id, score in fused_results:
            cursor.execute('''
                SELECT id, collection, hadith_text, reference, topic, question, grade
                FROM hadiths
                WHERE id = ?
            ''', (doc_id,))

            row = cursor.fetchone()
            if row:
                results.append({
                    'source': 'Hadith',
                    'id': row[0],
                    'collection': row[1].capitalize(),
                    'text': row[2],
                    'reference': row[3],
                    'topic': row[4],
                    'question': row[5],
                    'grade': row[6],
                    'similarity': float(score),
                    'search_method': 'hybrid'
                })

        conn.close()
        return results


def main():
    """Demo of hybrid search"""
    import sys
    from sentence_transformers import SentenceTransformer

    print("="*80)
    print("HYBRID SEARCH DEMO - Quran & Hadith")
    print("="*80)

    # Setup
    app_dir = os.path.dirname(os.path.abspath(__file__))
    quran_db = os.path.join(app_dir, 'quran_database.sqlite')
    hadith_db = os.path.join(app_dir, 'hadith_database.sqlite')

    # Load model (only for demo - not needed on mobile!)
    print("\nLoading model (for query encoding only)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Initialize hybrid search
    search = HybridSearch(quran_db, hadith_db)

    # Demo search
    query = "prayer and patience"
    print(f"\nSearching for: '{query}'")
    print("="*80)

    # Encode query
    query_embedding = model.encode(query)

    # Search Quran
    print("\nQURAN RESULTS (Hybrid Search):")
    print("-"*80)
    quran_results = search.hybrid_search_quran(query, query_embedding, top_n=3)
    for i, result in enumerate(quran_results, 1):
        print(f"\n{i}. {result['reference']} (Score: {result['similarity']:.3f})")
        print(f"   {result['text'][:200]}...")

    # Search Hadith
    print("\n\nHADITH RESULTS (Hybrid Search):")
    print("-"*80)
    hadith_results = search.hybrid_search_hadith(query, query_embedding, top_n=3)
    for i, result in enumerate(hadith_results, 1):
        print(f"\n{i}. [{result['collection']}] {result['reference']} (Score: {result['similarity']:.3f})")
        print(f"   Topic: {result['topic']}")
        print(f"   {result['text'][:200]}...")

    print("\n" + "="*80)
    print("✓ Hybrid search combines best of semantic + keyword matching!")
    print("="*80)


if __name__ == '__main__':
    main()
