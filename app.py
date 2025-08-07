import os
import re
from flask import Flask, render_template, abort

app = Flask(__name__)

# Configuration
SCRIPTURES_DIR = 'scriptures'
TITLE_MAPPING = {
    'dao_de_jing': '道德经',
    'zhuangzi': '庄子',
}

def get_scriptures():
    """Get a list of all scriptures with their titles."""
    if not os.path.exists(SCRIPTURES_DIR):
        return []
    scriptures = []
    for f in sorted(os.listdir(SCRIPTURES_DIR)):
        if f.endswith('.txt'):
            filename = f.split('.')[0]
            title = TITLE_MAPPING.get(filename, filename.replace('_', ' ').title())
            scriptures.append({'filename': filename, 'title': title})

    return scriptures

@app.route('/')
def index():
    """Main page, showing a list of scriptures."""
    scriptures = get_scriptures()
    return render_template('index.html', scriptures=scriptures)

def parse_scripture(content):
    """Parses raw scripture text into a list of chapters."""
    # This pattern looks for lines that are typical chapter headings.
    pattern = re.compile(r'(^第.*?章.*$)', re.MULTILINE)

    # Split the content by the chapter titles. The titles themselves will be in the resulting list.
    parts = pattern.split(content)

    chapters = []

    # The first part of the split is any text before the first chapter.
    intro_content = parts[0].strip()
    if intro_content:
        chapters.append({
            'title': '引言',  # Introduction
            'anchor': 'chapter-0',
            'content': intro_content
        })

    # The rest of the parts come in pairs of (title, content).
    chapter_parts = parts[1:]
    for i in range(0, len(chapter_parts), 2):
        title = chapter_parts[i].strip()
        chapter_content = chapter_parts[i+1].strip() if (i + 1) < len(chapter_parts) else ""
        anchor = f"chapter-{len(chapters)}"
        chapters.append({
            'title': title,
            'anchor': anchor,
            'content': chapter_content
        })

    # If no chapters were found, treat the entire text as a single block.
    if not chapters and content.strip():
        chapters.append({
            'title': '全文',  # Full Text
            'anchor': 'chapter-0',
            'content': content.strip()
        })

    return chapters

@app.route('/scripture/<string:filename>')
def scripture(filename):
    """Display a single scripture."""
    scriptures = get_scriptures() # For the layout
    filepath = os.path.join(SCRIPTURES_DIR, filename + '.txt')

    if not os.path.exists(filepath):
        abort(404)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    title = TITLE_MAPPING.get(filename, filename.replace('_', ' ').title())

    # Parse the content into a structured format
    parsed_content = parse_scripture(content)

    return render_template('scripture.html', title=title, parsed_content=parsed_content, scriptures=scriptures, show_outline_sidebar=True)

if __name__ == '__main__':
    app.run(debug=True)
