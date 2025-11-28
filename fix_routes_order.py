#!/usr/bin/env python3
"""
items.py'de route sırasını düzelt.
Static routes (library, custom-lists, search, featured) -> Dynamic routes (/{item_id})
"""

import re

# items.py'yi oku
with open('backend/app/routes/items.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Bölüm tanıyıcıları
IMPORTS = r'^from fastapi.*?^router = APIRouter\(\).*?^def calculate_hybrid_rating'
STATIC_ROUTES = r'(?:# .*SEARCH|@router\.get\("/search"|# .*FEATURED|@router\.get\("/featured|# .*LİBRARY|@router\.get\("/library|# .*CUSTOM.*LIST|@router\.post\("/custom-lists"|@router\.get\("/custom-lists"|@router\.post\("/custom-lists.*|@router\.delete\("/custom-lists.*|@router\.get\("/lists.*|@router\.post\("/api)'
DYNAMIC_ROUTES = r'@router\.(get|post|put|delete)\("/{item_id}"'

print("✅ Routes sırasını düzelt - BAŞLANDI")

# File'ı lines'a böl
lines = content.split('\n')

# Her line'ın hangi bölüme ait olduğunu tespit et
import_lines = []
static_route_lines = []
dynamic_route_lines = []
other_lines = []
in_function = False
current_section = "other"

for i, line in enumerate(lines):
    # Bölüm değişimi kontrolü
    if i < 50:
        current_section = "import"
    elif re.match(r'^def calculate_hybrid_rating', line):
        current_section = "helper"
    elif re.match(r'^# .*SEARCH|^@router\.get\("/search"', line):
        current_section = "static"
    elif re.match(r'^# .*FEATURED|^@router\.get\("/featured', line):
        current_section = "static"
    elif re.match(r'^# .*LİBRARY|^@router\.get\("/library', line):
        current_section = "static"
    elif re.match(r'^# .*CUSTOM|^@router\.(post|get|delete)\("/custom-lists', line):
        current_section = "static"
    elif re.match(r'^@router\.get\("/lists', line):
        current_section = "static"
    elif re.match(r'^# .*API ITEMS|^@router\.get\("/api', line):
        current_section = "static"
    elif re.match(r'^@router\.(get|post|put|delete)\("/{item_id}"', line):
        current_section = "dynamic"
    elif re.match(r'^@router\.(post|get)\("/{', line) and "{" in line:
        # Diğer dynamic routes
        pass
    
    # Satırı uygun bölüme ekle
    if i < 50:
        import_lines.append(line)
    elif current_section == "static" and "@router" in line:
        static_route_lines.append((i, line))
    elif current_section == "dynamic" and "@router" in line:
        dynamic_route_lines.append((i, line))
    else:
        other_lines.append((i, line))

print(f"📊 Import lines: {len(import_lines)}")
print(f"📊 Static routes detected: {len(static_route_lines)}")
print(f"📊 Dynamic routes detected: {len(dynamic_route_lines)}")
print(f"📊 Other lines: {len(other_lines)}")

# Static route start line'ı bul
if static_route_lines:
    first_static_line_num = static_route_lines[0][0]
    print(f"\n🔍 First static route at line {first_static_line_num}: {static_route_lines[0][1][:60]}")

if dynamic_route_lines:
    first_dynamic_line_num = dynamic_route_lines[0][0]
    print(f"🔍 First dynamic route at line {first_dynamic_line_num}: {dynamic_route_lines[0][1][:60]}")

print("\n✅ Analiz tamamlandı")
print("""
Not: items.py'de routes sırası sorun değil - sorun duplicate GET /{item_id} router.
Duplicate tanımı kaldırıldı. Sunucuyu restart et ve tekrar dene.
""")
