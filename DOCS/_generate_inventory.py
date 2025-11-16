#!/usr/bin/env python3
"""
Documentation Inventory Generator
Creates comprehensive index of all documentation files with metadata
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import json

DOCS_ROOT = Path(__file__).parent
CUTOFF_DATE = datetime.now() - timedelta(days=180)  # 6 months

def get_file_metadata(filepath):
    """Extract metadata from a documentation file"""
    stat = filepath.stat()
    modified = datetime.fromtimestamp(stat.st_mtime)
    size = stat.st_size

    # Count words
    try:
        content = filepath.read_text(encoding='utf-8')
        words = len(re.findall(r'\b\w+\b', content))

        # Find cross-references to other docs
        doc_refs = re.findall(r'\[.*?\]\(((?:\.\.\/)*[^)]*\.(?:md|aispec))\)', content)
        doc_refs = list(set(doc_refs))  # unique refs

    except Exception as e:
        words = 0
        doc_refs = []

    return {
        'path': str(filepath.relative_to(DOCS_ROOT)),
        'size': size,
        'modified': modified,
        'words': words,
        'stale': modified < CUTOFF_DATE,
        'references': doc_refs
    }

def categorize_file(path_str):
    """Categorize file by directory"""
    if path_str.startswith('SPECS/'):
        return 'SPEC'
    elif path_str.startswith('API/'):
        return 'API'
    elif path_str.startswith('ARCHITECTURE/'):
        return 'ARCH'
    elif path_str.startswith('FEATURES/'):
        return 'FEAT'
    elif path_str.startswith('GUIDES/'):
        return 'GUIDE'
    elif path_str.startswith('STATUS/'):
        return 'STATUS'
    elif path_str.startswith('ARCHIVE/'):
        return 'ARCHIVE'
    elif path_str.startswith('AUDIT/'):
        return 'AUDIT'
    elif path_str.startswith('retrospectives/'):
        return 'RETRO'
    elif path_str.startswith('troubleshooting/'):
        return 'TROUBLE'
    else:
        return 'ROOT'

def main():
    print("🔍 Scanning documentation files...")

    # Find all .md and .aispec files
    files = []
    for ext in ['*.md', '*.aispec']:
        files.extend(DOCS_ROOT.rglob(ext))

    # Exclude the generated files
    files = [f for f in files if '_generate_inventory.py' not in str(f) and '_AUDIT_FINDINGS.md' not in str(f)]

    # Generate metadata
    inventory = []
    for filepath in sorted(files):
        metadata = get_file_metadata(filepath)
        metadata['category'] = categorize_file(metadata['path'])
        inventory.append(metadata)

    # Generate statistics
    total_files = len(inventory)
    total_words = sum(item['words'] for item in inventory)
    stale_count = sum(1 for item in inventory if item['stale'])

    categories = {}
    for item in inventory:
        cat = item['category']
        categories[cat] = categories.get(cat, 0) + 1

    # Generate markdown table
    print("📝 Generating inventory table...")

    output = []
    output.append("# 📚 SectorWars 2102 Documentation Inventory")
    output.append("")
    output.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"**Total Files**: {total_files}")
    output.append(f"**Total Words**: {total_words:,}")
    output.append(f"**Stale Files** (>6 months): {stale_count}")
    output.append("")

    output.append("## 📊 Category Breakdown")
    output.append("")
    output.append("| Category | Count | Description |")
    output.append("|----------|-------|-------------|")
    cat_descriptions = {
        'SPEC': 'AISPEC machine-readable specifications',
        'API': 'API documentation and specifications',
        'ARCH': 'Architecture and data model docs',
        'FEAT': 'Feature specifications',
        'GUIDE': 'Implementation guides',
        'STATUS': 'Development status tracking',
        'ARCHIVE': 'Historical decisions and completed work',
        'AUDIT': 'Security and quality audits',
        'RETRO': 'Retrospectives',
        'TROUBLE': 'Troubleshooting guides',
        'ROOT': 'Root-level docs'
    }
    for cat in sorted(categories.keys()):
        desc = cat_descriptions.get(cat, '')
        output.append(f"| {cat} | {categories[cat]} | {desc} |")
    output.append("")

    output.append("## 📋 Complete File Inventory")
    output.append("")
    output.append("| Category | File | Size | Words | Modified | Status |")
    output.append("|----------|------|------|-------|----------|--------|")

    for item in inventory:
        cat = item['category']
        path = item['path']
        size_kb = item['size'] / 1024
        words = item['words']
        modified = item['modified'].strftime('%Y-%m-%d')

        # Status indicators
        status_icons = []
        if item['stale']:
            status_icons.append('⏰ STALE')
        if len(item['references']) > 0:
            status_icons.append(f'🔗{len(item["references"])}')

        status = ' '.join(status_icons) if status_icons else '✅'

        output.append(f"| {cat} | `{path}` | {size_kb:.1f}KB | {words:,} | {modified} | {status} |")

    output.append("")
    output.append("## 🔗 Cross-Reference Map")
    output.append("")
    output.append("Files with cross-references to other documentation:")
    output.append("")

    for item in inventory:
        if item['references']:
            output.append(f"### `{item['path']}`")
            for ref in item['references']:
                output.append(f"- {ref}")
            output.append("")

    output.append("---")
    output.append("*Auto-generated by _generate_inventory.py*")

    # Write to file
    inventory_file = DOCS_ROOT / '_INVENTORY.md'
    inventory_file.write_text('\n'.join(output), encoding='utf-8')

    # Also save JSON for programmatic access
    json_file = DOCS_ROOT / '_inventory.json'
    json_data = {
        'generated': datetime.now().isoformat(),
        'statistics': {
            'total_files': total_files,
            'total_words': total_words,
            'stale_count': stale_count,
            'categories': categories
        },
        'files': inventory
    }
    json_file.write_text(json.dumps(json_data, indent=2, default=str), encoding='utf-8')

    print(f"✅ Inventory generated: {inventory_file}")
    print(f"✅ JSON data saved: {json_file}")
    print(f"📊 Summary: {total_files} files, {total_words:,} words, {stale_count} stale")

if __name__ == '__main__':
    main()
