# qh-db: Quran & Hadith Database

A comprehensive Islamic texts database API combining the complete Quran with authentic Hadith collections, powered by AI semantic search technology.

## Quick Start

Get the app running in 3 simple steps:

1. **Navigate to the app directory**
   ```bash
   cd app_source
   ```

2. **Install dependencies** (one-time setup)
   ```bash
   ./venv/bin/pip install flask sentence-transformers scipy numpy faiss-cpu
   ```

3. **Run the app**
   ```bash
   ./venv/bin/python3 app.py
   ```

4. **Open in your browser**
   ```
   http://127.0.0.1:5005
   ```

That's it! The app will start in about 10-15 seconds as it loads the AI model and database indices.

## What's Inside?

### Quran Database
- **Complete Quran**: 6,236 verses in 88 translations across 23 languages
- **99 Names of Allah**: Complete with meanings
- **Surah Metadata**: Detailed information for all 114 surahs

### Hadith Database
- **Authentic Hadiths**: 15,432 hadiths from 4 major collections
  - Sahih al-Bukhari (7,249 hadiths)
  - Sahih Muslim (2,917 hadiths)
  - Jami at-Tirmidhi (3,917 hadiths)
  - Musnad Ahmad (1,349 hadiths)
- **Topic Classification**: Browse hadiths by subject (Prayer, Fasting, Charity, etc.)
- **Similar Hadiths**: Discover related teachings across different collections
- **Smart Filtering**: Search by collection, topic, or both

### Search Capabilities
- **AI-Powered Semantic Search**: Find verses and hadiths by meaning, not just keywords
- **Topic-Based Search**: Filter results by subject matter
- **Cross-Reference Discovery**: Find similar hadiths automatically

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Database**: SQLite (2 databases)
- **AI Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Embeddings**: 384-dimensional vectors for semantic similarity

## Need the Raw Database Files?

The SQLite database files are included in the `app_source/` directory:
- **Quran Database**: `app_source/quran_database.sqlite` (227 MB)
- **Hadith Database**: `app_source/hadith_database.sqlite` (93 MB)

You can use these files directly with any SQLite browser or in your own projects. They contain:
- All verses and hadiths with full text
- Pre-computed AI embeddings for semantic search
- Metadata and classifications

**Note**: The databases are tracked with Git LFS (Large File Storage). If you clone the repo and the database files appear very small, you may need to install Git LFS:
```bash
git lfs install
git lfs pull
```

## Advanced Setup (Optional)

If you want to set up from scratch or customize:

### Prerequisites
- Python 3.x
- pip (Python package manager)

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/BasilSuhail/Quran-Hadith-Application-Database.git
   cd Quran-Hadith-Application-Database
   ```

2. **Install Git LFS for database files**
   ```bash
   git lfs install
   git lfs pull
   ```

3. **Navigate to app directory**
   ```bash
   cd app_source
   ```

4. **Install dependencies in virtual environment**
   ```bash
   ./venv/bin/pip install flask sentence-transformers scipy numpy faiss-cpu
   ```

5. **Run the application**
   ```bash
   ./venv/bin/python3 app.py
   ```

## How to Use

Once the app is running, open http://127.0.0.1:5005 in your browser.

### Search Across Quran & Hadith
The AI-powered search understands meaning, not just keywords. Try searching for:
- "forgiveness" → finds verses about mercy, pardoning, repentance
- "prayer times" → finds hadiths about salah and its timings
- "charity" → finds content about zakat, sadaqah, and giving

### Browse by Collection
- **Quran**: View all 6,236 verses, switch between 88 translations in 23 languages
- **Hadith**: Browse by collection (Bukhari, Muslim, Tirmidhi, Ahmad) or by topic
- Filter and search within specific collections

### Discover Similar Content
Click on any hadith to see related hadiths from other collections on the same topic

## API Endpoints

The app provides a REST API for developers:

### Main Endpoints
- `GET /` - Web interface
- `GET /stats` - Database statistics
- `POST /search/unified` - Search both Quran and Hadith
- `POST /search/quran` - Search Quran only
- `POST /search/hadith` - Search Hadith only
- `GET /quran/translations` - Get Quran verses (paginated)
- `GET /quran/surah_info` - Get surah metadata
- `GET /quran/names_of_allah` - Get 99 Names of Allah
- `GET /hadith/collections` - List hadith collections
- `GET /hadith/{collection}` - Get hadiths from a collection
- `GET /hadith/topics/list` - List all hadith topics
- `GET /hadith/{id}/similar` - Find similar hadiths

### Example API Call
```bash
curl -X POST http://127.0.0.1:5005/search/unified \
  -H "Content-Type: application/json" \
  -d '{"query": "patience", "top_n": 5}'
```

## Project Structure

```
qh-db/
├── app_source/                 # Main application directory
│   ├── app.py                  # Flask server
│   ├── hybrid_search.py        # AI search engine
│   ├── quran_database.sqlite   # Quran database (227 MB)
│   ├── hadith_database.sqlite  # Hadith database (93 MB)
│   ├── Names.csv               # 99 Names of Allah
│   ├── surah_info.csv          # Surah metadata
│   ├── templates/              # HTML templates
│   └── venv/                   # Python virtual environment
├── mobile_assets/              # Optimized FAISS indices
├── build_database.py           # Database generation script
├── build_mobile_assets.py      # Mobile optimization script
└── README.md                   # This file
```

## Configuration

Want to customize the app? Here's how:

### Change Port
Edit [app.py](app_source/app.py) and change:
```python
app.run(debug=True, port=5005)  # Change 5005 to your preferred port
```

### Use Different Database Files
Edit [app.py](app_source/app.py) and modify:
```python
quran_db_path = os.path.join(app_dir, 'your_quran_database.sqlite')
hadith_db_path = os.path.join(app_dir, 'your_hadith_database.sqlite')
```

## Performance

Expected performance on modern hardware:
- **First Launch**: 10-15 seconds (loads AI model, one-time download ~90MB)
- **Subsequent Launches**: 5-10 seconds
- **Search Speed**: <1 second after initial load
- **Memory Usage**: ~300-500 MB (includes AI model in memory)

## Mobile/Production Optimization

For mobile apps or production deployment, generate optimized FAISS indices:

```bash
python build_mobile_assets.py
```

Benefits:
- **100x faster search** - No need to load heavy AI model on device
- **Smaller footprint** - Pre-computed indices (32 MB vs 90 MB model)
- **Hybrid search** - Combines semantic + keyword search
- **Production ready** - Optimized for mobile and embedded use

Optimized assets are saved in `mobile_assets/` directory.

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
