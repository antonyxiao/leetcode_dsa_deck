#!/usr/bin/env python3
"""
Generate a beautifully styled Anki deck from the LeetCode DSA flashcards.

This script creates an .apkg file with:
- Modern dark theme styling
- Syntax-highlighted code blocks
- Organized subdecks by topic
- Both Basic and Cloze note types

Usage: python generate_anki_deck.py
Output: LeetCode_DSA_Deck.apkg
"""

import csv
import os
import hashlib
import random

# Try to import genanki, provide instructions if not available
try:
    import genanki
except ImportError:
    print("Error: genanki is required. Install it with:")
    print("  pip install genanki")
    exit(1)

# ============================================================================
# STYLING
# ============================================================================

CARD_CSS = """
/* ==========================================
   LeetCode DSA Deck - Modern Card Styling
   ========================================== */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg-primary: #1a1b26;
  --bg-secondary: #24283b;
  --bg-card: #1f2335;
  --text-primary: #c0caf5;
  --text-secondary: #a9b1d6;
  --text-muted: #565f89;
  --accent-blue: #7aa2f7;
  --accent-purple: #bb9af7;
  --accent-cyan: #7dcfff;
  --accent-green: #9ece6a;
  --accent-orange: #ff9e64;
  --accent-red: #f7768e;
  --accent-yellow: #e0af68;
  --border-color: #3b4261;
  --code-bg: #1a1b26;
  --shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  --radius: 12px;
  --radius-sm: 8px;
}

.card {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 18px;
  line-height: 1.7;
  background: var(--bg-primary);
  color: var(--text-primary);
  padding: 30px;
  text-align: left;
}

.card-container {
  max-width: 800px;
  margin: 0 auto;
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
  padding: 14px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tag-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  backdrop-filter: blur(10px);
}

.card-type {
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-body {
  padding: 28px;
}

.question {
  font-size: 19px;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.6;
}

.answer {
  font-size: 17px;
  color: var(--text-secondary);
  padding: 20px 24px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  border-left: 4px solid var(--accent-green);
  margin-top: 20px;
  line-height: 1.7;
}

.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-color), transparent);
  margin: 24px 0;
}

/* Cloze styling */
.cloze {
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  font-size: 1.05em;
}

/* Code styling */
code {
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
  background: var(--bg-secondary);
  color: var(--accent-cyan);
  padding: 3px 8px;
  border-radius: 5px;
  font-size: 0.88em;
  border: 1px solid var(--border-color);
}

.code-block {
  background: var(--code-bg);
  border-radius: var(--radius-sm);
  padding: 20px;
  margin: 18px 0;
  overflow-x: auto;
  border: 1px solid var(--border-color);
  position: relative;
}

.code-block::before {
  content: 'PYTHON';
  position: absolute;
  top: 10px;
  right: 14px;
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 1.5px;
  font-weight: 600;
}

.code-block code {
  background: transparent;
  border: none;
  padding: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-primary);
  display: block;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Syntax highlighting */
.kw { color: #bb9af7; font-weight: 500; }
.fn { color: #7aa2f7; }
.str { color: #9ece6a; }
.num { color: #ff9e64; }
.cmt { color: #565f89; font-style: italic; }
.op { color: #7dcfff; }
.bi { color: #7dcfff; }
.cls { color: #e0af68; }

/* Implementation card */
.impl {
  border: 2px solid var(--accent-green);
  border-radius: var(--radius);
  overflow: hidden;
  margin: 18px 0;
}

.impl-header {
  background: linear-gradient(135deg, rgba(158, 206, 106, 0.15), rgba(125, 207, 255, 0.15));
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-color);
}

.impl-title {
  color: var(--accent-green);
  font-weight: 600;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.impl-body .code-block {
  margin: 0;
  border: none;
  border-radius: 0;
}

/* Complexity badge */
.complexity {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 13px;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  background: rgba(122, 162, 247, 0.15);
  color: var(--accent-blue);
  border: 1px solid var(--accent-blue);
}

/* Night mode */
.nightMode .card {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --bg-card: #0d1117;
}

/* Mobile */
@media (max-width: 600px) {
  .card { font-size: 16px; padding: 15px; }
  .card-body { padding: 20px; }
  .question { font-size: 17px; }
  .code-block code { font-size: 13px; }
}
"""

