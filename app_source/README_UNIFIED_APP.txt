================================================================================
QURAN & HADITH APPLICATION - USER GUIDE
================================================================================

Welcome! This is a complete Islamic texts application that lets you search and
explore the Quran and Hadith collections using powerful AI technology.

📚 WHAT'S INSIDE?
--------------------------------------------------------------------------------
✓ Complete Quran with 88 different translations in 23 languages
✓ Over 15,000 authentic Hadiths from 4 major collections
✓ Smart AI search that understands meaning, not just keywords
✓ 99 Beautiful Names of Allah
✓ All 114 Surah information and details

================================================================================
🚀 GETTING STARTED (SIMPLE STEPS)
================================================================================

STEP 1: Open Your Terminal
---------------------------
On Mac: Press Cmd + Space, type "Terminal", press Enter
On Windows: Press Win + R, type "cmd", press Enter
On Linux: Press Ctrl + Alt + T

STEP 2: Navigate to the App Folder
-----------------------------------
Type this command (replace <PROJECT_FOLDER> with your actual folder location):

    cd <PROJECT_FOLDER>/app_source

Example: If your project is in Documents/quran_app, you'd type:
    cd Documents/quran_app/app_source

STEP 3: Activate the Virtual Environment
-----------------------------------------
This loads the required programs. Type:

    source venv/bin/activate

You'll see (venv) appear at the start of your command line.

STEP 4: Start the Application
------------------------------
Type this command:

    python3 app.py

Wait a few seconds. You'll see messages like "Loading AI model..." - this is
normal! The first time takes longer (downloads AI model, about 90MB).

STEP 5: Open in Your Browser
-----------------------------
Open your web browser and go to:

    http://127.0.0.1:5005

That's it! The app is now running.

================================================================================
🛑 HOW TO STOP THE APP
================================================================================

Two easy methods:

Method 1 (Recommended) - Kill by Port:
    lsof -ti:5005 | xargs kill -9

Method 2 - If Running in Terminal:
    Press CTRL + C (hold Control key and press C)

================================================================================
📖 HOW TO USE THE APP
================================================================================

When you open the app, you'll see 4 main tabs:

TAB 1: UNIFIED SEARCH (Search Everything at Once)
--------------------------------------------------
This is the most powerful feature! Type any question or topic, and the AI will
search BOTH the Quran and Hadith for you.

How to use:
1. Type your question in plain English (like "What does Islam say about charity?")
2. Choose how many results you want (5-10 is a good start)
3. Toggle checkboxes to search Quran, Hadith, or both
4. Click "Search"

The AI will find the most relevant verses and hadiths, even if they don't use
your exact words! For example, searching "forgiveness" will also find verses
about mercy, pardon, and compassion.

TAB 2: QURAN SEARCH
-------------------
Search only in the Quran translations.

How to use:
1. Type what you're looking for
2. Pick a language and translation from the dropdown
3. Click "Load All Verses" to load the complete Quran (makes search better!)
4. Use the search box to filter verses

Tips:
- Each verse shows the Surah name and Ayat number
- Click "Load All Verses" for the best search experience
- You can search in Arabic, English, Urdu, Turkish, and 19 other languages!

TAB 3: HADITH SEARCH
--------------------
Search in authentic Hadith collections.

How to use:
1. Choose a collection (Bukhari, Muslim, Tirmidhi, Ahmad, or "All")
2. Click "Load All from Current Collection" for better searching
3. Type your search term
4. Results show the hadith text, reference, and related question

Collections explained:
- Sahih al-Bukhari: Most authentic (7,249 hadiths)
- Sahih Muslim: Second most authentic (2,917 hadiths)
- Jami at-Tirmidhi: Detailed commentary (3,917 hadiths)
- Musnad Ahmad: Large collection (1,349 hadiths)

TAB 4: ABOUT
------------
Information about the app, features, and how everything works.

================================================================================
💡 UNDERSTANDING THE AI SEARCH
================================================================================

What is "Semantic Search"?
--------------------------
Traditional search finds exact words. AI semantic search understands MEANING.

Example:
You search: "charity"
AI finds: verses about "giving", "helping the poor", "zakah", "sadaqah"
Even if they don't contain the word "charity"!

