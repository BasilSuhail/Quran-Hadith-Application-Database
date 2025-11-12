#!/usr/bin/env python3
"""
Unified Quran & Hadith Application
Combines Quran translations (88 translations, 23 languages) with Hadith collections (4 major books)
Includes semantic search across both databases using AI embeddings
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import sys
from hybrid_search import HybridSearch

app = Flask(__name__)

# Define database paths
app_dir = os.path.dirname(os.path.abspath(__file__))
quran_db_path = os.path.join(app_dir, 'quran_database.sqlite')
hadith_db_path = os.path.join(app_dir, 'hadith_database.sqlite')
assets_dir = os.path.join(os.path.dirname(app_dir), 'mobile_assets')

# Initialize hybrid search with model loaded at startup (web server mode)
print("="*80)
print("Initializing Hybrid Search System (Web Server Mode)")
print("="*80)
print(f"Quran DB: {quran_db_path}")
print(f"Hadith DB: {hadith_db_path}")
print(f"Assets: {assets_dir}")
print()

hybrid_search = HybridSearch(
    quran_db_path,
    hadith_db_path,
    assets_dir=assets_dir,
    load_model=True  # Load model at startup for web server
)

# Pre-load FAISS indices at startup
print("\nPre-loading FAISS indices...")
hybrid_search.load_quran_index()
hybrid_search.load_hadith_index()

print()
print("="*80)
print("✓ Search system ready! (Model + FAISS indices loaded)")
print("="*80)
print()


def get_quran_connection():
    """Get connection to Quran database"""
    conn = sqlite3.connect(quran_db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_hadith_connection():
    """Get connection to Hadith database"""
    conn = sqlite3.connect(hadith_db_path)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    """Main page"""
    return render_template('unified_app.html')


# ============================================================================
# QURAN ENDPOINTS
# ============================================================================

@app.route('/quran/translations')
def get_quran_translations():
    """
    Get Quran translations with pagination
    Query params: page, per_page, surah
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    surah = request.args.get('surah', type=int)

    conn = get_quran_connection()

    # Build query - get column names excluding embedding
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(quran_db10_translations)")
    columns = [row[1] for row in cursor.fetchall() if row[1] != 'embedding']

    # Build query with all columns except embedding
    quoted_columns = [f'"{col}"' if " " in col or "-" in col else col for col in columns]
    query = f'SELECT {", ".join(quoted_columns)} FROM quran_db10_translations'

    if surah:
        query += f' WHERE Surah = {surah}'

    # Get total count
    count_query = 'SELECT COUNT(*) FROM quran_db10_translations'
    if surah:
        count_query += f' WHERE Surah = {surah}'
    total = conn.execute(count_query).fetchone()[0]

    # Add pagination
    offset = (page - 1) * per_page
    query += f' LIMIT {per_page} OFFSET {offset}'

    translations = conn.execute(query).fetchall()
    conn.close()

    return jsonify({
        'translations': [dict(row) for row in translations],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    })


@app.route('/quran/surah_info')
def get_surah_info():
    """Get metadata for all surahs"""
    conn = get_quran_connection()
    surah_info = conn.execute('SELECT * FROM quran_db10_surah_info').fetchall()
    conn.close()
    return jsonify([dict(row) for row in surah_info])


@app.route('/quran/names_of_allah')
def get_names_of_allah():
    """Get 99 names of Allah"""
    conn = get_quran_connection()
    names = conn.execute('SELECT * FROM quran_db10_names_of_allah').fetchall()
    conn.close()
    return jsonify([dict(row) for row in names])


# ============================================================================
# HADITH ENDPOINTS
# ============================================================================

