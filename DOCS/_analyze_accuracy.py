#!/usr/bin/env python3
"""
Documentation Accuracy Analyzer
Compares documentation files against actual codebase implementation
"""

import os
import re
from pathlib import Path
from datetime import datetime, timedelta
import json

DOCS_ROOT = Path(__file__).parent
PROJECT_ROOT = DOCS_ROOT.parent
GAMESERVER_MODELS = PROJECT_ROOT / "services/gameserver/src/models"
GAMESERVER_API = PROJECT_ROOT / "services/gameserver/src/api"

def check_model_documentation_accuracy(doc_path):
    """Check if a data model doc matches the actual model file"""
    doc_name = doc_path.stem
    model_file = GAMESERVER_MODELS / f"{doc_name}.py"

    if not model_file.exists():
        return 0, f"Model file {doc_name}.py not found"

    try:
        doc_content = doc_path.read_text(encoding='utf-8')
        model_content = model_file.read_text(encoding='utf-8')

        # Extract field names from doc (looking for common patterns)
        doc_fields = set(re.findall(r'^\s*[-*]\s*`?(\w+)`?:', doc_content, re.MULTILINE))
        doc_fields.update(re.findall(r'^\s*(\w+)\s*=\s*Column', doc_content, re.MULTILINE))

        # Extract field names from model
        model_fields = set(re.findall(r'^\s+(\w+)\s*=\s*Column', model_content, re.MULTILINE))

        if not doc_fields:
            return 50, "Documentation format unclear, manual review needed"

        if not model_fields:
            return 30, "Could not parse model fields"

        # Calculate overlap
        matching = doc_fields & model_fields
        doc_only = doc_fields - model_fields
        model_only = model_fields - doc_fields

        if len(model_fields) == 0:
            return 30, "Model appears empty"

        accuracy = (len(matching) / len(model_fields)) * 100

        notes = []
        if doc_only:
            notes.append(f"Docs mention fields not in model: {', '.join(list(doc_only)[:5])}")
        if model_only:
            notes.append(f"Model has undocumented fields: {', '.join(list(model_only)[:5])}")

        note = "; ".join(notes) if notes else "Fields match well"
        return int(accuracy), note

    except Exception as e:
        return 30, f"Error analyzing: {str(e)}"

def check_aispec_accuracy(doc_path):
    """Check AISPEC file accuracy"""
    try:
        content = doc_path.read_text(encoding='utf-8')
        issues = []

        # Check for /app/ vs /src/ path issues
        if '/app/' in content and doc_path.name != 'AI_Specification_Doc.aispec':
            issues.append("Uses /app/ paths (should be /src/)")

        # Check for specific known issues
        if doc_path.name == 'Database.aispec':
            if 'id: Integer' in content:
                issues.append("User.id documented as Integer (actually UUID)")
            if 'password_hash: String' in content:
                issues.append("User.password_hash documented (moved to separate tables)")
            return 25, "Critical inaccuracies: " + "; ".join(issues)

        if doc_path.name == 'AuthSystem.aispec':
            if issues:
                return 70, "; ".join(issues)
            return 85, "Mostly accurate but paths need verification"

        # Default for other AISPEC files
        if issues:
            return 60, "; ".join(issues)
        return 75, "Needs manual verification against code"

    except Exception as e:
        return 50, f"Error reading file: {str(e)}"

def check_feature_documentation(doc_path):
    """Check if feature documentation matches implementation"""
    doc_name = doc_path.stem.lower()

    # Check for signs of implementation
    try:
        content = doc_path.read_text(encoding='utf-8')

        # Look for implementation status markers
        if 'NOT IMPLEMENTED' in content.upper() or 'PLANNED' in content.upper():
            return 100, "Accurately marked as planned/not implemented"

        if 'COMPLETE' in content.upper() or 'IMPLEMENTED' in content.upper():
            # TODO: Could verify this claim
            return 85, "Claims to be implemented - needs code verification"

        # Check modification date
        stat = doc_path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime)
        age_days = (datetime.now() - modified).days

        if age_days > 180:
            return 60, f"Not updated in {age_days} days - may be outdated"
        elif age_days > 90:
            return 75, f"Last updated {age_days} days ago"
        else:
            return 85, "Recently updated"

    except Exception as e:
        return 50, f"Error: {str(e)}"