# ============================================================================
# TEMPLATES
# ============================================================================

BASIC_FRONT = """
<div class="card-container">
  <div class="card-header">
    <span class="tag-badge">{{Tags}}</span>
    <span class="card-type">Question</span>
  </div>
  <div class="card-body">
    <div class="question">{{Front}}</div>
  </div>
</div>
"""

BASIC_BACK = """
<div class="card-container">
  <div class="card-header">
    <span class="tag-badge">{{Tags}}</span>
    <span class="card-type">Answer</span>
  </div>
  <div class="card-body">
    <div class="question">{{Front}}</div>
    <div class="divider"></div>
    <div class="answer">{{Back}}</div>
  </div>
</div>
"""

CLOZE_FRONT = """
<div class="card-container">
  <div class="card-header">
    <span class="tag-badge">{{Tags}}</span>
    <span class="card-type">Fill in the blank</span>
  </div>
  <div class="card-body">
    <div class="question">{{cloze:Front}}</div>
  </div>
</div>
"""

CLOZE_BACK = """
<div class="card-container">
  <div class="card-header">
    <span class="tag-badge">{{Tags}}</span>
    <span class="card-type">Answer</span>
  </div>
  <div class="card-body">
    <div class="question">{{cloze:Front}}</div>
  </div>
</div>
"""

# ============================================================================
# MODELS
# ============================================================================

def generate_model_id(name):
    """Generate a stable model ID from name."""
    return int(hashlib.md5(name.encode()).hexdigest()[:8], 16)

basic_model = genanki.Model(
    generate_model_id('LeetCode DSA Basic v3'),
    'LeetCode DSA Basic',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Tags'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': BASIC_FRONT,
            'afmt': BASIC_BACK,
        },
    ],
    css=CARD_CSS,
)

cloze_model = genanki.Model(
    generate_model_id('LeetCode DSA Cloze v3'),
    'LeetCode DSA Cloze',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Tags'},
    ],
    templates=[
        {
            'name': 'Cloze',
            'qfmt': CLOZE_FRONT,
            'afmt': CLOZE_BACK,
        },
    ],
    css=CARD_CSS,
    model_type=genanki.Model.CLOZE,
)

# ============================================================================
# DECK CONFIGURATION
# ============================================================================

TOPIC_CONFIG = {
    '01_arrays_hashing': ('1. Arrays & Hashing', '🔢'),
    '02_two_pointers': ('2. Two Pointers', '👆'),
    '03_stack': ('3. Stack', '📚'),
    '04_binary_search': ('4. Binary Search', '🔍'),
    '05_sliding_window': ('5. Sliding Window', '🪟'),
    '06_linked_list': ('6. Linked List', '🔗'),
    '07_trees': ('7. Trees', '🌳'),
    '08_tries': ('8. Tries', '🔤'),
    '09_backtracking': ('9. Backtracking', '↩️'),
    '10_heap_priority_queue': ('10. Heap / Priority Queue', '⬆️'),
    '11_graphs': ('11. Graphs', '🕸️'),
    '12_1d_dp': ('12. 1D Dynamic Programming', '📊'),
    '13_intervals': ('13. Intervals', '📏'),
    '14_greedy': ('14. Greedy', '🤑'),
    '15_advanced_graphs': ('15. Advanced Graphs', '🗺️'),
    '16_2d_dp': ('16. 2D Dynamic Programming', '📈'),
    '17_bit_manipulation': ('17. Bit Manipulation', '🔢'),
    '18_math_geometry': ('18. Math & Geometry', '📐'),
}

# ============================================================================
# HELPERS
# ============================================================================

def highlight_code(text):
    """Add syntax highlighting classes to Python code."""
    keywords = ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'return',
                'import', 'from', 'as', 'try', 'except', 'finally', 'with',
                'lambda', 'yield', 'raise', 'pass', 'break', 'continue', 'in',
                'not', 'and', 'or', 'is', 'None', 'True', 'False', 'self']
    builtins = ['len', 'range', 'print', 'int', 'str', 'list', 'dict', 'set',
                'tuple', 'max', 'min', 'sum', 'abs', 'sorted', 'enumerate',
                'zip', 'map', 'filter', 'any', 'all', 'heapq', 'deque',
                'Counter', 'defaultdict', 'heappush', 'heappop', 'bisect_left']

    import re

    # Simple highlighting for display
    for kw in keywords:
        text = re.sub(rf'\b({kw})\b', r'<span class="kw">\1</span>', text)
    for bi in builtins:
        text = re.sub(rf'\b({bi})\b', r'<span class="bi">\1</span>', text)

    return text


