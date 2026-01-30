#!/usr/bin/env python3
"""
Generate Anki deck with proper sorting and clean grayscale design.
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
# SIMPLE GRAYSCALE DESIGN (Dark Mode Optimized)
# ============================================================================

CARD_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

.card {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  background: #1a1a1a;
  color: #e0e0e0;
  padding: 20px;
  text-align: left;
}

.container {
  max-width: 700px;
  margin: 0 auto;
  background: #242424;
  border-radius: 8px;
  border: 1px solid #333;
}

.header {
  padding: 10px 16px;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag {
  font-size: 11px;
  font-weight: 500;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.type {
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.content {
  padding: 20px;
}

.question {
  font-size: 17px;
  font-weight: 500;
  color: #f0f0f0;
  margin: 0;
  line-height: 1.7;
}

.hr {
  border: none;
  border-top: 1px solid #333;
  margin: 16px 0;
}

.answer {
  color: #c0c0c0;
  font-size: 16px;
  line-height: 1.6;
}

/* Cloze */
.cloze {
  color: #fff;
  font-weight: 600;
}

/* Inline code */
code {
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  font-size: 0.88em;
  background: #1a1a1a;
  color: #d0d0d0;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #333;
}

/* Code blocks */
pre {
  background: #0d0d0d;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 16px;
  margin: 12px 0;
  overflow-x: auto;
}

pre code {
  background: none;
  border: none;
  padding: 0;
  font-size: 13px;
  line-height: 1.5;
  color: #d4d4d4;
  white-space: pre;
  display: block;
}

/* Syntax highlighting - grayscale with subtle tints */
.kw { color: #c9c9c9; font-weight: 500; }
.str { color: #a8a8a8; }
.num { color: #b8b8b8; }
.cmt { color: #666; font-style: italic; }
.bi { color: #d0d0d0; }

/* Complexity */
.complexity {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: #aaa;
}

/* Light mode fallback */
.card:not(.nightMode) {
  background: #f5f5f5;
  color: #222;
}
.card:not(.nightMode) .container {
  background: #fff;
  border-color: #ddd;
}
.card:not(.nightMode) .header {
  border-color: #ddd;
}
.card:not(.nightMode) .question {
  color: #111;
}
.card:not(.nightMode) .answer {
  color: #333;
}
.card:not(.nightMode) code {
  background: #f0f0f0;
  color: #333;
  border-color: #ddd;
}
.card:not(.nightMode) pre {
  background: #f8f8f8;
  border-color: #ddd;
}
.card:not(.nightMode) pre code {
  color: #333;
}
.card:not(.nightMode) .hr {
  border-color: #ddd;
}

/* Mobile */
@media (max-width: 600px) {
  .card { padding: 12px; font-size: 15px; }
  .content { padding: 16px; }
  pre code { font-size: 12px; }
}
"""

BASIC_FRONT = """<div class="container">
  <div class="header">
    <span class="tag">{{Tags}}</span>
    <span class="type">Q</span>
  </div>
  <div class="content">
    <div class="question">{{Front}}</div>
  </div>
</div>"""

BASIC_BACK = """<div class="container">
  <div class="header">
    <span class="tag">{{Tags}}</span>
    <span class="type">A</span>
  </div>
  <div class="content">
    <div class="question">{{Front}}</div>
    <hr class="hr">
    <div class="answer">{{Back}}</div>
  </div>
</div>"""

CLOZE_TEMPLATE = """<div class="container">
  <div class="header">
    <span class="tag">{{Tags}}</span>
    <span class="type">Fill</span>
  </div>
  <div class="content">
    <div class="question">{{cloze:Front}}</div>
  </div>
</div>"""

# ============================================================================
# MODELS WITH SORT FIELD
# ============================================================================

def model_id(name):
    return int(hashlib.md5(name.encode()).hexdigest()[:8], 16)

# Basic model with Sort field
basic_model = genanki.Model(
    model_id('LeetCode-Basic-v7'),
    'LeetCode Basic',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Tags'},
        {'name': 'Sort'},  # Sort field for ordering
    ],
    templates=[{'name': 'Card', 'qfmt': BASIC_FRONT, 'afmt': BASIC_BACK}],
    css=CARD_CSS,
    sort_field_index=3,  # Use Sort field for ordering
)

# Cloze model with Sort field
cloze_model = genanki.Model(
    model_id('LeetCode-Cloze-v7'),
    'LeetCode Cloze',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Tags'},
        {'name': 'Sort'},  # Sort field for ordering
    ],
    templates=[{'name': 'Cloze', 'qfmt': CLOZE_TEMPLATE, 'afmt': CLOZE_TEMPLATE}],
    css=CARD_CSS,
    model_type=genanki.Model.CLOZE,
    sort_field_index=3,  # Use Sort field for ordering
)

# ============================================================================
# TOPICS - Ordered
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
    ('12_1d_dp', '12 DP 1D'),
    ('13_intervals', '13 Intervals'),
    ('14_greedy', '14 Greedy'),
    ('15_advanced_graphs', '15 Advanced Graphs'),
    ('16_2d_dp', '16 DP 2D'),
    ('17_bit_manipulation', '17 Bit Manipulation'),
    ('18_math_geometry', '18 Math & Geometry'),
]