def analyze_file(filepath):
    """Analyze a single documentation file for accuracy"""
    rel_path = str(filepath.relative_to(DOCS_ROOT))

    # Categorize file
    if rel_path.startswith('ARCHIVE/'):
        return 100, "N/A - Archive (historical record)", "ARCHIVE"

    if rel_path.startswith('retrospectives/'):
        return 100, "N/A - Retrospective (historical)", "RETRO"

    if 'AUDIT' in rel_path:
        # Check if audit is recent
        stat = filepath.stat()
        modified = datetime.fromtimestamp(stat.st_mtime)
        age_days = (datetime.now() - modified).days
        if age_days > 180:
            return 70, f"Audit from {age_days} days ago - may need update", "AUDIT"
        return 90, "Recent audit", "AUDIT"

    if rel_path.startswith('SPECS/'):
        accuracy, note = check_aispec_accuracy(filepath)
        return accuracy, note, "SPEC"

    if 'data-models/' in rel_path and filepath.name != 'README.md':
        # Individual data model docs
        if 'multi-regional' in filepath.name or 'comprehensive' in filepath.name:
            return 75, "Overview doc - needs manual review", "ARCH"
        accuracy, note = check_model_documentation_accuracy(filepath)
        return accuracy, note, "ARCH"

    if rel_path.startswith('FEATURES/'):
        accuracy, note = check_feature_documentation(filepath)
        return accuracy, note, "FEAT"

    if rel_path.startswith('API/'):
        return 70, "API doc - needs endpoint verification", "API"

    if rel_path.startswith('STATUS/'):
        stat = filepath.stat()
        modified = datetime.fromtimestamp(stat.st_mtime)
        age_days = (datetime.now() - modified).days
        if age_days > 30:
            return 50, f"Status doc not updated in {age_days} days", "STATUS"
        return 85, "Recent status update", "STATUS"

    if rel_path.startswith('GUIDES/'):
        return 75, "Guide - needs process verification", "GUIDE"

    if rel_path.startswith('troubleshooting/'):
        return 80, "Troubleshooting guide", "TROUBLE"

    # Root level files
    if filepath.name == 'README.md':
        return 70, "Needs manual review for broken links", "ROOT"

    if filepath.name == 'brainstorm.md':
        return 100, "N/A - Brainstorming doc", "ROOT"

    return 60, "Needs manual review", "OTHER"

def get_recommendation(accuracy, category, note):
    """Generate action recommendation based on accuracy"""
    if category in ['ARCHIVE', 'RETRO']:
        return "KEEP - Historical record"

    if accuracy >= 90:
        return "KEEP - Accurate"
    elif accuracy >= 75:
        return "REVIEW - Minor updates needed"
    elif accuracy >= 50:
        return "UPDATE - Significant changes needed"
    elif accuracy >= 30:
        return "REWRITE - Major inaccuracies"
    else:
        return "DELETE/REWRITE - Critically wrong"

