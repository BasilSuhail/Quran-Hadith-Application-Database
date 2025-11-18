#!/usr/bin/env python3
"""
Export Quran and Hadith databases to CSV files
Creates CSV backups of all database tables (excluding embeddings for smaller file sizes)
"""

import sqlite3
import csv
import os
from datetime import datetime

def export_table_to_csv(db_path, table_name, output_dir, exclude_columns=None):
    """Export a single table to CSV, optionally excluding specific columns"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table info to determine columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    all_columns = [col[1] for col in columns_info]

    # Filter out excluded columns
    if exclude_columns:
        columns = [col for col in all_columns if col not in exclude_columns]
    else:
        columns = all_columns

    # Build SELECT query
    columns_str = ', '.join([f'"{col}"' for col in columns])

    # Get data
    cursor.execute(f"SELECT {columns_str} FROM {table_name}")
    rows = cursor.fetchall()

    # Write to CSV
    csv_filename = os.path.join(output_dir, f"{table_name}.csv")
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)  # Header
        writer.writerows(rows)

    conn.close()
    print(f"  ✓ Exported {table_name}: {len(rows)} rows → {csv_filename}")
    return len(rows)

def export_quran_database(db_path, output_dir):
    """Export Quran database to CSV files"""
    print("\n" + "="*80)
    print("EXPORTING QURAN DATABASE")
    print("="*80)

    # Main tables to export (excluding FTS tables and embeddings)
    tables = {
        'quran_db10_translations': ['embedding'],  # Exclude embedding column
        'quran_db10_surah_info': None,
        'quran_db10_names_of_allah': None,
    }

    total_rows = 0
    for table, exclude_cols in tables.items():
        try:
            rows = export_table_to_csv(db_path, table, output_dir, exclude_cols)
            total_rows += rows
        except Exception as e:
            print(f"  ✗ Failed to export {table}: {e}")

    print(f"\nTotal rows exported: {total_rows:,}")
    return total_rows

def export_hadith_database(db_path, output_dir):
    """Export Hadith database to CSV files"""
    print("\n" + "="*80)
    print("EXPORTING HADITH DATABASE")
    print("="*80)

    # Main tables to export (excluding FTS tables and embeddings)
    tables = {
        'collection_metadata': None,
        'hadiths': ['embedding'],  # Exclude embedding column
        'similar_hadiths': None,
    }

    total_rows = 0
    for table, exclude_cols in tables.items():
        try:
            rows = export_table_to_csv(db_path, table, output_dir, exclude_cols)
            total_rows += rows
        except Exception as e:
            print(f"  ✗ Failed to export {table}: {e}")

    print(f"\nTotal rows exported: {total_rows:,}")
    return total_rows

def main():
    """Main export function"""
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(script_dir, f"csv_backups_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    print("="*80)
    print("DATABASE TO CSV EXPORT TOOL")
    print("="*80)
    print(f"Output directory: {output_dir}")

    # Database paths
    quran_db = os.path.join(script_dir, 'app_source', 'quran_database.sqlite')
    hadith_db = os.path.join(script_dir, 'app_source', 'hadith_database.sqlite')

    # Check if databases exist
    if not os.path.exists(quran_db):
        print(f"\n✗ Quran database not found: {quran_db}")
        return

    if not os.path.exists(hadith_db):
        print(f"\n✗ Hadith database not found: {hadith_db}")
        return

    # Export databases
    quran_rows = export_quran_database(quran_db, output_dir)
    hadith_rows = export_hadith_database(hadith_db, output_dir)

    # Summary
    print("\n" + "="*80)
    print("EXPORT COMPLETE")
    print("="*80)
    print(f"Location: {output_dir}")
    print(f"Quran rows: {quran_rows:,}")
    print(f"Hadith rows: {hadith_rows:,}")
    print(f"Total rows: {(quran_rows + hadith_rows):,}")

    # List exported files
    csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    total_size = sum(os.path.getsize(os.path.join(output_dir, f)) for f in csv_files)
    print(f"\nExported {len(csv_files)} CSV files ({total_size / 1024 / 1024:.1f} MB)")
    print("\nFiles:")
    for filename in sorted(csv_files):
        filepath = os.path.join(output_dir, filename)
        size = os.path.getsize(filepath) / 1024 / 1024
        print(f"  - {filename} ({size:.1f} MB)")

    print("\n" + "="*80)
    print("Note: Embedding columns were excluded to reduce file size.")
    print("The CSV files contain all text data but not the AI embeddings.")
    print("="*80)

if __name__ == "__main__":
    main()