How does it work?
-----------------
Think of it like this: The AI reads every verse and hadith, understands what
it means, and gives each one a unique "fingerprint" (called an embedding).
When you search, the AI creates a fingerprint for your query and finds verses
with similar fingerprints.

Why is it powerful?
-------------------
✓ Works across different languages
✓ Finds synonyms and related concepts
✓ Ranks results by relevance (most similar first)
✓ Understands context, not just keywords

Similarity Score:
-----------------
Each result shows a percentage (like 85%). Higher = more relevant to your query.
- 90-100%: Extremely relevant
- 75-90%: Very relevant
- 60-75%: Moderately relevant

================================================================================
📊 WHAT'S IN THE DATABASES?
================================================================================

QURAN DATABASE
--------------
✓ 6,236 verses (all of the Quran)
✓ 114 Surahs
✓ 88 translations by different scholars
✓ 23 languages including:
  - English (20 translations!)
  - Persian/Farsi (12 translations)
  - Turkish (9 translations)
  - Urdu (3 translations)
  - Arabic, Chinese, French, German, Spanish, and many more!

HADITH DATABASE
---------------
✓ 15,432 authentic hadiths
✓ 4 major collections
✓ Question-answer format for easy learning
✓ Authentication grades (Sahih = authentic)
✓ Complete references with book and hadith numbers

Collection Details:
1. Sahih al-Bukhari (7,249 hadiths)
   - Compiled by Imam Bukhari
   - Most authentic collection after the Quran

2. Jami at-Tirmidhi (3,917 hadiths)
   - Compiled by Imam Tirmidhi
   - One of six major collections

3. Sahih Muslim (2,917 hadiths)
   - Compiled by Imam Muslim
   - Second most authentic collection

4. Musnad Ahmad (1,349 hadiths)
   - Compiled by Imam Ahmad ibn Hanbal
   - Organized by narrator

================================================================================
🔍 SEARCH TIPS FOR BEST RESULTS
================================================================================

1. USE NATURAL LANGUAGE
   ✓ Good: "What does Islam say about being kind to parents?"
   ✓ Good: "Patience during difficult times"
   ✗ Avoid: Just typing "patience" (too vague)

2. BE SPECIFIC WHEN YOU CAN
   ✓ "Prayer times and how to pray"
   ✓ "Fasting during Ramadan rules"

3. TRY DIFFERENT PHRASINGS
   If you don't find what you need, rephrase your question:
   - "charity" → "helping the poor" → "giving to those in need"

4. START WITH FEWER RESULTS
   - Begin with 5-10 results
   - If you need more, search again with 20-30

5. USE THE RIGHT TAB
   - Want verses from Quran? → Use "Quran Search" tab
   - Want hadith guidance? → Use "Hadith Search" tab
   - Want both? → Use "Unified Search" tab

6. LOAD ALL DATA FOR BETTER SEARCH
   Click "Load All Verses" or "Load All Hadiths" buttons before searching.
   This lets you search through EVERYTHING instead of just a small sample.

================================================================================
⚡ PERFORMANCE - WHAT TO EXPECT
================================================================================

FIRST TIME RUNNING THE APP
---------------------------
- Takes 3-5 seconds to start
- Downloads AI model (~90MB) - ONE TIME ONLY
- After this, it remembers the model

EVERY TIME AFTER THAT
----------------------
- Starts in ~2 seconds
- No downloads needed
- Ready to search immediately

SEARCH SPEED
------------
- First search: 2-3 seconds (AI warms up)
- After that: Less than 1 second per search
- Searching both Quran + Hadith: 2-3 seconds (lots of data!)

MEMORY USAGE
------------
The app uses about 200-300 MB of RAM. This is normal and won't slow down
your computer.

================================================================================
🚨 TROUBLESHOOTING - FIX COMMON PROBLEMS
================================================================================

PROBLEM: "Port 5005 already in use"
MEANING: The app is already running, or another app is using port 5005
FIX: Stop the existing app first:
    lsof -ti:5005 | xargs kill -9
Then try starting again.

PROBLEM: "ModuleNotFoundError" or "No module named..."
MEANING: Virtual environment is not activated
FIX: Run this command first:
    source venv/bin/activate
You should see (venv) appear in your terminal.

PROBLEM: "Database not found"
MEANING: You're in the wrong folder
FIX: Make sure you navigate to the app_source folder:
    cd <PROJECT_FOLDER>/app_source