# Card type ordering
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
    """Sort cards within a topic by type."""
    tags = card.get('Tags', '')
    front = card.get('Front', '')

    if '::' in tags:
        subtype = tags.split('::')[1].lower()
    else:
        subtype = 'code'

    if 'Complete ' in front and '<br>' in front:
        subtype = 'implementation'

    order = TYPE_ORDER.get(subtype, 5)
    return (order, front[:50])

# ============================================================================
# CODE FORMATTING
# ============================================================================

def format_code_block(code):
    """Format code as a proper code block with indentation."""
    # Clean up the code
    lines = code.strip().split('\n')

    # Remove common leading whitespace
    if lines:
        # Find minimum indentation (excluding empty lines)
        min_indent = float('inf')
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)

        if min_indent < float('inf'):
            lines = [line[min_indent:] if len(line) >= min_indent else line for line in lines]

    formatted_code = '\n'.join(lines)

    # Simple syntax highlighting
    keywords = ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'return',
                'import', 'from', 'as', 'try', 'except', 'with', 'lambda',
                'yield', 'raise', 'pass', 'break', 'continue', 'in', 'not',
                'and', 'or', 'is', 'None', 'True', 'False', 'self']
    builtins = ['len', 'range', 'int', 'str', 'list', 'dict', 'set', 'tuple',
                'max', 'min', 'sum', 'abs', 'sorted', 'enumerate', 'zip',
                'map', 'filter', 'any', 'all', 'heapq', 'deque', 'Counter',
                'defaultdict', 'heappush', 'heappop', 'bisect_left']

    # Escape HTML
    formatted_code = formatted_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Comments
    formatted_code = re.sub(r'(#[^\n]*)', r'<span class="cmt">\1</span>', formatted_code)

    # Strings
    formatted_code = re.sub(r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')', r'<span class="str">\1</span>', formatted_code)

    # Numbers
    formatted_code = re.sub(r'\b(\d+\.?\d*)\b', r'<span class="num">\1</span>', formatted_code)

    # Keywords
    for kw in keywords:
        formatted_code = re.sub(rf'\b({kw})\b', r'<span class="kw">\1</span>', formatted_code)

    # Builtins
    for bi in builtins:
        formatted_code = re.sub(rf'\b({bi})\b', r'<span class="bi">\1</span>', formatted_code)

    return f'<pre><code>{formatted_code}</code></pre>'


def format_content(text):
    """Format card content, converting code to proper blocks."""
    if not text:
        return text

    # Check if this is a code implementation card (has <br> and code patterns)
    if '<br>' in text and ('def ' in text or 'class ' in text or '{{c1::' in text):
        # This is a code card - convert to proper code block

        # Convert <br> to newlines
        code = text.replace('<br>', '\n')

        # Check if there's a title prefix like "Complete X:"
        title_match = re.match(r'^(Complete [^:]+):\s*\n?', code)
        title = ''
        if title_match:
            title = title_match.group(1)
            code = code[title_match.end():]

        # Format as code block
        formatted = format_code_block(code)

        if title:
            return f'<div style="color:#888;font-size:12px;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">{title}</div>{formatted}'
        return formatted

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

    topic = topic.replace('_', ' ').title()
    topic = topic.replace('1d', '1D').replace('2d', '2D')
    topic = re.sub(r'\bDp\b', 'DP', topic)

    if subtype:
        subtype = subtype.replace('_', ' ').title()
        return f"{topic} › {subtype}"
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
    global_sort_index = 0

    print("=" * 50)
    print("  LeetCode DSA Anki Deck Generator")
    print("  Grayscale Design with Sort Field")
    print("=" * 50)
    print()

    for topic_idx, (topic_file, topic_name) in enumerate(TOPICS):
        filepath = os.path.join(topics_dir, f'{topic_file}.csv')
        if not os.path.exists(filepath):
            continue

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

        # Sort cards by type
        cards.sort(key=get_card_sort_key)

        # Add cards with sort index
        for card_idx, card in enumerate(cards):
            card_type = card.get('Type', 'Basic')
            front = card.get('Front', '')
            back = card.get('Back', '')
            tags = card.get('Tags', topic_file)

            display_tag = format_tag(tags)
            front_fmt = format_content(front)
            back_fmt = format_content(back) if back else ''

            # Create sort value: topic_index * 10000 + card_index
            sort_value = str(topic_idx * 10000 + card_idx).zfill(6)
            global_sort_index += 1

            if card_type == 'Cloze':
                note = genanki.Note(
                    model=cloze_model,
                    fields=[front_fmt, back_fmt, display_tag, sort_value],
                    tags=[tags.replace('::', '_')]
                )
            else:
                note = genanki.Note(
                    model=basic_model,
                    fields=[front_fmt, back_fmt, display_tag, sort_value],
                    tags=[tags.replace('::', '_')]
                )

            subdeck.add_note(note)
            total_cards += 1

        all_decks.append(subdeck)
        print(f"  {topic_name}: {len(cards)} cards")

    # Save
    package = genanki.Package(all_decks)
    output_path = os.path.join(script_dir, 'LeetCode_DSA_Deck.apkg')
    package.write_to_file(output_path)

    print()
    print(f"✓ Created: {output_path}")
    print(f"✓ Total: {total_cards} cards in {len(all_decks)} subdecks")
    print(f"✓ Cards have sort field for proper ordering")
    print()

if __name__ == '__main__':
    main()
