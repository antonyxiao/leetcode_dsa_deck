#!/usr/bin/env python3
"""
Generate a clean, flat-styled Anki deck from the LeetCode DSA flashcards.
"""

import csv
import os
import hashlib
import re

try:
    import genanki
except ImportError:
    print("Install genanki: pip install genanki")
    exit(1)

# ============================================================================
# CLEAN FLAT STYLING
# ============================================================================

CARD_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Fira+Code:wght@400;500&display=swap');

.card {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 17px;
  line-height: 1.6;
  color: #1a1a2e;
  background: #f8f9fa;
  padding: 24px;
  text-align: left;
}

.container {
  max-width: 680px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

/* Header */
.header {
  background: #f1f5f9;
  padding: 12px 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag {
  font-size: 11px;
  font-weight: 600;
  color: #6366f1;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.type {
  font-size: 11px;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Content */
.content {
  padding: 24px;
}

.question {
  font-size: 18px;
  font-weight: 500;
  color: #111827;
  margin: 0;
}

.hr {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 20px 0;
}

.answer {
  background: #f0fdf4;
  border-left: 3px solid #22c55e;
  padding: 16px 20px;
  border-radius: 0 6px 6px 0;
  color: #166534;
  font-size: 16px;
}

/* Cloze */
.cloze {
  color: #6366f1;
  font-weight: 600;
}

/* Code */
code {
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  color: #0f172a;
}

.code-block {
  background: #1e293b;
  color: #e2e8f0;
  padding: 16px 20px;
  border-radius: 6px;
  margin: 16px 0;
  overflow-x: auto;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.code-block .cloze {
  color: #a5b4fc;
  background: rgba(99, 102, 241, 0.2);
  padding: 1px 4px;
  border-radius: 3px;
}

/* Syntax */
.kw { color: #c084fc; }
.fn { color: #60a5fa; }
.str { color: #4ade80; }
.num { color: #fb923c; }
.cmt { color: #64748b; font-style: italic; }
.bi { color: #22d3ee; }

/* Complexity */
.complexity {
  display: inline-block;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  font-weight: 500;
  color: #6366f1;
  background: #eef2ff;
  padding: 2px 8px;
  border-radius: 4px;
}

/* Mobile */
@media (max-width: 600px) {
  .card { padding: 12px; font-size: 15px; }
  .content { padding: 16px; }
  .question { font-size: 16px; }
  .code-block { font-size: 12px; padding: 12px; }
}

/* Night mode */
.nightMode .card { background: #0f172a; color: #e2e8f0; }
.nightMode .container { background: #1e293b; border-color: #334155; }
.nightMode .header { background: #334155; border-color: #475569; }
.nightMode .question { color: #f1f5f9; }
.nightMode .answer { background: #064e3b; border-color: #10b981; color: #d1fae5; }
.nightMode code { background: #334155; color: #e2e8f0; }
.nightMode .hr { border-color: #475569; }
"""

BASIC_FRONT = """<div class="container">
  <div class="header">
    <span class="tag">{{Tags}}</span>
    <span class="type">Question</span>
  </div>
  <div class="content">
    <p class="question">{{Front}}</p>
  </div>
</div>"""

BASIC_BACK = """<div class="container">
  <div class="header">
    <span class="tag">{{Tags}}</span>
    <span class="type">Answer</span>
  </div>
  <div class="content">
    <p class="question">{{Front}}</p>
    <hr class="hr">
    <div class="answer">{{Back}}</div>
  </div>
</div>"""

CLOZE_TEMPLATE = """<div class="container">
  <div class="header">
    <span class="tag">{{Tags}}</span>
    <span class="type">Fill in</span>
  </div>
  <div class="content">
    <div class="question">{{cloze:Front}}</div>
  </div>
</div>"""

# ============================================================================
# MODELS
# ============================================================================

def model_id(name):
    return int(hashlib.md5(name.encode()).hexdigest()[:8], 16)

basic_model = genanki.Model(
    model_id('LeetCode-Basic-v5'),
    'LeetCode Basic',
    fields=[{'name': 'Front'}, {'name': 'Back'}, {'name': 'Tags'}],
    templates=[{'name': 'Card', 'qfmt': BASIC_FRONT, 'afmt': BASIC_BACK}],
    css=CARD_CSS,
)

cloze_model = genanki.Model(
    model_id('LeetCode-Cloze-v5'),
    'LeetCode Cloze',
    fields=[{'name': 'Front'}, {'name': 'Back'}, {'name': 'Tags'}],
    templates=[{'name': 'Cloze', 'qfmt': CLOZE_TEMPLATE, 'afmt': CLOZE_TEMPLATE}],
    css=CARD_CSS,
    model_type=genanki.Model.CLOZE,
)

# ============================================================================
# TOPIC CONFIG - Properly ordered
# ============================================================================

TOPICS = [
    ('01_arrays_hashing', '01 Arrays & Hashing'),
    ('02_two_pointers', '02 Two Pointers'),
    ('03_stack', '03 Stack'),
    ('04_binary_search', '04 Binary Search'),
    ('05_sliding_window', '05 Sliding Window'),
    ('06_linked_list', '06 Linked List'),
    ('07_trees', '07 Trees'),
    ('08_tries', '08 Tries'),
    ('09_backtracking', '09 Backtracking'),
    ('10_heap_priority_queue', '10 Heap & Priority Queue'),
    ('11_graphs', '11 Graphs'),
    ('12_1d_dp', '12 Dynamic Programming 1D'),
    ('13_intervals', '13 Intervals'),
    ('14_greedy', '14 Greedy'),
    ('15_advanced_graphs', '15 Advanced Graphs'),
    ('16_2d_dp', '16 Dynamic Programming 2D'),
    ('17_bit_manipulation', '17 Bit Manipulation'),
    ('18_math_geometry', '18 Math & Geometry'),
]

# Card type ordering (logical learning sequence)
TYPE_ORDER = {
    'concept': 0,
    'python': 1,
    'pattern': 2,
    'code': 3,
    'implementation': 4,
    'problem': 5,
    'complexity': 6,
    'insight': 7,
    'edge_case': 8,
}

def get_card_sort_key(card):
    """Sort cards within a topic by type, then alphabetically."""
    tags = card.get('Tags', '')

    # Extract subtype from tag (e.g., "arrays_hashing::concept" -> "concept")
    if '::' in tags:
        subtype = tags.split('::')[1].lower()
    else:
        subtype = 'code'

    # Check for implementation in content
    front = card.get('Front', '')
    if 'Complete ' in front and '<br>' in front:
        subtype = 'implementation'

    order = TYPE_ORDER.get(subtype, 5)
    return (order, front[:50])

# ============================================================================
# FORMATTING
# ============================================================================

def highlight_python(code):
    """Simple syntax highlighting."""
    keywords = ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'return',
                'import', 'from', 'as', 'try', 'except', 'with', 'lambda',
                'yield', 'raise', 'pass', 'break', 'continue', 'in', 'not',
                'and', 'or', 'is', 'None', 'True', 'False', 'self']
    builtins = ['len', 'range', 'int', 'str', 'list', 'dict', 'set', 'tuple',
                'max', 'min', 'sum', 'abs', 'sorted', 'enumerate', 'zip',
                'map', 'filter', 'any', 'all', 'heapq', 'deque', 'Counter',
                'defaultdict', 'heappush', 'heappop', 'bisect_left']

    # Escape HTML first
    code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Comments
    code = re.sub(r'(#[^\n]*)', r'<span class="cmt">\1</span>', code)

    # Strings
    code = re.sub(r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')', r'<span class="str">\1</span>', code)

    # Numbers
    code = re.sub(r'\b(\d+\.?\d*)\b', r'<span class="num">\1</span>', code)

    # Keywords
    for kw in keywords:
        code = re.sub(rf'\b({kw})\b', r'<span class="kw">\1</span>', code)

    # Builtins
    for bi in builtins:
        code = re.sub(rf'\b({bi})\b', r'<span class="bi">\1</span>', code)

    return code

def format_content(text, is_code_card=False):
    """Format card content."""
    if not text:
        return text

    # Check if implementation card
    if '<br>' in text and ('def ' in text or 'class ' in text or 'Complete' in text):
        is_code_card = True

    if is_code_card:
        # Convert to code block
        code = text.replace('<br>', '\n')

        # Remove "Complete X:" prefix for cleaner display
        if code.startswith('Complete '):
            code = re.sub(r'^Complete [^:]+:\s*\n?', '', code)

        highlighted = highlight_python(code)
        return f'<div class="code-block">{highlighted}</div>'

    # Regular text - format inline code and complexity
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\bO\(([^)]+)\)', r'<span class="complexity">O(\1)</span>', text)

    return text

def format_tag(tag):
    """Format tag for display."""
    if '::' in tag:
        topic, subtype = tag.split('::')
    else:
        topic = tag
        subtype = ''

    # Clean up topic name
    topic = topic.replace('_', ' ').title()
    topic = topic.replace('Dp ', 'DP ')

    if subtype:
        subtype = subtype.replace('_', ' ').title()
        return f"{topic} · {subtype}"
    return topic

# ============================================================================
# MAIN
# ============================================================================

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    topics_dir = os.path.join(script_dir, 'topics')

    main_deck_name = 'LeetCode DSA'
    all_decks = []
    total_cards = 0

    print("=" * 50)
    print("  LeetCode DSA Anki Deck Generator")
    print("  Clean Flat Design")
    print("=" * 50)
    print()

    for topic_file, topic_name in TOPICS:
        filepath = os.path.join(topics_dir, f'{topic_file}.csv')
        if not os.path.exists(filepath):
            continue

        # Create subdeck
        subdeck_name = f"{main_deck_name}::{topic_name}"
        subdeck = genanki.Deck(
            int(hashlib.md5(subdeck_name.encode()).hexdigest()[:12], 16),
            subdeck_name
        )

        # Read and sort cards
        cards = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            cards = list(reader)

        # Sort cards by type for logical learning order
        cards.sort(key=get_card_sort_key)

        # Add cards to deck
        for card in cards:
            card_type = card.get('Type', 'Basic')
            front = card.get('Front', '')
            back = card.get('Back', '')
            tags = card.get('Tags', topic_file)

            display_tag = format_tag(tags)

            # Check if code card
            is_code = ('implementation' in tags.lower() or
                      ('<br>' in front and ('def ' in front or 'class ' in front)))

            front_fmt = format_content(front, is_code)

            if card_type == 'Cloze':
                note = genanki.Note(
                    model=cloze_model,
                    fields=[front_fmt, back, display_tag],
                    tags=[tags.replace('::', '_')]
                )
            else:
                back_fmt = format_content(back, False)
                note = genanki.Note(
                    model=basic_model,
                    fields=[front_fmt, back_fmt, display_tag],
                    tags=[tags.replace('::', '_')]
                )

            subdeck.add_note(note)
            total_cards += 1

        all_decks.append(subdeck)
        print(f"  {topic_name}: {len(cards)} cards")

    # Create and save package
    package = genanki.Package(all_decks)
    output_path = os.path.join(script_dir, 'LeetCode_DSA_Deck.apkg')
    package.write_to_file(output_path)

    print()
    print(f"✓ Created: {output_path}")
    print(f"✓ Total: {total_cards} cards in {len(all_decks)} subdecks")
    print()
    print("Import into Anki to start studying!")

if __name__ == '__main__':
    main()