PROBLEM: "App is very slow on first run"
MEANING: This is normal! The AI model is downloading (90MB)
FIX: Just wait. It only happens once. After that, it's fast.

PROBLEM: "Search results are not relevant"
MEANING: Query might be too vague
FIX: Try being more specific:
    Instead of "prayer" → "how to perform prayer step by step"
    Instead of "fasting" → "rules of fasting in Ramadan"

PROBLEM: "Browser shows 'Cannot connect' or 'Connection refused'"
MEANING: App is not running
FIX: Make sure you started the app (python3 app.py) and see the success message

PROBLEM: "Only seeing 20-50 results when searching"
MEANING: Only loaded initial data
FIX: Click the "Load All Verses" or "Load All Hadiths" button first

================================================================================
📁 FILES IN THIS APP (FOR REFERENCE)
================================================================================

app_source/
├── app.py                      Main application (the brain)
├── unified_search.py           AI search engine
├── quran_db10.sqlite           Quran database (215 MB)
├── hadith_database.sqlite      Hadith database (44 MB)
├── templates/
│   └── unified_app.html        The webpage you see
└── venv/                       Virtual environment (required programs)

Note: The .sqlite files are databases (like super-organized digital libraries)

================================================================================
🎓 TECHNICAL DETAILS (FOR CURIOUS USERS)
================================================================================

What is Flask?
--------------
Flask is a Python tool that creates web applications. It's what makes this app
run in your browser.

What is SQLite?
---------------
SQLite is a database - think of it as a very organized filing cabinet for data.
We use two databases: one for Quran, one for Hadith.

What is the AI Model?
---------------------
We use "all-MiniLM-L6-v2" - a pre-trained AI that understands text meaning.
- Size: 90 MB
- Type: Sentence transformer
- Purpose: Converts text into numbers (embeddings) for comparison

What are Embeddings?
--------------------
Imagine every verse and hadith has a unique "fingerprint" - a list of 384
numbers that represents its meaning. When you search, the AI compares
fingerprints to find the most similar ones.

What is Cosine Similarity?
---------------------------
A mathematical way to measure how similar two fingerprints are.
Result is a number from 0-100%: higher = more similar.

Dependencies (Required Programs):
----------------------------------
- Python 3.x (programming language)
- Flask (web framework)
- sentence-transformers (AI library)
- scipy (math library)
- numpy (number processing)
- sqlite3 (database, built into Python)

All of these are included in the venv folder!

================================================================================
⚙️ QUICK COMMANDS CHEAT SHEET
================================================================================

Navigate to App:
    cd <PROJECT_FOLDER>/app_source

Activate Virtual Environment:
    source venv/bin/activate

Start App:
    python3 app.py

Stop App (Method 1):
    lsof -ti:5005 | xargs kill -9

Stop App (Method 2):
    Press CTRL + C in terminal

Check if App is Running:
    lsof -ti:5005

View Database Files:
    ls -lh *.sqlite

Check Virtual Environment:
    which python3
    (Should show path with "venv" in it when activated)

================================================================================
🌟 ADVANCED FEATURES
================================================================================

COMMAND-LINE SEARCH
-------------------
You can search without opening the browser!

1. Navigate to app folder and activate venv
2. Run: python3 unified_search.py
3. Choose search type (1-4)
4. Enter your query
5. Get results in the terminal

This is useful for quick searches or scripting.

API ENDPOINTS (FOR DEVELOPERS)
-------------------------------
The app has a REST API you can use in your own programs:

Search Endpoints (send POST requests with JSON):
- /search/unified - Search both Quran and Hadith
- /search/quran - Search only Quran
- /search/hadith - Search only Hadith

Data Endpoints (send GET requests):
- /quran/translations - Get Quran verses
- /hadith/<collection> - Get hadiths from a collection
- /stats - Get database statistics

Example using curl (command line):
    curl -X POST http://localhost:5005/search/unified \
      -H "Content-Type: application/json" \
      -d '{"query": "mercy", "top_n": 5}'

================================================================================
🔐 SECURITY & PRIVACY NOTES
================================================================================

✓ Everything runs on YOUR computer (localhost)
✓ No data is sent to external servers
✓ No internet required after first setup (except for model download)
✓ Your searches are completely private

