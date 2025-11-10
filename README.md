# Quran & Hadith Application

A comprehensive Islamic texts application combining the complete Quran with authentic Hadith collections, powered by AI semantic search technology.

## Features

- **Complete Quran**: 6,236 verses in 88 translations across 23 languages
- **Authentic Hadiths**: 15,432 hadiths from 4 major collections
  - Sahih al-Bukhari (7,249 hadiths)
  - Sahih Muslim (2,917 hadiths)
  - Jami at-Tirmidhi (3,917 hadiths)
  - Musnad Ahmad (1,349 hadiths)
- **AI-Powered Semantic Search**: Find verses and hadiths by meaning, not just keywords
- **Fuzzy Search**: Fast client-side searching with Fuse.js
- **99 Names of Allah**: Complete with meanings
- **Surah Metadata**: Detailed information for all 114 surahs

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Database**: SQLite (2 databases)
- **AI Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Search**: Fuse.js for fuzzy matching
- **Embeddings**: 384-dimensional vectors for semantic similarity

## Installation

### Prerequisites

- Python 3.x
- pip (Python package manager)
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/BasilSuhail/Quran-Hadith-Application-Database.git
   cd Quran-Hadith-Application-Database/app_source
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask sentence-transformers scipy numpy
   ```

4. **Download the databases**

   The database files are too large for Git (270MB total). You need to generate them locally:

   - **Quran Database** (`quran_database.sqlite` - 215MB): Contains all verses with embeddings
   - **Hadith Database** (`hadith_database.sqlite` - 44MB): Contains all hadiths with embeddings

   > **Note**: Database generation scripts will be provided in a future update. For now, please contact the maintainer for database files.

5. **Run the application**
   ```bash
   python3 app.py
   ```

6. **Open in browser**
   ```
   http://127.0.0.1:5005
   ```

## Usage

### Unified Search
Search across both Quran and Hadith simultaneously. The AI understands context and meaning, finding relevant results even if they don't contain your exact words.

Example:
- Query: "forgiveness"
- Finds: Verses about mercy, pardoning, absolution, etc.

### Quran Translations
- Browse all 6,236 verses
- Switch between 88 translations in 23 languages
- Load all verses for comprehensive searching
- Filter by Surah

### Hadith Collections
- Search through 4 major authentic collections
- Filter by specific collection or search all
- View hadith text, reference, grade, and related questions
- Load complete collections for full-text search

## API Endpoints

### Quran Endpoints
```
GET  /quran/translations?page=1&per_page=10&surah=1
GET  /quran/surah_info
GET  /quran/names_of_allah
```

### Hadith Endpoints
```
GET  /hadith/collections
GET  /hadith/{collection}?page=1&per_page=10
     Collections: bukhari, muslim, ahmad, tirmidhi
```

### Search Endpoints (POST)
```
POST /search/quran
     Body: {"query": "mercy", "top_n": 5}

POST /search/hadith
     Body: {"query": "prayer", "collection": "all", "top_n": 5}

POST /search/unified
     Body: {"query": "charity", "top_n": 10, "include_quran": true, "include_hadith": true}
```

### Stats
```
GET  /stats
```

## File Structure

```
app_source/
├── app.py                      # Main Flask application
├── unified_search.py           # AI-powered search engine
├── quran_database.sqlite       # Quran database (not in repo - too large)
├── hadith_database.sqlite      # Hadith database (not in repo - too large)
├── Names.csv                   # 99 Names of Allah
├── surah_info.csv              # Surah metadata
├── templates/
│   └── unified_app.html        # Modern responsive frontend
└── venv/                       # Virtual environment
```

## Configuration

### Port
Default port is 5005. Change in `app.py`:
```python
app.run(debug=True, port=5005)
```

### Database Paths
Databases are loaded from the `app_source` directory by default. Modify in `app.py` if needed:
```python
quran_db_path = os.path.join(app_dir, 'quran_database.sqlite')
hadith_db_path = os.path.join(app_dir, 'hadith_database.sqlite')
```

## Performance

- **First Launch**: 3-5 seconds (downloads AI model ~90MB, one-time only)
- **Subsequent Launches**: ~2 seconds
- **First Search**: 2-3 seconds (AI warm-up)
- **Subsequent Searches**: <1 second
- **Memory Usage**: ~200-300 MB

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available for educational and non-commercial use.

## Acknowledgments

- Quran translations from various scholars and institutions
- Authentic hadith collections compiled by great Islamic scholars
- AI technology from Sentence Transformers (HuggingFace)
- Flask web framework
- Fuse.js fuzzy search library
- SQLite database system

## Contact

For questions or support, please open an issue on GitHub.

## Disclaimer

This is an educational tool. For religious guidance, please consult qualified Islamic scholars.

---

**May Allah accept this work and make it beneficial for all who use it.**
