# Documentation Tools

Utility scripts and generated data files for documentation maintenance.

## Scripts

| Script | Purpose |
|--------|---------|
| `_discover_api_endpoints.py` | Auto-discovers API endpoints from gameserver source code |
| `_analyze_accuracy.py` | Analyzes documentation accuracy against implementation |
| `_generate_inventory.py` | Generates comprehensive file inventory |

## Generated Files

| File | Description |
|------|-------------|
| `_API_ENDPOINT_INVENTORY.md` | Human-readable endpoint inventory |
| `_api_endpoints.json` | Machine-readable endpoint data |
| `_accuracy_report.json` | Documentation accuracy analysis |
| `_inventory.json` | Complete documentation inventory |

## Usage

```bash
# Run from DOCS/_TOOLS directory
python3 _discover_api_endpoints.py
python3 _analyze_accuracy.py
python3 _generate_inventory.py
```

---
*Last Updated: 2025-12-09*
