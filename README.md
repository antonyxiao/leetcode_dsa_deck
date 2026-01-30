# LeetCode DSA Anki Deck

A comprehensive Anki flashcard deck for LeetCode interview preparation covering 18 essential data structures and algorithms topics.

## Stats
- **Total Cards:** ~1,170 atomic flashcards
- **Topics:** 18 DSA categories
- **Card Types:** Cloze deletions and Basic Q&A

## Topics Covered

| # | Topic | Cards |
|---|-------|-------|
| 1 | Arrays & Hashing | 76 |
| 2 | Two Pointers | 66 |
| 3 | Stack | 73 |
| 4 | Binary Search | 71 |
| 5 | Sliding Window | 64 |
| 6 | Linked List | 70 |
| 7 | Trees | 75 |
| 8 | Tries | 50 |
| 9 | Backtracking | 62 |
| 10 | Heap/Priority Queue | 67 |
| 11 | Graphs | 69 |
| 12 | 1-D Dynamic Programming | 68 |
| 13 | Intervals | 51 |
| 14 | Greedy | 59 |
| 15 | Advanced Graphs | 60 |
| 16 | 2-D Dynamic Programming | 61 |
| 17 | Bit Manipulation | 60 |
| 18 | Math & Geometry | 68 |

## Card Categories

Each topic includes:
1. **Definitions & Concepts** - Core data structure/algorithm understanding
2. **Python Syntax** - Essential imports, methods, and idioms
3. **Complexity Analysis** - Time and space complexity
4. **Pattern Recognition** - "When you see X, think Y" cards
5. **Code Patterns** - Key implementation lines and templates
6. **Problem Approaches** - How to tackle specific LeetCode problems

## Import Instructions

### Method 1: Import Complete Deck
1. Open Anki Desktop
2. Go to **File → Import**
3. Select `leetcode_dsa_complete.csv`
4. Configure import settings:
   - **Type:** "Basic" and "Cloze" (mixed)
   - **Deck:** Create new deck "LeetCode DSA"
   - **Fields separated by:** Comma
   - **Field mapping:**
     - Field 1 → Note Type
     - Field 2 → Front/Text
     - Field 3 → Back
     - Field 4 → Tags
   - Check "Allow HTML in fields"
5. Click **Import**

### Method 2: Import Individual Topics
Import files from the `topics/` folder separately to create sub-decks:
- `topics/01_arrays_hashing.csv` → "LeetCode DSA::Arrays & Hashing"
- `topics/02_two_pointers.csv` → "LeetCode DSA::Two Pointers"
- etc.

## Note Types Required

Create these note types in Anki before importing:

### Basic Note Type
- Front field
- Back field

### Cloze Note Type
- Text field (with cloze deletions like `{{c1::hidden text}}`)

## Anki Settings Recommendations

### New Cards
- New cards/day: 20-30
- Learning steps: 1m 10m 1d
- Graduating interval: 3 days

### Reviews
- Maximum reviews/day: 200
- Enable "Bury related new cards"

## Tags Structure

Cards are tagged by topic and subtopic:
- `arrays_hashing::complexity`
- `arrays_hashing::python`
- `arrays_hashing::pattern`
- `arrays_hashing::code`
- `arrays_hashing::problem`

Use Anki's filtered decks or tag browser to study specific subtopics.

## Study Tips

1. **Study by topic** - Master one topic before moving to the next
2. **Practice after review** - Solve related LeetCode problems after reviewing cards
3. **Use code cards actively** - Try to write the code before revealing
4. **Focus on patterns** - Pattern recognition cards help identify problem types quickly

## File Structure

```
leetcode_dsa_deck/
├── leetcode_dsa_complete.csv    # Complete deck (all topics)
├── topics/                       # Individual topic files
│   ├── 01_arrays_hashing.csv
│   ├── 02_two_pointers.csv
│   ├── 03_stack.csv
│   ├── 04_binary_search.csv
│   ├── 05_sliding_window.csv
│   ├── 06_linked_list.csv
│   ├── 07_trees.csv
│   ├── 08_tries.csv
│   ├── 09_backtracking.csv
│   ├── 10_heap_priority_queue.csv
│   ├── 11_graphs.csv
│   ├── 12_1d_dp.csv
│   ├── 13_intervals.csv
│   ├── 14_greedy.csv
│   ├── 15_advanced_graphs.csv
│   ├── 16_2d_dp.csv
│   ├── 17_bit_manipulation.csv
│   └── 18_math_geometry.csv
└── README.md
```

## Contributing

Feel free to suggest new cards or improvements via pull requests.

## License

This flashcard deck is provided for educational purposes.