WARNING FOR PUBLIC DEPLOYMENT:
If you want to put this app online for others to use:
- Don't use Flask's development server (current setup)
- Add user authentication
- Use HTTPS (encrypted connections)
- Add rate limiting to prevent abuse
- Use a production server like gunicorn or uwsgi

The current setup is perfect for personal use but NOT for public websites.

================================================================================
❓ FREQUENTLY ASKED QUESTIONS
================================================================================

Q: Do I need internet to use this app?
A: Only for the first run (downloads the AI model). After that, no internet
   is needed. Everything runs on your computer.

Q: Can I use this on Windows?
A: Yes! The commands are slightly different:
   - Instead of "source venv/bin/activate" use "venv\Scripts\activate"
   - Use "python" instead of "python3"

Q: How much space does this take?
A: About 350 MB total:
   - Quran database: 215 MB
   - Hadith database: 44 MB
   - AI model: 90 MB

Q: Is this data authentic?
A: Yes! The Quran translations come from well-known scholars, and the hadiths
   are from the most authentic collections (Bukhari, Muslim, etc.).

Q: Can I add more translations or hadiths?
A: Yes, but it requires technical knowledge. You'd need to modify the database
   files and regenerate the AI embeddings.

Q: Why are some searches slow?
A: The AI is comparing your query against 21,000+ texts! First search takes
   2-3 seconds, then it's much faster. This is normal.

Q: Can I search in Arabic?
A: Yes! The Quran database includes Arabic text, and the AI works across
   languages.

Q: What if I find an error in a translation?
A: The translations come from established scholars. If you notice something,
   cross-reference with other translations in the app.

Q: Can multiple people use this at once?
A: Yes, but they need to access it from the same network. They can go to:
   http://<YOUR_IP>:5005 (replace <YOUR_IP> with your computer's IP address)

================================================================================
📝 VERSION & UPDATES
================================================================================

Current Version: 2.0 (Quran_db12)
Port: 5005
Last Updated: November 2025

New in Version 2.0:
✓ Added Fuse.js for faster fuzzy search
✓ Improved search performance
✓ Better UI responsiveness
✓ Enhanced search accuracy
✓ "Load All" buttons for comprehensive searching

Previous Version (v1.0):
- Port 5004
- Basic semantic search only

================================================================================
💬 TIPS FOR BEST EXPERIENCE
================================================================================

1. ALWAYS click "Load All" buttons before searching
   → This loads the complete database for better results

2. Start with Unified Search
   → See both Quran and Hadith results together

3. Use specific queries
   → "How to pray Fajr" is better than just "prayer"

4. Check multiple translations
   → Different scholars phrase things differently

5. Read the full hadith
   → The question field gives context about what the hadith teaches

6. Use the similarity score
   → Higher percentages = more relevant to your search

7. Try different collections
   → Bukhari and Muslim are most authentic
   → Tirmidhi has detailed commentary

8. Be patient on first run
   → Model download is one-time, then everything is fast

9. Explore all tabs
   → Each tab offers different ways to find what you need

10. Save your searches
    → Use browser bookmarks for queries you use often

================================================================================
🙏 ACKNOWLEDGMENTS
================================================================================

This application uses:
- Quran translations from various scholars and institutions
- Authentic hadith collections compiled by great Islamic scholars
- AI technology from Sentence Transformers (HuggingFace)
- Flask web framework (open source)
- Fuse.js fuzzy search library
- SQLite database system

May Allah accept this work and make it beneficial for all who use it.

================================================================================
📧 NEED MORE HELP?
================================================================================

If you're stuck:

1. Read this README carefully again
2. Check the Troubleshooting section
3. Make sure you followed all steps in order
4. Verify your virtual environment is activated (you see "venv")
5. Check that you're in the correct folder

For technical issues:
- Check that Python 3 is installed: python3 --version
- Verify database files exist: ls -lh *.sqlite
- Look for error messages in the terminal - they often explain the problem

Remember: Most issues are simple fixes like being in the wrong folder or
forgetting to activate the virtual environment!

================================================================================
✨ ENJOY YOUR JOURNEY IN LEARNING!
================================================================================

This app is designed to make exploring Islamic texts easy, fast, and accurate.
Whether you're studying, teaching, or just curious, the AI search will help
you find what you need.

May your search for knowledge be blessed and fruitful.

================================================================================
Generated with Claude Code
Last Updated: November 2025
================================================================================