@app.route('/hadith/collections')
def get_hadith_collections():
    """Get metadata for all hadith collections"""
    conn = get_hadith_connection()
    collections = conn.execute('SELECT * FROM collection_metadata ORDER BY total_hadiths DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in collections])


@app.route('/hadith/<collection>')
def get_hadiths_by_collection(collection):
    """
    Get hadiths from a specific collection
    Query params: page, per_page
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if collection not in ['bukhari', 'muslim', 'ahmad', 'tirmidhi']:
        return jsonify({'error': 'Invalid collection'}), 400

    conn = get_hadith_connection()

    # Get total count
    total = conn.execute('SELECT COUNT(*) FROM hadiths WHERE collection = ?', (collection,)).fetchone()[0]

    # Get paginated results
    offset = (page - 1) * per_page
    query = '''
        SELECT id, hadith_text, reference, book_number, hadith_number,
               grade, question_id, question, topic
        FROM hadiths
        WHERE collection = ?
        LIMIT ? OFFSET ?
    '''
    hadiths = conn.execute(query, (collection, per_page, offset)).fetchall()
    conn.close()

    return jsonify({
        'collection': collection,
        'hadiths': [dict(row) for row in hadiths],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page
    })


@app.route('/hadith/topics/list')
def get_hadith_topics():
    """Get all available hadith topics with counts"""
    topics = hybrid_search.get_topics()
    return jsonify({
        'topics': topics,
        'total_topics': len(topics)
    })


@app.route('/hadith/topic/<topic>')
def get_hadiths_by_topic(topic):
    """
    Browse hadiths by topic
    Query params: page, per_page
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    results = hybrid_search.get_hadiths_by_topic(topic, page, per_page)
    return jsonify(results)


@app.route('/hadith/<int:hadith_id>/similar')
def get_similar_hadiths_endpoint(hadith_id):
    """
    Get hadiths similar to a given hadith
    Query params: top_n (default: 5)
    """
    top_n = request.args.get('top_n', 5, type=int)

    similar = hybrid_search.get_similar_hadiths(hadith_id, top_n)
    return jsonify({
        'hadith_id': hadith_id,
        'similar_hadiths': similar,
        'count': len(similar)
    })


# ============================================================================
# UNIFIED SEARCH ENDPOINTS
# ============================================================================

@app.route('/search/quran', methods=['POST'])
def search_quran():
    """
    Hybrid search in Quran translations (FAISS + FTS5)
    Body: {"query": "your search", "top_n": 5}
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_n = data.get('top_n', 5)

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        results = hybrid_search.search_quran(query, top_n)

        return jsonify({
            'query': query,
            'source': 'quran',
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search/hadith', methods=['POST'])
def search_hadith():
    """
    Hybrid search in Hadith collections (FAISS + FTS5)
    Body: {"query": "your search", "collection": "all", "top_n": 5, "topic": "Prayer"}
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        collection = data.get('collection', 'all')
        top_n = data.get('top_n', 5)
        topic = data.get('topic')

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        results = hybrid_search.search_hadith(query, collection, top_n, topic)

        return jsonify({
            'query': query,
            'source': 'hadith',
            'collection': collection,
            'topic': topic,
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search/all', methods=['POST'])
def search_all():
    """
    Search both Quran and Hadith
    Body: {"query": "your search", "quran_results": 5, "hadith_results": 5, "collection": "all"}
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        quran_results = data.get('quran_results', 5)
        hadith_results = data.get('hadith_results', 5)
        collection = data.get('collection', 'all')

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        results = hybrid_search.search_all(query, quran_results, hadith_results, collection)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search/unified', methods=['POST'])
def search_unified():
    """
    Unified ranked search across both sources
    Body: {"query": "your search", "top_n": 10, "include_quran": true, "include_hadith": true}
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_n = data.get('top_n', 10)
        include_quran = data.get('include_quran', True)
        include_hadith = data.get('include_hadith', True)

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        results = hybrid_search.search_unified(query, top_n, include_quran, include_hadith)

        return jsonify({
            'query': query,
            'source': 'unified',
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.route('/stats')
def get_stats():
    """Get overall statistics for the application"""
    try:
        quran_conn = get_quran_connection()
        hadith_conn = get_hadith_connection()

        # Quran stats
        quran_verses = quran_conn.execute('SELECT COUNT(*) FROM quran_db10_translations').fetchone()[0]
        quran_surahs = quran_conn.execute('SELECT COUNT(*) FROM quran_db10_surah_info').fetchone()[0]

        # Hadith stats
        collections = hadith_conn.execute('SELECT * FROM collection_metadata').fetchall()
        hadith_stats = [dict(row) for row in collections]
        total_hadiths = sum(c['total_hadiths'] for c in hadith_stats)

        quran_conn.close()
        hadith_conn.close()

        return jsonify({
            'quran': {
                'total_verses': quran_verses,
                'total_surahs': quran_surahs,
                'total_translations': 88,
                'total_languages': 23
            },
            'hadith': {
                'total_hadiths': total_hadiths,
                'collections': hadith_stats
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 80)
    print("UNIFIED QURAN & HADITH APPLICATION")
    print("=" * 80)
    print(f"\nQuran Database: {quran_db_path}")
    print(f"Hadith Database: {hadith_db_path}")
    print("\nFeatures:")
    print("  ✓ Quran: 6,236 verses in 88 translations (23 languages)")
    print("  ✓ Hadith: 15,432 authentic hadiths from 4 major collections")
    print("  ✓ AI-powered semantic search across both databases")
    print("  ✓ 99 Names of Allah")
    print("  ✓ Surah information and metadata")
    print("\nStarting server on http://127.0.0.1:5005")
    print("=" * 80)

    app.run(debug=True, port=5005)
