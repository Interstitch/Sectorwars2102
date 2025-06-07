#!/usr/bin/env python3
"""
Test script to verify our translation implementation and import translations.
This script can run without the full app setup.
"""

import json
import os
from pathlib import Path

def load_translation_file(file_path):
    """Load a translation JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def count_translation_keys(data, prefix=""):
    """Recursively count translation keys in a nested dict."""
    count = 0
    for key, value in data.items():
        current_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            count += count_translation_keys(value, current_key)
        else:
            count += 1
    return count

def validate_translation_structure(source_data, target_data, source_lang, target_lang):
    """Validate that translation structure matches between languages."""
    def get_structure(data, prefix=""):
        structure = set()
        for key, value in data.items():
            current_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                structure.update(get_structure(value, current_key))
            else:
                structure.add(current_key)
        return structure
    
    source_keys = get_structure(source_data)
    target_keys = get_structure(target_data)
    
    missing_keys = source_keys - target_keys
    extra_keys = target_keys - source_keys
    
    if missing_keys:
        print(f"⚠️  Missing keys in {target_lang}: {sorted(list(missing_keys))[:5]}...")
    if extra_keys:
        print(f"⚠️  Extra keys in {target_lang}: {sorted(list(extra_keys))[:5]}...")
    
    return len(missing_keys) == 0 and len(extra_keys) == 0

def main():
    """Main test function."""
    print("🌍 Testing Internationalization Implementation")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    locales_path = base_path / "shared" / "i18n" / "locales"
    namespaces_path = base_path / "shared" / "i18n" / "namespaces"
    
    # Load English base files
    print("\n📖 Loading English base translations...")
    en_common = load_translation_file(locales_path / "en.json")
    en_auth = load_translation_file(namespaces_path / "auth.json")
    en_admin = load_translation_file(namespaces_path / "admin.json")
    en_game = load_translation_file(namespaces_path / "game.json")
    
    if not all([en_common, en_auth, en_admin, en_game]):
        print("❌ Failed to load English base files")
        return
    
    # Count total keys
    total_keys = (
        count_translation_keys(en_common) +
        count_translation_keys(en_auth) +
        count_translation_keys(en_admin) +
        count_translation_keys(en_game)
    )
    print(f"✅ English base: {total_keys} translation keys")
    
    # Test available languages
    languages = [
        ("es", "Spanish", "🇪🇸"),
        ("fr", "French", "🇫🇷"),
        ("zh", "Chinese Simplified", "🇨🇳"),
        ("pt", "Portuguese", "🇧🇷"),
    ]
    
    results = {}
    
    for lang_code, lang_name, flag in languages:
        print(f"\n{flag} Testing {lang_name} ({lang_code})...")
        
        # Load translated files
        lang_common = load_translation_file(locales_path / f"{lang_code}.json")
        lang_auth = load_translation_file(namespaces_path / lang_code / "auth.json")
        lang_admin = load_translation_file(namespaces_path / lang_code / "admin.json")
        lang_game = load_translation_file(namespaces_path / lang_code / "game.json")
        
        if not all([lang_common, lang_auth, lang_admin, lang_game]):
            print(f"❌ Missing translation files for {lang_name}")
            results[lang_code] = {"status": "incomplete", "keys": 0}
            continue
        
        # Count keys
        lang_keys = (
            count_translation_keys(lang_common) +
            count_translation_keys(lang_auth) +
            count_translation_keys(lang_admin) +
            count_translation_keys(lang_game)
        )
        
        # Validate structure
        structure_valid = (
            validate_translation_structure(en_common["common"], lang_common["common"], "en", lang_code) and
            validate_translation_structure(en_auth, lang_auth, "en", lang_code) and
            validate_translation_structure(en_admin, lang_admin, "en", lang_code) and
            validate_translation_structure(en_game, lang_game, "en", lang_code)
        )
        
        completion = (lang_keys / total_keys) * 100
        status = "complete" if completion == 100 and structure_valid else "partial"
        
        print(f"   📊 Keys: {lang_keys}/{total_keys} ({completion:.1f}%)")
        print(f"   🎯 Status: {status}")
        
        results[lang_code] = {
            "status": status,
            "keys": lang_keys,
            "completion": completion,
            "structure_valid": structure_valid
        }
    
    # Summary
    print("\n" + "=" * 50)
    print("📈 SUMMARY")
    print("=" * 50)
    print(f"Base language (English): {total_keys} keys")
    
    completed_languages = [lang for lang, data in results.items() if data["status"] == "complete"]
    partial_languages = [lang for lang, data in results.items() if data["status"] == "partial"]
    incomplete_languages = [lang for lang, data in results.items() if data["status"] == "incomplete"]
    
    print(f"✅ Complete translations: {len(completed_languages)} languages")
    if completed_languages:
        print(f"   Languages: {', '.join(completed_languages)}")
    
    if partial_languages:
        print(f"⚠️  Partial translations: {len(partial_languages)} languages")
        print(f"   Languages: {', '.join(partial_languages)}")
    
    if incomplete_languages:
        print(f"❌ Incomplete translations: {len(incomplete_languages)} languages")
        print(f"   Languages: {', '.join(incomplete_languages)}")
    
    total_translated_keys = sum(data["keys"] for data in results.values())
    total_possible_keys = total_keys * len(results)
    overall_completion = (total_translated_keys / total_possible_keys) * 100 if total_possible_keys > 0 else 0
    
    print(f"\n🎯 Overall completion: {overall_completion:.1f}%")
    print(f"📊 Total translated keys: {total_translated_keys:,}")
    
    if overall_completion >= 75:
        print("🎉 Internationalization system is ready for production!")
    elif overall_completion >= 50:
        print("🚧 Good progress, continue adding translations")
    else:
        print("⚠️  More translation work needed")

if __name__ == "__main__":
    main()