import sqlite3
from lxml import etree
import json

# Define the file path to the XML file and the SQLite database
xml_file_path = './ntlh.xml'  # Use the correct path for the XML file in the current environment
db_path = 'ntlh_pt_bible.db'

# Connect to the SQLite database (or create it)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


f = open('../../abbrev.json')
data = json.load(f)['pt']

englishData = json.load(open('../../abbrev.json'))['en']

intlID = data['intlID']
englishIntlID = englishData['intlID']
bookNames = data['bookNames']

# Create the Books table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    book_abv TEXT,
    int_book_abv TEXT
)
''')

# Create the Chapters table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    chapter_number INTEGER,
    FOREIGN KEY(book_id) REFERENCES Books(id)
)
''')

# Create the Verses table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Verses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER,
    verse_number INTEGER,
    verse_text TEXT,
    FOREIGN KEY(chapter_id) REFERENCES Chapters(id)
)
''')

# Commit the changes
conn.commit()

# Parse the XML file
tree = etree.parse(xml_file_path)
root = tree.getroot()

# Populate the database
for bible in root.findall('testament'):  # Updated to find 'testament' instead of 'bible'
    for book in bible.findall('book'):  # Use the correct root node
        bookIndex = int(book.get('number')) - 1  # Adjust index to be zero-based
        book_name = bookNames[bookIndex]
        book_abv = intlID[bookIndex]
        englishBook_abv = englishIntlID[bookIndex]

        # Insert the book into the Books table
        cursor.execute('INSERT INTO Books (name, book_abv, int_book_abv) VALUES (?, ?, ?)', (book_name, book_abv, englishBook_abv))
        book_id = cursor.lastrowid  # Get the ID of the inserted book

        for chapter in book.findall('chapter'):
            chapter_number = int(chapter.get('number'))

            # Insert the chapter into the Chapters table
            cursor.execute('INSERT INTO Chapters (book_id, chapter_number) VALUES (?, ?)', (book_id, chapter_number))
            chapter_id = cursor.lastrowid  # Get the ID of the inserted chapter

            for verse in chapter.findall('verse'):
                verse_number = int(verse.get('number'))
                verse_text = verse.text.strip() if verse.text else ""

                # Insert the verse into the Verses table
                cursor.execute('INSERT INTO Verses (chapter_id, verse_number, verse_text) VALUES (?, ?, ?)',
                               (chapter_id, verse_number, verse_text))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database creation and population complete.")