def main():
    print("🔍 Analyzing documentation accuracy...")

    # Find all docs
    files = []
    for ext in ['*.md', '*.aispec']:
        files.extend(DOCS_ROOT.rglob(ext))

    # Exclude generated files
    files = [f for f in files if not any(x in str(f) for x in ['_generate_inventory', '_INVENTORY', '_AUDIT_FINDINGS', '_analyze_accuracy'])]

    results = []
    for filepath in sorted(files):
        accuracy, note, category = analyze_file(filepath)
        recommendation = get_recommendation(accuracy, category, note)

        rel_path = str(filepath.relative_to(DOCS_ROOT))
        stat = filepath.stat()
        modified = datetime.fromtimestamp(stat.st_mtime)

        results.append({
            'path': rel_path,
            'category': category,
            'accuracy': accuracy,
            'note': note,
            'recommendation': recommendation,
            'modified': modified.strftime('%Y-%m-%d'),
            'size_kb': stat.st_size / 1024
        })

    # Generate markdown report
    output = []
    output.append("# 📊 Documentation Accuracy Report")
    output.append("")
    output.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"**Files Analyzed**: {len(results)}")
    output.append("")
    output.append("## Accuracy Scale")
    output.append("")
    output.append("- **90-100%**: Accurate, minimal changes needed")
    output.append("- **75-89%**: Mostly accurate, minor updates needed")
    output.append("- **50-74%**: Significantly outdated, needs review")
    output.append("- **30-49%**: Major inaccuracies, needs rewrite")
    output.append("- **0-29%**: Critically wrong or obsolete")
    output.append("- **N/A**: Archive/historical docs (not compared to current code)")
    output.append("")

    # Summary statistics
    avg_accuracy = sum(r['accuracy'] for r in results if r['category'] not in ['ARCHIVE', 'RETRO']) / len([r for r in results if r['category'] not in ['ARCHIVE', 'RETRO']])
    critical = [r for r in results if r['accuracy'] < 30 and r['category'] not in ['ARCHIVE', 'RETRO']]
    needs_update = [r for r in results if 30 <= r['accuracy'] < 75 and r['category'] not in ['ARCHIVE', 'RETRO']]

    output.append(f"## Summary Statistics")
    output.append("")
    output.append(f"- **Average Accuracy** (non-archive): {avg_accuracy:.1f}%")
    output.append(f"- **Critically Wrong** (0-29%): {len(critical)} files")
    output.append(f"- **Needs Update** (30-74%): {len(needs_update)} files")
    output.append("")

    # Group by recommendation
    output.append("## 🚨 Action Required - Priority Order")
    output.append("")

    for rec_type in ["DELETE/REWRITE - Critically wrong", "REWRITE - Major inaccuracies", "UPDATE - Significant changes needed", "REVIEW - Minor updates needed", "KEEP - Accurate", "KEEP - Historical record"]:
        matching = [r for r in results if r['recommendation'] == rec_type]
        if matching:
            output.append(f"### {rec_type} ({len(matching)} files)")
            output.append("")
            output.append("| File | Category | Accuracy | Notes | Modified |")
            output.append("|------|----------|----------|-------|----------|")
            for r in sorted(matching, key=lambda x: x['accuracy']):
                output.append(f"| `{r['path']}` | {r['category']} | **{r['accuracy']}%** | {r['note'][:80]} | {r['modified']} |")
            output.append("")

    output.append("## 📋 Complete File Index")
    output.append("")
    output.append("| File | Category | Accuracy | Recommendation | Notes | Modified |")
    output.append("|------|----------|----------|----------------|-------|----------|")

    for r in sorted(results, key=lambda x: (x['category'], x['path'])):
        acc_icon = "🔴" if r['accuracy'] < 30 else "🟡" if r['accuracy'] < 75 else "✅"
        output.append(f"| `{r['path']}` | {r['category']} | {acc_icon} **{r['accuracy']}%** | {r['recommendation']} | {r['note'][:60]} | {r['modified']} |")

    output.append("")
    output.append("---")
    output.append("*Auto-generated by _analyze_accuracy.py*")

    # Write report
    report_file = DOCS_ROOT / '_ACCURACY_REPORT.md'
    report_file.write_text('\n'.join(output), encoding='utf-8')

    # Save JSON
    json_file = DOCS_ROOT / '_accuracy_report.json'
    json_file.write_text(json.dumps(results, indent=2), encoding='utf-8')

    print(f"✅ Report generated: {report_file}")
    print(f"✅ JSON data saved: {json_file}")
    print(f"📊 Average accuracy: {avg_accuracy:.1f}%")
    print(f"🔴 Critical issues: {len(critical)} files")
    print(f"🟡 Needs update: {len(needs_update)} files")

if __name__ == '__main__':
    main()
