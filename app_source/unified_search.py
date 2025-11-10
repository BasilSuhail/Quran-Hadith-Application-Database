#!/usr/bin/env python3
"""
Unified semantic search across Quran translations and Hadith collections
Uses vector embeddings for intelligent, meaning-based search
"""

import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import os

class UnifiedSearch:
    def __init__(self, quran_db_path, hadith_db_path):
        """
        Initialize unified search across Quran and Hadith databases

        Args:
            quran_db_path (str): Path to Quran database
            hadith_db_path (str): Path to Hadith database
        """
        self.quran_db_path = quran_db_path
        self.hadith_db_path = hadith_db_path
        self.model = None

    def load_model(self):
        """Load the sentence transformer model (cached)"""
        if self.model is None:
            print("Loading AI model for semantic search...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Model loaded successfully!")
        return self.model

    def search_quran(self, query, top_n=5):
        """
        Search Quran translations using semantic similarity

        Args:
            query (str): Search query
            top_n (int): Number of results to return

        Returns:
            list: Top N most similar verses
        """
        model = self.load_model()
        query_embedding = model.encode(query)

        conn = sqlite3.connect(self.quran_db_path)
        cursor = conn.cursor()

        # Fetch all verses with embeddings
        cursor.execute('SELECT id, Name, Surah, Ayat, "Saheeh International", embedding FROM quran_db10_translations')
        all_verses = cursor.fetchall()

        similarities = []
        for verse_id, name, surah, ayat, text, embedding_blob in all_verses:
            if embedding_blob:
                verse_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                similarity = 1 - cosine(query_embedding, verse_embedding)
                similarities.append({
                    'source': 'Quran',
                    'id': verse_id,
                    'name': name,
                    'surah': surah,
                    'ayat': ayat,
                    'text': text,
                    'reference': f"Surah {surah}:{ayat}",
                    'similarity': float(similarity)
                })

        conn.close()

        # Sort and return top N
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_n]

    def search_hadith(self, query, collection='all', top_n=5, topic=None):
        """
        Search Hadith collections using semantic similarity

        Args:
            query (str): Search query
            collection (str): 'all', 'bukhari', 'muslim', 'ahmad', or 'tirmidhi'
            top_n (int): Number of results to return
            topic (str): Optional topic filter (e.g., 'Prayer', 'Fasting')

        Returns:
            list: Top N most similar hadiths
        """
        model = self.load_model()
        query_embedding = model.encode(query)

        conn = sqlite3.connect(self.hadith_db_path)
        cursor = conn.cursor()

        # Build query with optional filters
        query_sql = "SELECT id, collection, hadith_text, reference, question, topic, embedding FROM hadiths WHERE embedding IS NOT NULL"
        params = []

        if collection != 'all':
            query_sql += " AND collection = ?"
            params.append(collection)

        if topic:
            query_sql += " AND topic = ?"
            params.append(topic)

        try:
            cursor.execute(query_sql, params)
            hadiths = cursor.fetchall()

            all_results = []
            for hadith_id, coll, text, ref, question, topic_val, embedding_blob in hadiths:
                hadith_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                similarity = 1 - cosine(query_embedding, hadith_embedding)
                all_results.append({
                    'source': 'Hadith',
                    'collection': coll.capitalize(),
                    'id': hadith_id,
                    'text': text,
                    'reference': ref,
                    'question': question,
                    'topic': topic_val,
                    'similarity': float(similarity)
                })

        except Exception as e:
            print(f"Error searching hadiths: {e}")
            all_results = []

        conn.close()

        # Sort and return top N
        all_results.sort(key=lambda x: x['similarity'], reverse=True)
        return all_results[:top_n]

    def search_all(self, query, quran_results=5, hadith_results=5, collection='all'):
        """
        Search both Quran and Hadith databases

        Args:
            query (str): Search query
            quran_results (int): Number of Quran results
            hadith_results (int): Number of Hadith results
            collection (str): Hadith collection filter

        Returns:
            dict: Results from both sources
        """
        return {
            'query': query,
            'quran': self.search_quran(query, quran_results),
            'hadith': self.search_hadith(query, collection, hadith_results)
        }

    def search_unified(self, query, top_n=10, include_quran=True, include_hadith=True):
        """
        Search and merge results from both sources into a single ranked list

        Args:
            query (str): Search query
            top_n (int): Total number of results
            include_quran (bool): Include Quran results
            include_hadith (bool): Include Hadith results

        Returns:
            list: Unified ranked list of results
        """
        all_results = []

        if include_quran:
            quran_results = self.search_quran(query, top_n * 2)  # Get more, we'll filter later
            all_results.extend(quran_results)

        if include_hadith:
            hadith_results = self.search_hadith(query, 'all', top_n * 2)
            all_results.extend(hadith_results)

        # Sort all results by similarity
        all_results.sort(key=lambda x: x['similarity'], reverse=True)

        return all_results[:top_n]

    def get_similar_hadiths(self, hadith_id, top_n=5):
        """
        Get hadiths that are similar to a given hadith

        Args:
            hadith_id (int): ID of the hadith
            top_n (int): Number of similar hadiths to return

        Returns:
            list: Similar hadiths with similarity scores
        """
        conn = sqlite3.connect(self.hadith_db_path)
        cursor = conn.cursor()

        try:
            # Get similar hadiths from the pre-computed table
            cursor.execute('''
                SELECT h.id, h.collection, h.hadith_text, h.reference, h.topic, s.similarity_score
                FROM similar_hadiths s
                JOIN hadiths h ON s.similar_hadith_id = h.id
                WHERE s.hadith_id = ?
                ORDER BY s.similarity_score DESC
                LIMIT ?
            ''', (hadith_id, top_n))

            results = []
            for hid, coll, text, ref, topic, score in cursor.fetchall():
                results.append({
                    'id': hid,
                    'collection': coll.capitalize(),
                    'text': text,
                    'reference': ref,
                    'topic': topic,
                    'similarity': float(score)
                })

            return results

        except Exception as e:
            print(f"Error fetching similar hadiths: {e}")
            return []

        finally:
            conn.close()

    def get_topics(self):
        """
        Get all available topics with hadith counts

        Returns:
            list: Topics with counts
        """
        conn = sqlite3.connect(self.hadith_db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT topic, COUNT(*) as count
                FROM hadiths
                WHERE topic IS NOT NULL
                GROUP BY topic
                ORDER BY count DESC
            ''')

            topics = []
            for topic, count in cursor.fetchall():
                topics.append({
                    'topic': topic,
                    'count': count
                })

            return topics

        except Exception as e:
            print(f"Error fetching topics: {e}")
            return []

        finally:
            conn.close()

    def get_hadiths_by_topic(self, topic, page=1, per_page=10):
        """
        Browse hadiths by topic with pagination

        Args:
            topic (str): Topic name
            page (int): Page number
            per_page (int): Results per page

        Returns:
            dict: Paginated results
        """
        conn = sqlite3.connect(self.hadith_db_path)
        cursor = conn.cursor()

        try:
            # Get total count
            cursor.execute('SELECT COUNT(*) FROM hadiths WHERE topic = ?', (topic,))
            total = cursor.fetchone()[0]

            # Get paginated results
            offset = (page - 1) * per_page
            cursor.execute('''
                SELECT id, collection, hadith_text, reference, question, grade
                FROM hadiths
                WHERE topic = ?
                ORDER BY collection, id
                LIMIT ? OFFSET ?
            ''', (topic, per_page, offset))

            hadiths = []
            for hid, coll, text, ref, question, grade in cursor.fetchall():
                hadiths.append({
                    'id': hid,
                    'collection': coll.capitalize(),
                    'text': text,
                    'reference': ref,
                    'question': question,
                    'grade': grade
                })

            return {
                'topic': topic,
                'hadiths': hadiths,
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }

        except Exception as e:
            print(f"Error fetching hadiths by topic: {e}")
            return {'hadiths': [], 'total': 0}

        finally:
            conn.close()


def main():
    """Interactive search demo"""
    print("=" * 80)
    print("UNIFIED QURAN & HADITH SEMANTIC SEARCH")
    print("=" * 80)

    # Setup paths
    app_dir = os.path.dirname(os.path.abspath(__file__))
    quran_db = os.path.join(app_dir, 'quran_database.sqlite')
    hadith_db = os.path.join(app_dir, 'hadith_database.sqlite')

    # Check if databases exist
    if not os.path.exists(quran_db):
        print(f"Error: Quran database not found at {quran_db}")
        return
    if not os.path.exists(hadith_db):
        print(f"Error: Hadith database not found at {hadith_db}")
        return

    # Initialize search
    search = UnifiedSearch(quran_db, hadith_db)

    print("\nSearch Options:")
    print("  1. Search Quran only")
    print("  2. Search Hadith only")
    print("  3. Search both (separate results)")
    print("  4. Search both (unified ranked)")
    print("  Type 'quit' or 'exit' to exit\n")

    while True:
        print("-" * 80)
        query = input("\nEnter your search query: ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if not query:
            print("Please enter a search query.")
            continue

        option = input("Select option (1-4, default: 4): ").strip() or "4"

        try:
            results_count = int(input("Number of results (default: 5): ").strip() or "5")
        except ValueError:
            results_count = 5

        print("\n" + "=" * 80)
        print(f"SEARCHING: '{query}'")
        print("=" * 80)

        try:
            if option == "1":
                # Quran only
                results = search.search_quran(query, results_count)
                print(f"\nFound {len(results)} results from Quran:\n")
                for i, result in enumerate(results, 1):
                    print(f"\n{'='*80}")
                    print(f"RESULT #{i} | {result['reference']} | Similarity: {result['similarity']:.4f}")
                    print(f"{'='*80}")
                    print(f"{result['text'][:500]}{'...' if len(result['text']) > 500 else ''}")

            elif option == "2":
                # Hadith only
                results = search.search_hadith(query, 'all', results_count)
                print(f"\nFound {len(results)} results from Hadith:\n")
                for i, result in enumerate(results, 1):
                    print(f"\n{'='*80}")
                    print(f"RESULT #{i} | {result['collection']} | Similarity: {result['similarity']:.4f}")
                    print(f"{'='*80}")
                    print(f"Reference: {result['reference']}")
                    print(f"{result['text'][:500]}{'...' if len(result['text']) > 500 else ''}")

            elif option == "3":
                # Both separate
                results = search.search_all(query, results_count, results_count)

                print(f"\n{'='*80}")
                print(f"QURAN RESULTS ({len(results['quran'])} found)")
                print(f"{'='*80}")
                for i, result in enumerate(results['quran'], 1):
                    print(f"\n{i}. [{result['reference']}] Similarity: {result['similarity']:.4f}")
                    print(f"   {result['text'][:200]}...")

                print(f"\n{'='*80}")
                print(f"HADITH RESULTS ({len(results['hadith'])} found)")
                print(f"{'='*80}")
                for i, result in enumerate(results['hadith'], 1):
                    print(f"\n{i}. [{result['collection']} - {result['reference']}] Similarity: {result['similarity']:.4f}")
                    print(f"   {result['text'][:200]}...")

            else:  # option == "4"
                # Unified ranking
                results = search.search_unified(query, results_count)
                print(f"\nFound {len(results)} unified results:\n")
                for i, result in enumerate(results, 1):
                    print(f"\n{'='*80}")
                    if result['source'] == 'Quran':
                        print(f"RESULT #{i} | QURAN: {result['reference']} | Similarity: {result['similarity']:.4f}")
                    else:
                        print(f"RESULT #{i} | HADITH: {result['collection']} | Similarity: {result['similarity']:.4f}")
                    print(f"{'='*80}")
                    print(f"{result['text'][:500]}{'...' if len(result['text']) > 500 else ''}")

        except Exception as e:
            print(f"\nError during search: {e}")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
