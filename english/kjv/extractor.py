import sqlite3
from lxml import etree
import json


f = open('../../abbrev.json')
data = json.load(f)['en']

intlID = data['intlID']
bookNames = data['bookNames']

# Define the file path to the XML file and the SQLite database
xml_file_path = 'KJV.xmm'  # Replace with the correct path to your XML file
db_path = 'kjv_bible.db'

# Connect to the SQLite database (or create it)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the Books table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    book_abv,
    int_book_abv
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
for book in root.findall('b'):
    bookIndex = root.findall('b').index(book)
    book_name = bookNames[bookIndex]

    # Insert the book into the Books table
    cursor.execute('INSERT INTO Books (name, book_abv, int_book_abv) VALUES (?, ?, ?)', (book_name, intlID[bookIndex], intlID[bookIndex]))
    book_id = cursor.lastrowid  # Get the ID of the inserted book

    for chapter in book.findall('c'):
        chapter_number = int(chapter.get('n'))

        # Insert the chapter into the Chapters table
        cursor.execute('INSERT INTO Chapters (book_id, chapter_number) VALUES (?, ?)', (book_id, chapter_number))
        chapter_id = cursor.lastrowid  # Get the ID of the inserted chapter

        for verse in chapter.findall('v'):
            verse_number = int(verse.get('n'))
            verse_text = verse.text.strip()

            # Insert the verse into the Verses table
            cursor.execute('INSERT INTO Verses (chapter_id, verse_number, verse_text) VALUES (?, ?, ?)',
                           (chapter_id, verse_number, verse_text))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database creation and population complete.")

