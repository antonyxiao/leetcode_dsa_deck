#!/usr/bin/env python3
"""
Generate Anki deck with proper sorting, grayscale design, and correct code formatting.
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
# SIMPLE GRAYSCALE DESIGN (Dark Mode)
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

.cloze {
  color: #fff;
  font-weight: 600;
}

/* Inline code */
code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85em;
  background: #1a1a1a;
  color: #ccc;
  padding: 2px 6px;
  border-radius: 3px;
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
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  background: none;
  border: none;
  padding: 0;
  color: #d0d0d0;
  white-space: pre;
  display: block;
}

.code-title {
  color: #777;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

/* Light mode */
.card:not(.nightMode) {
  background: #f5f5f5;
  color: #222;
}
.card:not(.nightMode) .container { background: #fff; border-color: #ddd; }
.card:not(.nightMode) .header { border-color: #ddd; }
.card:not(.nightMode) .question { color: #111; }
.card:not(.nightMode) .answer { color: #333; }
.card:not(.nightMode) code { background: #f0f0f0; color: #333; border-color: #ddd; }
.card:not(.nightMode) pre { background: #f8f8f8; border-color: #ddd; }
.card:not(.nightMode) pre code { color: #333; }
.card:not(.nightMode) .hr { border-color: #ddd; }

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
# MODELS
# ============================================================================

def model_id(name):
    return int(hashlib.md5(name.encode()).hexdigest()[:8], 16)

basic_model = genanki.Model(
    model_id('LeetCode-Basic-v8'),
    'LeetCode Basic',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Tags'},
        {'name': 'Sort'},
    ],
    templates=[{'name': 'Card', 'qfmt': BASIC_FRONT, 'afmt': BASIC_BACK}],
    css=CARD_CSS,
    sort_field_index=3,
)

cloze_model = genanki.Model(
    model_id('LeetCode-Cloze-v8'),
    'LeetCode Cloze',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Tags'},
        {'name': 'Sort'},
    ],
    templates=[{'name': 'Cloze', 'qfmt': CLOZE_TEMPLATE, 'afmt': CLOZE_TEMPLATE}],
    css=CARD_CSS,
    model_type=genanki.Model.CLOZE,
    sort_field_index=3,
)

# ============================================================================
# TOPICS
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

TYPE_ORDER = {
    'concept': 0, 'python': 1, 'pattern': 2, 'code': 3,
    'implementation': 4, 'problem': 5, 'complexity': 6,
    'insight': 7, 'edge_case': 8,
}

def get_card_sort_key(card):
    tags = card.get('Tags', '')
    front = card.get('Front', '')
    subtype = tags.split('::')[1].lower() if '::' in tags else 'code'
    if 'Complete ' in front:
        subtype = 'implementation'
    return (TYPE_ORDER.get(subtype, 5), front[:50])

# ============================================================================
# CODE FORMATTING - Fixed
# ============================================================================

def is_code_card(text):
    """Check if text contains code that should be in a code block."""
    if '<br>' not in text:
        return False
    # Check for code patterns
    code_patterns = ['def ', 'class ', 'for ', 'while ', 'if ', 'return ', '{{c1::', '{{c2::']
    return any(p in text for p in code_patterns)


def format_code_block(text):
    """Convert <br> delimited code to proper code block."""
    # Convert <br> to newlines
    code = text.replace('<br>', '\n')

    # Extract title if present (e.g., "Complete Binary Search:")
    title = None
    title_match = re.match(r'^(Complete [^:]+):\s*', code)
    if title_match:
        title = title_match.group(1)
        code = code[title_match.end():]

    # Clean up the code
    lines = code.split('\n')

    # Remove empty leading/trailing lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    # Find minimum indentation
    min_indent = float('inf')
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, indent)

    # Remove common indentation
    if min_indent > 0 and min_indent < float('inf'):
        lines = [line[min_indent:] if len(line) >= min_indent else line for line in lines]

    # Join and escape HTML (but preserve cloze markers)
    code = '\n'.join(lines)

    # Escape HTML entities but preserve cloze
    # First, protect cloze markers
    cloze_pattern = r'(\{\{c\d+::.*?\}\})'
    clozes = re.findall(cloze_pattern, code)
    for i, c in enumerate(clozes):
        code = code.replace(c, f'__CLOZE_{i}__')

    # Escape HTML
    code = code.replace('&', '&amp;')
    code = code.replace('<', '&lt;')
    code = code.replace('>', '&gt;')

    # Restore cloze markers
    for i, c in enumerate(clozes):
        code = code.replace(f'__CLOZE_{i}__', c)

    # Build HTML
    html = ''
    if title:
        html += f'<div class="code-title">{title}</div>'
    html += f'<pre><code>{code}</code></pre>'

    return html


def format_content(text):
    """Format card content."""
    if not text:
        return text

    # Check if this is a code card
    if is_code_card(text):
        return format_code_block(text)

    # Regular text - format inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    return text


def format_tag(tag):
    if '::' in tag:
        topic, subtype = tag.split('::')
    else:
        topic, subtype = tag, ''

    topic = topic.replace('_', ' ').title()
    topic = topic.replace('1d', '1D').replace('2d', '2D')
    topic = re.sub(r'\bDp\b', 'DP', topic)

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

    all_decks = []
    total_cards = 0

    print("=" * 50)
    print("  LeetCode DSA Deck Generator")
    print("=" * 50)
    print()

    for topic_idx, (topic_file, topic_name) in enumerate(TOPICS):
        filepath = os.path.join(topics_dir, f'{topic_file}.csv')
        if not os.path.exists(filepath):
            continue

        subdeck = genanki.Deck(
            int(hashlib.md5(f'LeetCode DSA::{topic_name}'.encode()).hexdigest()[:12], 16),
            f'LeetCode DSA::{topic_name}'
        )

        with open(filepath, 'r', encoding='utf-8') as f:
            cards = list(csv.DictReader(f))

        cards.sort(key=get_card_sort_key)

        for card_idx, card in enumerate(cards):
            card_type = card.get('Type', 'Basic')
            front = card.get('Front', '')
            back = card.get('Back', '')
            tags = card.get('Tags', topic_file)

            display_tag = format_tag(tags)
            front_fmt = format_content(front)
            back_fmt = format_content(back) if back else ''
            sort_value = str(topic_idx * 10000 + card_idx).zfill(6)

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

    package = genanki.Package(all_decks)
    output_path = os.path.join(script_dir, 'LeetCode_DSA_Deck.apkg')
    package.write_to_file(output_path)

    print()
    print(f"Created: {output_path}")
    print(f"Total: {total_cards} cards")

if __name__ == '__main__':
    main()
