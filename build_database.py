#!/usr/bin/env python3
"""
qh-db: Unified Database Builder
================================
This script prepares production-ready databases for BOTH mobile and web deployments:

1. Imports CSV data (Names.csv, surah_info.csv) into quran_database.sqlite
2. Creates FAISS indices for fast semantic search (both mobile and web)
3. Adds FTS5 full-text search tables for keyword matching
4. Generates metadata files
5. Optimizes databases for production use

Output:
  - quran_database.sqlite (with FTS5 + imported CSV tables)
  - hadith_database.sqlite (with FTS5)
  - mobile_assets/quran.index (FAISS)
  - mobile_assets/hadith.index (FAISS)

Run this once during development to prepare production-ready assets.
"""

import sqlite3
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
import json
import csv
from datetime import datetime
from pathlib import Path


class DatabaseBuilder:
    def __init__(self, quran_db_path, hadith_db_path, csv_dir='app_source', output_dir='mobile_assets'):
        self.quran_db_path = quran_db_path
        self.hadith_db_path = hadith_db_path
        self.csv_dir = csv_dir
        self.output_dir = output_dir
        self.model = None

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def load_model(self):
        """Load the sentence transformer model (only needed during build)"""
        if self.model is None:
            print("Loading AI model (build-time only, not needed in production)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Model loaded")
        return self.model

    def import_csv_to_quran_db(self):
        """
        Import Names.csv and surah_info.csv into quran_database.sqlite
        This eliminates the need to read CSV files at runtime
        """
        print("\n" + "="*80)
        print("STEP 1: Importing CSV Data into Quran Database")
        print("="*80)

        conn = sqlite3.connect(self.quran_db_path)
        cursor = conn.cursor()

        # Import Names of Allah
        names_csv = os.path.join(self.csv_dir, 'Names.csv')
        if os.path.exists(names_csv):
            print(f"\nImporting {names_csv}...")

            # Drop existing table if it exists
            cursor.execute('DROP TABLE IF EXISTS names_of_allah')

            # Create table
            cursor.execute('''
                CREATE TABLE names_of_allah (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arabic_name TEXT,
                    name_in_english TEXT,
                    name_meaning TEXT,
                    short_summary TEXT,
                    long_summary TEXT,
                    arabic_root TEXT,
                    details TEXT
                )
            ''')

            # Read and import CSV
            with open(names_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                names_count = 0
                for row in reader:
                    cursor.execute('''
                        INSERT INTO names_of_allah
                        (arabic_name, name_in_english, name_meaning, short_summary,
                         long_summary, arabic_root, details)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['Arabic Name'],
                        row['Name in English'],
                        row['Name Meaning'],
                        row['Short Summary'],
                        row['Long Summary'],
                        row['Arabic Root'],
                        row['Details']
                    ))
                    names_count += 1

            print(f"✓ Imported {names_count} Names of Allah")
        else:
            print(f"⚠ Warning: {names_csv} not found, skipping")

        # Import Surah Info
        surah_csv = os.path.join(self.csv_dir, 'surah_info.csv')
        if os.path.exists(surah_csv):
            print(f"\nImporting {surah_csv}...")

            # Drop existing table if it exists
            cursor.execute('DROP TABLE IF EXISTS surah_info')

            # Create table
            cursor.execute('''
                CREATE TABLE surah_info (
                    surah_number INTEGER PRIMARY KEY,
                    english_title TEXT,
                    arabic_title TEXT,
                    roman_title TEXT,
                    number_of_verses INTEGER,
                    number_of_rukus TEXT,
                    place_of_revelation TEXT
                )
            ''')

            # Read and import CSV
            with open(surah_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                surah_count = 0
                for row in reader:
                    cursor.execute('''
                        INSERT INTO surah_info
                        (surah_number, english_title, arabic_title, roman_title,
                         number_of_verses, number_of_rukus, place_of_revelation)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        int(row['SurahNumber']),
                        row['EnglishTitle'],
                        row['ArabicTitle'],
                        row['RomanTitle'],
                        int(row['NumberOfVerses']),
                        row['NumberOfRukus'],
                        row['PlaceOfRevelation']
                    ))
                    surah_count += 1

            print(f"✓ Imported {surah_count} Surah info records")
        else:
            print(f"⚠ Warning: {surah_csv} not found, skipping")

        conn.commit()
        conn.close()

        print("\n✓ CSV data successfully imported into quran_database.sqlite")
        print("✓ CSV files are no longer needed at runtime")

    def build_quran_faiss_index(self):
        """
        Build FAISS index for Quran verses
        Used by both mobile app and web server for instant semantic search
        """
        print("\n" + "="*80)
        print("STEP 2: Building Quran FAISS Index")
        print("="*80)

        conn = sqlite3.connect(self.quran_db_path)
        cursor = conn.cursor()

        # Fetch all embeddings
        cursor.execute('SELECT id, embedding FROM quran_db10_translations WHERE embedding IS NOT NULL')
        rows = cursor.fetchall()

        print(f"Loading {len(rows)} Quran verse embeddings...")

        # Convert to numpy array
        ids = []
        embeddings = []
        for row_id, embedding_blob in rows:
            ids.append(row_id)
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            embeddings.append(embedding)

        embeddings_matrix = np.array(embeddings).astype('float32')

        print(f"Embeddings shape: {embeddings_matrix.shape}")
        print(f"Memory size: {embeddings_matrix.nbytes / (1024*1024):.2f} MB")

        # Create FAISS index
        dimension = embeddings_matrix.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_matrix)

        # Save index
        index_path = os.path.join(self.output_dir, 'quran.index')
        faiss.write_index(index, index_path)

        # Save ID mapping
        mapping_path = os.path.join(self.output_dir, 'quran_id_mapping.json')
        with open(mapping_path, 'w') as f:
            json.dump(ids, f)

        conn.close()

        index_size = os.path.getsize(index_path) / (1024*1024)
        print(f"✓ Quran index saved: {index_path} ({index_size:.2f} MB)")
        print(f"✓ ID mapping saved: {mapping_path}")

        return len(ids), index_size

    def build_hadith_faiss_index(self):
        """
        Build FAISS index for Hadith collection
        Used by both mobile app and web server
        """
        print("\n" + "="*80)
        print("STEP 3: Building Hadith FAISS Index")
        print("="*80)

        conn = sqlite3.connect(self.hadith_db_path)
        cursor = conn.cursor()

        # Fetch all embeddings from unified table
        cursor.execute('SELECT id, embedding FROM hadiths WHERE embedding IS NOT NULL')
        rows = cursor.fetchall()

        print(f"Loading {len(rows)} Hadith embeddings...")

        # Convert to numpy array
        ids = []
        embeddings = []
        for row_id, embedding_blob in rows:
            ids.append(row_id)
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            embeddings.append(embedding)

        embeddings_matrix = np.array(embeddings).astype('float32')

        print(f"Embeddings shape: {embeddings_matrix.shape}")
        print(f"Memory size: {embeddings_matrix.nbytes / (1024*1024):.2f} MB")

        # Create FAISS index
        dimension = embeddings_matrix.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_matrix)

        # Save index
        index_path = os.path.join(self.output_dir, 'hadith.index')
        faiss.write_index(index, index_path)

        # Save ID mapping
        mapping_path = os.path.join(self.output_dir, 'hadith_id_mapping.json')
        with open(mapping_path, 'w') as f:
            json.dump(ids, f)

        conn.close()

        index_size = os.path.getsize(index_path) / (1024*1024)
        print(f"✓ Hadith index saved: {index_path} ({index_size:.2f} MB)")
        print(f"✓ ID mapping saved: {mapping_path}")

        return len(ids), index_size

    def add_fts5_to_quran(self):
        """
        Add FTS5 (Full-Text Search) virtual table to Quran database
        This enables fast keyword search
        """
        print("\n" + "="*80)
        print("STEP 4: Adding FTS5 to Quran Database")
        print("="*80)

        conn = sqlite3.connect(self.quran_db_path)
        cursor = conn.cursor()

        # Drop existing FTS table if it exists
        cursor.execute('DROP TABLE IF EXISTS quran_fts')

        # Create FTS5 virtual table
        cursor.execute('''
            CREATE VIRTUAL TABLE quran_fts USING fts5(
                id UNINDEXED,
                surah UNINDEXED,
                ayat UNINDEXED,
                name,
                text,
                content='quran_db10_translations',
                content_rowid='id'
            )
        ''')

        # Populate FTS table
        cursor.execute('''
            INSERT INTO quran_fts(rowid, id, surah, ayat, name, text)
            SELECT id, id, Surah, Ayat, Name, "Saheeh International"
            FROM quran_db10_translations
        ''')

        count = cursor.execute('SELECT COUNT(*) FROM quran_db10_translations').fetchone()[0]

        conn.commit()
        conn.close()

        print(f"✓ FTS5 table created with {count} verses")
        print("✓ Keyword search enabled for Quran")

    def add_fts5_to_hadith(self):
        """
        Add FTS5 (Full-Text Search) virtual table to Hadith database
        This enables fast keyword search
        """
        print("\n" + "="*80)
        print("STEP 5: Adding FTS5 to Hadith Database")
        print("="*80)

        conn = sqlite3.connect(self.hadith_db_path)
        cursor = conn.cursor()

        # Drop existing FTS table if it exists
        cursor.execute('DROP TABLE IF EXISTS hadiths_fts')

        # Create FTS5 virtual table
        cursor.execute('''
            CREATE VIRTUAL TABLE hadiths_fts USING fts5(
                id UNINDEXED,
                collection UNINDEXED,
                topic UNINDEXED,
                reference,
                hadith_text,
                question,
                content='hadiths',
                content_rowid='id'
            )
        ''')

        # Populate FTS table
        cursor.execute('''
            INSERT INTO hadiths_fts(rowid, id, collection, topic, reference, hadith_text, question)
            SELECT id, id, collection, topic, reference, hadith_text, question
            FROM hadiths
        ''')

        count = cursor.execute('SELECT COUNT(*) FROM hadiths').fetchone()[0]

        conn.commit()
        conn.close()

        print(f"✓ FTS5 table created with {count} hadiths")
        print("✓ Keyword search enabled for Hadith")

    def generate_metadata(self, quran_count, quran_size, hadith_count, hadith_size):
        """
        Generate metadata file with information about the indices
        """
        print("\n" + "="*80)
        print("STEP 6: Generating Metadata")
        print("="*80)

        metadata = {
            'generated_at': datetime.now().isoformat(),
            'model': 'all-MiniLM-L6-v2',
            'embedding_dimension': 384,
            'quran': {
                'total_verses': quran_count,
                'index_file': 'quran.index',
                'index_size_mb': round(quran_size, 2),
                'id_mapping_file': 'quran_id_mapping.json',
                'fts5_enabled': True,
                'csv_imported': True
            },
            'hadith': {
                'total_hadiths': hadith_count,
                'index_file': 'hadith.index',
                'index_size_mb': round(hadith_size, 2),
                'id_mapping_file': 'hadith_id_mapping.json',
                'fts5_enabled': True,
                'topics_available': True
            },
            'deployment': {
                'mobile_ready': True,
                'web_ready': True,
                'no_model_needed_on_device': True,
                'model_only_for_query_encoding': True
            }
        }

        metadata_path = os.path.join(self.output_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Metadata saved: {metadata_path}")
        print("\nMetadata:")
        print(json.dumps(metadata, indent=2))

    def run_full_pipeline(self):
        """
        Execute the complete data pipeline
        """
        print("\n" + "="*80)
        print("qh-db: UNIFIED DATABASE BUILDER")
        print("="*80)
        print(f"Output directory: {self.output_dir}")
        print("="*80)

        start_time = datetime.now()

        # Step 1: Import CSV data into quran_database.sqlite
        self.import_csv_to_quran_db()

        # Step 2: Build Quran FAISS index
        quran_count, quran_size = self.build_quran_faiss_index()

        # Step 3: Build Hadith FAISS index
        hadith_count, hadith_size = self.build_hadith_faiss_index()

        # Step 4: Add FTS5 to Quran
        self.add_fts5_to_quran()

        # Step 5: Add FTS5 to Hadith
        self.add_fts5_to_hadith()

        # Step 6: Generate metadata
        self.generate_metadata(quran_count, quran_size, hadith_count, hadith_size)

        duration = (datetime.now() - start_time).total_seconds()

        print("\n" + "="*80)
        print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"Time taken: {duration:.1f} seconds")
        print(f"\nProduction-ready assets:")
        print(f"  • {self.quran_db_path} (with FTS5 + CSV data)")
        print(f"  • {self.hadith_db_path} (with FTS5)")
        print(f"  • {self.output_dir}/quran.index (FAISS)")
        print(f"  • {self.output_dir}/hadith.index (FAISS)")
        print("\nThese assets work for:")
        print("  ✓ Mobile apps (Flutter/React Native)")
        print("  ✓ Web servers (Flask/Django/FastAPI)")
        print("  ✓ Desktop applications")
        print("\nNext steps:")
        print("  1. For web: Point Flask app to these databases and FAISS indexes")
        print("  2. For mobile: Copy assets to mobile project")
        print("="*80)


def main():
    """Main entry point"""
    import sys

    # Paths
    app_dir = os.path.dirname(os.path.abspath(__file__))
    quran_db = os.path.join(app_dir, 'app_source', 'quran_database.sqlite')
    hadith_db = os.path.join(app_dir, 'app_source', 'hadith_database.sqlite')
    csv_dir = 'app_source'

    # Check if databases exist
    if not os.path.exists(quran_db):
        print(f"Error: Quran database not found at {quran_db}")
        sys.exit(1)
    if not os.path.exists(hadith_db):
        print(f"Error: Hadith database not found at {hadith_db}")
        sys.exit(1)

    # Build databases
    builder = DatabaseBuilder(quran_db, hadith_db, csv_dir=csv_dir)
    builder.run_full_pipeline()


if __name__ == '__main__':
    main()