def format_card_content(text, is_implementation=False):
    """Format card content with code highlighting."""
    if not text:
        return text

    # Check if this is an implementation card (contains code)
    if '<br>' in text and ('def ' in text or 'class ' in text):
        is_implementation = True

    if is_implementation:
        # Extract title
        title = "Implementation"
        if ':' in text.split('<br>')[0]:
            parts = text.split(':', 1)
            title = parts[0].replace('Complete ', '').strip()
            text = parts[1].strip()

        # Convert <br> to newlines and highlight
        code = text.replace('<br>', '\n')
        code = highlight_code(code)

        return f'''<div class="impl">
            <div class="impl-header"><span class="impl-title">{title}</span></div>
            <div class="impl-body"><div class="code-block"><code>{code}</code></div></div>
        </div>'''

    # Regular text - just wrap inline code
    import re
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Highlight O() complexity
    text = re.sub(r'O\(([^)]+)\)', r'<span class="complexity">O(\1)</span>', text)

    return text


def generate_deck_id(name):
    """Generate a stable deck ID from name."""
    return int(hashlib.md5(name.encode()).hexdigest()[:12], 16)


def read_csv_file(filepath):
    """Read a CSV file and return list of cards."""
    cards = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cards.append(row)
    return cards


# ============================================================================
# MAIN
# ============================================================================

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    topics_dir = os.path.join(script_dir, 'topics')

    # Create main deck
    main_deck_name = 'LeetCode DSA'
    main_deck = genanki.Deck(
        generate_deck_id(main_deck_name),
        main_deck_name
    )

    # Create subdecks and collect all cards
    all_decks = [main_deck]
    total_cards = 0

    for filename in sorted(os.listdir(topics_dir)):
        if not filename.endswith('.csv'):
            continue

        topic_key = filename.replace('.csv', '')
        if topic_key not in TOPIC_CONFIG:
            continue

        topic_name, emoji = TOPIC_CONFIG[topic_key]
        subdeck_name = f"{main_deck_name}::{topic_name}"

        subdeck = genanki.Deck(
            generate_deck_id(subdeck_name),
            subdeck_name
        )

        filepath = os.path.join(topics_dir, filename)
        cards = read_csv_file(filepath)

        for card in cards:
            card_type = card.get('Type', 'Basic')
            front = card.get('Front', '')
            back = card.get('Back', '')
            tags = card.get('Tags', topic_key)

            # Format display tag
            display_tag = tags.replace('_', ' ').replace('::', ' → ').title()

            # Check if implementation card
            is_impl = 'implementation' in tags.lower() or 'Complete ' in front

            # Format content
            front_formatted = format_card_content(front, is_impl)

            if card_type == 'Cloze':
                note = genanki.Note(
                    model=cloze_model,
                    fields=[front_formatted, back, display_tag],
                    tags=[tags.replace('::', '_')]
                )
            else:
                back_formatted = format_card_content(back)
                note = genanki.Note(
                    model=basic_model,
                    fields=[front_formatted, back_formatted, display_tag],
                    tags=[tags.replace('::', '_')]
                )

            subdeck.add_note(note)
            total_cards += 1

        all_decks.append(subdeck)
        print(f"  {emoji} {topic_name}: {len(cards)} cards")

    # Create package
    package = genanki.Package(all_decks)

    output_path = os.path.join(script_dir, 'LeetCode_DSA_Deck.apkg')
    package.write_to_file(output_path)

    print(f"\n✅ Successfully created: {output_path}")
    print(f"📚 Total cards: {total_cards}")
    print(f"📁 Subdecks: {len(all_decks) - 1}")
    print("\n📖 Import this file into Anki to start studying!")


if __name__ == '__main__':
    print("=" * 50)
    print("🎴 LeetCode DSA Anki Deck Generator")
    print("=" * 50)
    print()
    main()
