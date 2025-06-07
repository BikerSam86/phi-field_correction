import re, json, os

# Paths to source files
FILES = {
    'README': 'README.md',
    'INDEX': 'index.md',
    'FINAL': 'Final_Paper_Draft.md',
    'OUTPUT': 'Output_Comparison.md',
    'AXIOMS': 'New_Axioms.md'
}

# Helper function to read file

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

data = {}

# Parse axioms from New_Axioms.md
text = read_file(FILES['AXIOMS'])
axiom_pattern = re.compile(r"^## Axiom (\d+):([^\n]*)\n\*\*(.*?)\*\*", re.MULTILINE)
axioms = []
for num, title, desc in axiom_pattern.findall(text):
    axioms.append({'id': int(num), 'title': title.strip(), 'statement': desc.strip()})
data['axioms'] = axioms

# Parse core equations from README
text = read_file(FILES['README'])
core_eq = []
core_section = re.search(r"### 🧮 Core Corrected Equations(.*?)(---|$)", text, re.S)
if core_section:
    lines = core_section.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r"\d+\.\s*\*\*(.*?)\*\*:?", line)
        if m:
            equation = ''
            if i + 1 < len(lines):
                eq_line = lines[i + 1].strip()
                if eq_line.startswith('`') and eq_line.endswith('`'):
                    equation = eq_line.strip('`')
                    i += 1
            core_eq.append({'name': m.group(1), 'equation': equation})
        else:
            m2 = re.match(r"-\s*(.*?)`([^`]+)`", line)
            if m2 and core_eq:
                core_eq[-1].setdefault('corrections', []).append({'desc': m2.group(1).strip(), 'equation': m2.group(2)})
        i += 1
data['core_equations'] = core_eq

# Parse improvements table from README
improv_match = re.search(r"### 📈 Demonstrated Improvements.*?\n(\|.*\n)+", text, re.S)
if improv_match:
    table_lines = [l.strip() for l in improv_match.group(0).splitlines() if l.strip().startswith('|')]
    headers = [h.strip() for h in table_lines[0].strip('|').split('|')]
    improvements = []
    for row in table_lines[2:]:
        cells = [c.strip() for c in row.strip('|').split('|')]
        if len(cells) == len(headers):
            improvements.append(dict(zip(headers, cells)))
    data['improvements'] = improvements

# Parse predictions table from Final_Paper_Draft
text = read_file(FILES['FINAL'])
pred_match = re.search(r"Experimental Predictions.*?\n(\|.*\n)+", text)
if pred_match:
    lines = [l.strip() for l in pred_match.group(0).splitlines() if l.strip().startswith('|')]
    headers = [h.strip() for h in lines[1].strip('|').split('|')]
    preds = []
    for row in lines[2:]:
        cells = [c.strip() for c in row.strip('|').split('|')]
        if len(cells) == len(headers):
            preds.append(dict(zip(headers, cells)))
    data['predictions'] = preds

# Parse glossary from Final_Paper_Draft
gloss_match = re.search(r"## Glossary of Symbols(.*?)(##|$)", text, re.S)
if gloss_match:
    lines = [l.strip('* ').strip() for l in gloss_match.group(1).splitlines() if l.strip().startswith('*')]
    glossary = {}
    for line in lines:
        if ':' in line:
            key, val = line.split(':',1)
            glossary[key.strip()] = val.strip()
    data['glossary'] = glossary

# Parse Output_Comparison tables
out_text = read_file(FILES['OUTPUT'])
# Helper to parse markdown table
def parse_table(section_title):
    pattern = rf"{re.escape(section_title)}.*?(\n\|.*\n)+"
    m = re.search(pattern, out_text, re.S)
    if not m:
        return []
    lines = [l.strip() for l in m.group(0).splitlines() if l.strip().startswith('|')]
    headers = [h.strip() for h in lines[0].strip('|').split('|')]
    rows = []
    for row in lines[2:]:
        cells = [c.strip() for c in row.strip('|').split('|')]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows

data['energy_levels'] = parse_table('## 1. Energy Levels')
data['atomic_radii'] = parse_table('## 2. Atomic Radii')
data['angular_momentum'] = parse_table('## 3. Angular Momentum')
data['orbital_velocity'] = parse_table('## 4. Orbital Velocity')
data['ionization_energy'] = parse_table('## 5. Ionization Energy')
data['universal_constants'] = parse_table('## 6. Universal Constants')

# Write JSON
os.makedirs('parsed_data', exist_ok=True)
with open('parsed_data/useful_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print('Database built at parsed_data/useful_data.json')
