#!/usr/bin/env python3
"""
API Endpoint Discovery Tool
Extracts all FastAPI endpoints from route files and generates comprehensive documentation
"""

import re
from pathlib import Path
from collections import defaultdict
import json

API_ROUTES_DIR = Path("/workspaces/Sectorwars2102/services/gameserver/src/api/routes")

def extract_endpoints_from_file(filepath):
    """Extract all @router decorators and their endpoints from a Python file"""
    try:
        content = filepath.read_text(encoding='utf-8')

        endpoints = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            # Match @router.get, @router.post, etc.
            match = re.match(r'@router\.(get|post|put|patch|delete|websocket)\("([^"]+)"', line)
            if match:
                method = match.group(1).upper()
                path = match.group(2)

                # Try to find the function name on the next few lines
                func_name = None
                for j in range(i+1, min(i+10, len(lines))):
                    func_match = re.match(r'(?:async\s+)?def\s+(\w+)\(', lines[j])
                    if func_match:
                        func_name = func_match.group(1)
                        break

                # Try to find summary/description from docstring or comments
                description = ""
                if func_name:
                    for j in range(i+1, min(i+20, len(lines))):
                        if '"""' in lines[j] or "'''" in lines[j]:
                            # Found docstring
                            doc_start = j
                            for k in range(j, min(j+10, len(lines))):
                                if k > doc_start and ('"""' in lines[k] or "'''" in lines[k]):
                                    description = ' '.join(lines[doc_start:k+1])
                                    description = description.replace('"""', '').replace("'''", '').strip()
                                    break
                            break

                endpoints.append({
                    'method': method,
                    'path': path,
                    'function': func_name or 'unknown',
                    'description': description[:100] if description else ''
                })

        return endpoints
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def categorize_endpoints(all_endpoints):
    """Categorize endpoints by functional area"""
    categories = defaultdict(list)

    for file_name, endpoints in all_endpoints.items():
        # Determine category from filename
        if 'admin' in file_name:
            if 'enhanced' in file_name:
                category = 'Admin Enhanced'
            elif 'comprehensive' in file_name:
                category = 'Admin Comprehensive'
            elif 'ships' in file_name:
                category = 'Admin Ships'
            elif 'combat' in file_name:
                category = 'Admin Combat'
            elif 'economy' in file_name:
                category = 'Admin Economy'
            elif 'colonization' in file_name:
                category = 'Admin Colonization'
            elif 'fleets' in file_name:
                category = 'Admin Fleets'
            elif 'drones' in file_name:
                category = 'Admin Drones'
            elif 'factions' in file_name:
                category = 'Admin Factions'
            elif 'messages' in file_name:
                category = 'Admin Messages'
            else:
                category = 'Admin Core'
        elif 'auth' in file_name:
            category = 'Authentication'
        elif 'user' in file_name:
            category = 'User Management'
        elif 'player' in file_name:
            category = 'Player'
        elif 'combat' in file_name:
            category = 'Combat'
        elif 'economy' in file_name or 'trading' in file_name:
            category = 'Economy & Trading'
        elif 'sector' in file_name:
            category = 'Sectors'
        elif 'planet' in file_name:
            category = 'Planets'
        elif 'fleet' in file_name:
            category = 'Fleets'
        elif 'drone' in file_name:
            category = 'Drones'
        elif 'faction' in file_name:
            category = 'Factions'
        elif 'team' in file_name:
            category = 'Teams'
        elif 'message' in file_name:
            category = 'Messages'
        elif 'ai' in file_name:
            category = 'AI Systems'
        elif 'websocket' in file_name:
            category = 'WebSocket'
        elif 'paypal' in file_name:
            category = 'Payment'
        elif 'mfa' in file_name:
            category = 'Security (MFA)'
        elif 'regional' in file_name or 'nexus' in file_name:
            category = 'Multi-Regional'
        elif 'translation' in file_name:
            category = 'Internationalization'
        elif 'event' in file_name:
            category = 'Events'
        elif 'audit' in file_name:
            category = 'Audit'
        elif 'status' in file_name:
            category = 'System Status'
        elif 'first_login' in file_name:
            category = 'First Login'
        elif 'debug' in file_name:
            category = 'Debug (Dev Only)'
        elif 'test' in file_name:
            category = 'Test (Dev Only)'
        else:
            category = 'Other'

        for endpoint in endpoints:
            categories[category].append({
                'file': file_name,
                **endpoint
            })

    return categories

def main():
    print("🔍 Discovering API endpoints...")

    # Find all route files
    route_files = [f for f in API_ROUTES_DIR.glob("*.py") if f.name != "__init__.py"]

    all_endpoints = {}
    total_count = 0

    for route_file in sorted(route_files):
        endpoints = extract_endpoints_from_file(route_file)
        if endpoints:
            all_endpoints[route_file.stem] = endpoints
            total_count += len(endpoints)
            print(f"  ✓ {route_file.stem}: {len(endpoints)} endpoints")

    print(f"\n📊 Total endpoints discovered: {total_count} across {len(all_endpoints)} files")

    # Categorize
    categories = categorize_endpoints(all_endpoints)

    # Generate markdown report
    output = []
    output.append("# 🚀 SectorWars 2102 - Complete API Endpoint Inventory")
    output.append("")
    output.append(f"**Generated**: 2025-11-16")
    output.append(f"**Total Endpoints**: {total_count}")
    output.append(f"**Route Modules**: {len(all_endpoints)}")
    output.append("")

    output.append("## 📊 Summary by Category")
    output.append("")
    output.append("| Category | Endpoints | Files |")
    output.append("|----------|-----------|-------|")

    for category in sorted(categories.keys()):
        files = set(ep['file'] for ep in categories[category])
        output.append(f"| {category} | {len(categories[category])} | {len(files)} |")

    output.append("")
    output.append("---")
    output.append("")

    # Detailed endpoints by category
    for category in sorted(categories.keys()):
        output.append(f"## {category}")
        output.append("")
        output.append("| Method | Path | Function | Source |")
        output.append("|--------|------|----------|--------|")

        for ep in sorted(categories[category], key=lambda x: (x['method'], x['path'])):
            path_display = ep['path'][:60]
            output.append(f"| {ep['method']} | `{path_display}` | `{ep['function']}` | `{ep['file']}.py` |")

        output.append("")

    output.append("---")
    output.append("*Auto-generated by _discover_api_endpoints.py*")

    # Write markdown
    report_file = Path("/workspaces/Sectorwars2102/DOCS/_API_ENDPOINT_INVENTORY.md")
    report_file.write_text('\n'.join(output), encoding='utf-8')

    # Write JSON
    json_data = {
        'generated': '2025-11-16',
        'total_endpoints': total_count,
        'categories': {cat: [ep for ep in endpoints] for cat, endpoints in categories.items()}
    }
    json_file = Path("/workspaces/Sectorwars2102/DOCS/_api_endpoints.json")
    json_file.write_text(json.dumps(json_data, indent=2), encoding='utf-8')

    print(f"✅ Report generated: {report_file}")
    print(f"✅ JSON saved: {json_file}")
    print(f"\n📋 Category breakdown:")
    for category in sorted(categories.keys()):
        print(f"  {category}: {len(categories[category])} endpoints")

if __name__ == '__main__':
    main()
