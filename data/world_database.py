"""Comprehensive world database — 195 UN member states + key entities.

Every country has real-world-calibrated data. Leaders are dynamic —
they change with elections, coups, and deaths. Historical leaders
are tracked per-era.
"""

from __future__ import annotations

# fmt: off
# (code, name, region, population_M, gdp_T, mil_power, nuclear, stability, democracy, tech, gov_type)
COUNTRIES_RAW: list[tuple] = [
    # ═══════════════════ NORTH AMERICA ═══════════════════
    ("US", "United States", "North America", 335, 28.0, 0.95, True, 0.65, 0.75, 0.92, "Federal Presidential Republic"),
    ("CA", "Canada", "North America", 40, 2.1, 0.30, False, 0.85, 0.90, 0.82, "Federal Parliamentary Democracy"),
    ("MX", "Mexico", "North America", 130, 1.8, 0.25, False, 0.45, 0.50, 0.50, "Federal Presidential Republic"),

    # ═══════════════════ CENTRAL AMERICA & CARIBBEAN ═══════════════════
    ("GT", "Guatemala", "Central America", 18, 0.095, 0.08, False, 0.35, 0.40, 0.25, "Presidential Republic"),
    ("HN", "Honduras", "Central America", 10, 0.032, 0.06, False, 0.30, 0.35, 0.20, "Presidential Republic"),
    ("SV", "El Salvador", "Central America", 6.5, 0.033, 0.06, False, 0.45, 0.35, 0.25, "Presidential Republic"),
    ("NI", "Nicaragua", "Central America", 7, 0.015, 0.05, False, 0.35, 0.15, 0.18, "Presidential Republic"),
    ("CR", "Costa Rica", "Central America", 5.2, 0.069, 0.03, False, 0.75, 0.80, 0.50, "Presidential Republic"),
    ("PA", "Panama", "Central America", 4.4, 0.077, 0.04, False, 0.60, 0.60, 0.40, "Presidential Republic"),
    ("BZ", "Belize", "Central America", 0.4, 0.003, 0.02, False, 0.60, 0.65, 0.20, "Parliamentary Democracy"),
    ("CU", "Cuba", "Caribbean", 11, 0.107, 0.15, False, 0.50, 0.10, 0.30, "One-Party Socialist State"),
    ("JM", "Jamaica", "Caribbean", 3, 0.019, 0.03, False, 0.55, 0.65, 0.30, "Parliamentary Democracy"),
    ("HT", "Haiti", "Caribbean", 12, 0.020, 0.03, False, 0.15, 0.20, 0.10, "Semi-Presidential Republic"),
    ("DO", "Dominican Republic", "Caribbean", 11, 0.114, 0.06, False, 0.55, 0.55, 0.30, "Presidential Republic"),
    ("TT", "Trinidad and Tobago", "Caribbean", 1.5, 0.028, 0.04, False, 0.60, 0.65, 0.35, "Parliamentary Republic"),

    # ═══════════════════ SOUTH AMERICA ═══════════════════
    ("BR", "Brazil", "South America", 215, 2.1, 0.35, False, 0.55, 0.60, 0.45, "Federal Presidential Republic"),
    ("AR", "Argentina", "South America", 46, 0.64, 0.20, False, 0.45, 0.60, 0.45, "Federal Presidential Republic"),
    ("CO", "Colombia", "South America", 52, 0.34, 0.18, False, 0.45, 0.55, 0.38, "Presidential Republic"),
    ("VE", "Venezuela", "South America", 28, 0.08, 0.15, False, 0.25, 0.12, 0.25, "Federal Presidential Republic"),
    ("CL", "Chile", "South America", 19.5, 0.30, 0.15, False, 0.70, 0.78, 0.55, "Presidential Republic"),
    ("PE", "Peru", "South America", 34, 0.24, 0.12, False, 0.40, 0.50, 0.35, "Presidential Republic"),
    ("EC", "Ecuador", "South America", 18, 0.11, 0.10, False, 0.40, 0.50, 0.30, "Presidential Republic"),
    ("BO", "Bolivia", "South America", 12, 0.044, 0.08, False, 0.40, 0.45, 0.22, "Presidential Republic"),
    ("PY", "Paraguay", "South America", 7, 0.042, 0.06, False, 0.50, 0.50, 0.25, "Presidential Republic"),
    ("UY", "Uruguay", "South America", 3.5, 0.072, 0.05, False, 0.80, 0.85, 0.50, "Presidential Republic"),
    ("GY", "Guyana", "South America", 0.8, 0.015, 0.02, False, 0.55, 0.55, 0.20, "Presidential Republic"),
    ("SR", "Suriname", "South America", 0.6, 0.004, 0.02, False, 0.50, 0.55, 0.18, "Presidential Republic"),

    # ═══════════════════ WESTERN EUROPE ═══════════════════
    ("GB", "United Kingdom", "Western Europe", 68, 3.3, 0.55, True, 0.65, 0.82, 0.78, "Constitutional Monarchy"),
    ("FR", "France", "Western Europe", 68, 3.0, 0.55, True, 0.55, 0.78, 0.75, "Semi-Presidential Republic"),
    ("DE", "Germany", "Western Europe", 84, 4.5, 0.35, False, 0.70, 0.90, 0.82, "Federal Parliamentary Republic"),
    ("IT", "Italy", "Western Europe", 59, 2.2, 0.30, False, 0.60, 0.72, 0.68, "Parliamentary Republic"),
    ("ES", "Spain", "Western Europe", 48, 1.6, 0.25, False, 0.65, 0.78, 0.65, "Parliamentary Constitutional Monarchy"),
    ("NL", "Netherlands", "Western Europe", 18, 1.1, 0.20, False, 0.80, 0.88, 0.82, "Parliamentary Constitutional Monarchy"),
    ("BE", "Belgium", "Western Europe", 12, 0.60, 0.15, False, 0.70, 0.82, 0.75, "Federal Parliamentary Constitutional Monarchy"),
    ("PT", "Portugal", "Western Europe", 10, 0.28, 0.12, False, 0.75, 0.82, 0.60, "Semi-Presidential Republic"),
    ("IE", "Ireland", "Western Europe", 5.1, 0.53, 0.05, False, 0.85, 0.90, 0.78, "Parliamentary Republic"),
    ("AT", "Austria", "Western Europe", 9.1, 0.52, 0.12, False, 0.80, 0.85, 0.75, "Federal Parliamentary Republic"),
    ("CH", "Switzerland", "Western Europe", 8.8, 0.87, 0.12, False, 0.90, 0.92, 0.85, "Federal Republic (Direct Democracy)"),
    ("LU", "Luxembourg", "Western Europe", 0.66, 0.085, 0.02, False, 0.90, 0.88, 0.80, "Constitutional Monarchy"),
    ("MC", "Monaco", "Western Europe", 0.04, 0.008, 0.01, False, 0.92, 0.70, 0.75, "Constitutional Monarchy"),
    ("LI", "Liechtenstein", "Western Europe", 0.04, 0.007, 0.01, False, 0.92, 0.85, 0.75, "Constitutional Monarchy"),
    ("AD", "Andorra", "Western Europe", 0.08, 0.003, 0.01, False, 0.90, 0.82, 0.60, "Parliamentary Co-Principality"),
    ("MT", "Malta", "Western Europe", 0.53, 0.020, 0.03, False, 0.80, 0.78, 0.55, "Parliamentary Republic"),
    ("IS", "Iceland", "Western Europe", 0.38, 0.028, 0.02, False, 0.92, 0.92, 0.78, "Parliamentary Republic"),

    # ═══════════════════ NORTHERN EUROPE / SCANDINAVIA ═══════════════════
    ("SE", "Sweden", "Northern Europe", 10.5, 0.59, 0.18, False, 0.82, 0.90, 0.82, "Parliamentary Constitutional Monarchy"),
    ("NO", "Norway", "Northern Europe", 5.5, 0.48, 0.15, False, 0.88, 0.92, 0.82, "Parliamentary Constitutional Monarchy"),
    ("DK", "Denmark", "Northern Europe", 5.9, 0.40, 0.14, False, 0.85, 0.92, 0.82, "Parliamentary Constitutional Monarchy"),
    ("FI", "Finland", "Northern Europe", 5.6, 0.30, 0.18, False, 0.85, 0.90, 0.82, "Parliamentary Republic"),

    # ═══════════════════ EASTERN EUROPE ═══════════════════
    ("PL", "Poland", "Eastern Europe", 38, 0.81, 0.30, False, 0.65, 0.68, 0.60, "Parliamentary Republic"),
    ("RO", "Romania", "Eastern Europe", 19, 0.30, 0.18, False, 0.55, 0.62, 0.48, "Semi-Presidential Republic"),
    ("CZ", "Czech Republic", "Eastern Europe", 10.8, 0.31, 0.16, False, 0.75, 0.80, 0.65, "Parliamentary Republic"),
    ("HU", "Hungary", "Eastern Europe", 10, 0.19, 0.14, False, 0.55, 0.52, 0.55, "Parliamentary Republic"),
    ("SK", "Slovakia", "Eastern Europe", 5.5, 0.13, 0.10, False, 0.65, 0.68, 0.50, "Parliamentary Republic"),
    ("BG", "Bulgaria", "Eastern Europe", 6.5, 0.10, 0.10, False, 0.50, 0.55, 0.42, "Parliamentary Republic"),
    ("HR", "Croatia", "Eastern Europe", 3.9, 0.072, 0.08, False, 0.65, 0.68, 0.48, "Parliamentary Republic"),
    ("RS", "Serbia", "Eastern Europe", 6.7, 0.063, 0.12, False, 0.50, 0.45, 0.42, "Parliamentary Republic"),
    ("BA", "Bosnia and Herzegovina", "Eastern Europe", 3.2, 0.024, 0.06, False, 0.40, 0.42, 0.30, "Federal Parliamentary Republic"),
    ("SI", "Slovenia", "Eastern Europe", 2.1, 0.063, 0.06, False, 0.78, 0.80, 0.60, "Parliamentary Republic"),
    ("ME", "Montenegro", "Eastern Europe", 0.62, 0.006, 0.04, False, 0.55, 0.55, 0.35, "Parliamentary Republic"),
    ("MK", "North Macedonia", "Eastern Europe", 1.8, 0.014, 0.05, False, 0.50, 0.52, 0.35, "Parliamentary Republic"),
    ("AL", "Albania", "Eastern Europe", 2.8, 0.022, 0.06, False, 0.50, 0.48, 0.32, "Parliamentary Republic"),
    ("XK", "Kosovo", "Eastern Europe", 1.8, 0.010, 0.04, False, 0.40, 0.45, 0.28, "Parliamentary Republic"),
    ("MD", "Moldova", "Eastern Europe", 2.6, 0.016, 0.04, False, 0.40, 0.50, 0.30, "Parliamentary Republic"),

    # ═══════════════════ FORMER SOVIET ═══════════════════
    ("RU", "Russia", "Eurasia", 144, 2.0, 0.80, True, 0.60, 0.20, 0.60, "Federal Semi-Presidential Republic"),
    ("UA", "Ukraine", "Eastern Europe", 37, 0.15, 0.35, False, 0.40, 0.55, 0.50, "Semi-Presidential Republic"),
    ("BY", "Belarus", "Eastern Europe", 9.4, 0.073, 0.12, False, 0.50, 0.08, 0.35, "Presidential Republic"),
    ("GE", "Georgia", "Caucasus", 3.7, 0.025, 0.08, False, 0.50, 0.55, 0.38, "Parliamentary Republic"),
    ("AM", "Armenia", "Caucasus", 3.0, 0.020, 0.08, False, 0.45, 0.50, 0.35, "Parliamentary Republic"),
    ("AZ", "Azerbaijan", "Caucasus", 10.2, 0.078, 0.15, False, 0.55, 0.15, 0.38, "Presidential Republic"),
    ("KZ", "Kazakhstan", "Central Asia", 19.5, 0.22, 0.18, False, 0.60, 0.22, 0.42, "Presidential Republic"),
    ("UZ", "Uzbekistan", "Central Asia", 35, 0.080, 0.12, False, 0.55, 0.15, 0.30, "Presidential Republic"),
    ("TM", "Turkmenistan", "Central Asia", 6.3, 0.045, 0.08, False, 0.50, 0.05, 0.22, "Presidential Republic"),
    ("KG", "Kyrgyzstan", "Central Asia", 6.7, 0.012, 0.06, False, 0.35, 0.35, 0.25, "Presidential Republic"),
    ("TJ", "Tajikistan", "Central Asia", 10, 0.012, 0.06, False, 0.40, 0.12, 0.18, "Presidential Republic"),
    ("EE", "Estonia", "Northern Europe", 1.3, 0.038, 0.06, False, 0.80, 0.85, 0.75, "Parliamentary Republic"),
    ("LV", "Latvia", "Northern Europe", 1.8, 0.041, 0.06, False, 0.75, 0.80, 0.60, "Parliamentary Republic"),
    ("LT", "Lithuania", "Northern Europe", 2.8, 0.067, 0.08, False, 0.75, 0.82, 0.62, "Semi-Presidential Republic"),

    # ═══════════════════ MIDDLE EAST ═══════════════════
    ("TR", "Turkey", "Middle East", 85, 1.15, 0.55, False, 0.55, 0.42, 0.50, "Presidential Republic"),
    ("SA", "Saudi Arabia", "Middle East", 36, 1.1, 0.40, False, 0.70, 0.08, 0.45, "Absolute Monarchy"),
    ("IR", "Iran", "Middle East", 88, 0.40, 0.45, False, 0.40, 0.15, 0.45, "Islamic Republic"),
    ("IL", "Israel", "Middle East", 9.8, 0.53, 0.55, True, 0.50, 0.65, 0.90, "Parliamentary Republic"),
    ("AE", "United Arab Emirates", "Middle East", 10, 0.50, 0.25, False, 0.82, 0.18, 0.65, "Federal Absolute Monarchy"),
    ("IQ", "Iraq", "Middle East", 43, 0.26, 0.18, False, 0.30, 0.30, 0.25, "Federal Parliamentary Republic"),
    ("SY", "Syria", "Middle East", 22, 0.01, 0.12, False, 0.15, 0.05, 0.18, "Presidential Republic"),
    ("JO", "Jordan", "Middle East", 11, 0.048, 0.10, False, 0.55, 0.38, 0.35, "Constitutional Monarchy"),
    ("LB", "Lebanon", "Middle East", 5.5, 0.019, 0.08, False, 0.20, 0.40, 0.35, "Parliamentary Republic"),
    ("KW", "Kuwait", "Middle East", 4.3, 0.16, 0.12, False, 0.70, 0.38, 0.50, "Constitutional Monarchy"),
    ("QA", "Qatar", "Middle East", 2.7, 0.22, 0.10, False, 0.85, 0.22, 0.60, "Absolute Monarchy"),
    ("BH", "Bahrain", "Middle East", 1.5, 0.044, 0.06, False, 0.55, 0.25, 0.45, "Constitutional Monarchy"),
    ("OM", "Oman", "Middle East", 4.6, 0.105, 0.10, False, 0.72, 0.20, 0.40, "Absolute Monarchy"),
    ("YE", "Yemen", "Middle East", 33, 0.021, 0.10, False, 0.10, 0.10, 0.12, "Presidential Republic (civil war)"),
    ("PS", "Palestine", "Middle East", 5.4, 0.019, 0.05, False, 0.15, 0.20, 0.18, "Semi-Presidential Republic"),

    # ═══════════════════ SOUTH ASIA ═══════════════════
    ("IN", "India", "South Asia", 1440, 4.0, 0.65, True, 0.60, 0.55, 0.60, "Federal Parliamentary Republic"),
    ("PK", "Pakistan", "South Asia", 230, 0.35, 0.45, True, 0.35, 0.35, 0.30, "Federal Parliamentary Republic"),
    ("BD", "Bangladesh", "South Asia", 170, 0.46, 0.12, False, 0.45, 0.35, 0.28, "Parliamentary Republic"),
    ("LK", "Sri Lanka", "South Asia", 22, 0.075, 0.08, False, 0.40, 0.45, 0.35, "Semi-Presidential Republic"),
    ("NP", "Nepal", "South Asia", 30, 0.040, 0.06, False, 0.40, 0.42, 0.22, "Federal Parliamentary Republic"),
    ("AF", "Afghanistan", "South Asia", 40, 0.015, 0.12, False, 0.10, 0.02, 0.08, "Islamic Emirate"),
    ("MM", "Myanmar", "South Asia", 55, 0.060, 0.12, False, 0.15, 0.08, 0.18, "Military Junta"),
    ("BT", "Bhutan", "South Asia", 0.78, 0.003, 0.02, False, 0.75, 0.55, 0.22, "Constitutional Monarchy"),
    ("MV", "Maldives", "South Asia", 0.52, 0.006, 0.02, False, 0.55, 0.42, 0.25, "Presidential Republic"),

    # ═══════════════════ EAST ASIA ═══════════════════
    ("CN", "China", "East Asia", 1420, 18.5, 0.82, True, 0.75, 0.10, 0.82, "One-Party Socialist Republic"),
    ("JP", "Japan", "East Asia", 124, 4.2, 0.45, False, 0.85, 0.80, 0.88, "Constitutional Monarchy"),
    ("KR", "South Korea", "East Asia", 52, 1.7, 0.45, False, 0.70, 0.80, 0.85, "Presidential Republic"),
    ("KP", "North Korea", "East Asia", 26, 0.03, 0.35, True, 0.80, 0.02, 0.25, "One-Party Totalitarian State"),
    ("MN", "Mongolia", "East Asia", 3.4, 0.017, 0.06, False, 0.55, 0.60, 0.28, "Semi-Presidential Republic"),
    ("TW", "Taiwan", "East Asia", 24, 0.79, 0.25, False, 0.80, 0.82, 0.88, "Semi-Presidential Republic"),

    # ═══════════════════ SOUTHEAST ASIA ═══════════════════
    ("ID", "Indonesia", "Southeast Asia", 275, 1.4, 0.30, False, 0.60, 0.55, 0.42, "Presidential Republic"),
    ("PH", "Philippines", "Southeast Asia", 115, 0.44, 0.15, False, 0.50, 0.52, 0.35, "Presidential Republic"),
    ("VN", "Vietnam", "Southeast Asia", 100, 0.43, 0.22, False, 0.65, 0.10, 0.42, "One-Party Socialist Republic"),
    ("TH", "Thailand", "Southeast Asia", 72, 0.51, 0.22, False, 0.55, 0.35, 0.45, "Constitutional Monarchy"),
    ("MY", "Malaysia", "Southeast Asia", 33, 0.40, 0.15, False, 0.65, 0.52, 0.52, "Federal Parliamentary Constitutional Monarchy"),
    ("SG", "Singapore", "Southeast Asia", 5.9, 0.40, 0.12, False, 0.90, 0.55, 0.88, "Parliamentary Republic"),
    ("KH", "Cambodia", "Southeast Asia", 17, 0.030, 0.06, False, 0.45, 0.15, 0.20, "Constitutional Monarchy"),
    ("LA", "Laos", "Southeast Asia", 7.5, 0.019, 0.05, False, 0.50, 0.08, 0.18, "One-Party Socialist Republic"),
    ("BN", "Brunei", "Southeast Asia", 0.45, 0.014, 0.04, False, 0.80, 0.15, 0.45, "Absolute Monarchy"),
    ("TL", "Timor-Leste", "Southeast Asia", 1.3, 0.003, 0.03, False, 0.40, 0.50, 0.15, "Semi-Presidential Republic"),

    # ═══════════════════ OCEANIA ═══════════════════
    ("AU", "Australia", "Oceania", 26, 1.7, 0.35, False, 0.80, 0.85, 0.70, "Federal Parliamentary Constitutional Monarchy"),
    ("NZ", "New Zealand", "Oceania", 5.2, 0.25, 0.08, False, 0.88, 0.90, 0.72, "Parliamentary Constitutional Monarchy"),
    ("PG", "Papua New Guinea", "Oceania", 10, 0.030, 0.04, False, 0.35, 0.45, 0.15, "Parliamentary Constitutional Monarchy"),
    ("FJ", "Fiji", "Oceania", 0.93, 0.005, 0.03, False, 0.55, 0.50, 0.25, "Parliamentary Republic"),

    # ═══════════════════ NORTH AFRICA ═══════════════════
    ("EG", "Egypt", "North Africa", 105, 0.40, 0.40, False, 0.50, 0.18, 0.30, "Presidential Republic"),
    ("DZ", "Algeria", "North Africa", 45, 0.19, 0.22, False, 0.45, 0.25, 0.30, "Presidential Republic"),
    ("MA", "Morocco", "North Africa", 37, 0.14, 0.18, False, 0.55, 0.42, 0.35, "Constitutional Monarchy"),
    ("TN", "Tunisia", "North Africa", 12, 0.047, 0.10, False, 0.40, 0.45, 0.32, "Presidential Republic"),
    ("LY", "Libya", "North Africa", 7, 0.042, 0.10, False, 0.15, 0.12, 0.20, "Provisional Government"),

    # ═══════════════════ WEST AFRICA ═══════════════════
    ("NG", "Nigeria", "West Africa", 225, 0.47, 0.20, False, 0.35, 0.40, 0.25, "Federal Presidential Republic"),
    ("GH", "Ghana", "West Africa", 33, 0.073, 0.08, False, 0.55, 0.62, 0.28, "Presidential Republic"),
    ("CI", "Ivory Coast", "West Africa", 28, 0.070, 0.08, False, 0.45, 0.38, 0.22, "Presidential Republic"),
    ("SN", "Senegal", "West Africa", 17, 0.028, 0.06, False, 0.55, 0.58, 0.25, "Presidential Republic"),
    ("ML", "Mali", "West Africa", 22, 0.019, 0.08, False, 0.20, 0.15, 0.12, "Military Junta"),
    ("BF", "Burkina Faso", "West Africa", 22, 0.019, 0.06, False, 0.20, 0.12, 0.12, "Military Junta"),
    ("NE", "Niger", "West Africa", 26, 0.015, 0.06, False, 0.25, 0.15, 0.10, "Military Junta"),
    ("GN", "Guinea", "West Africa", 14, 0.020, 0.06, False, 0.30, 0.18, 0.12, "Military Junta"),
    ("SL", "Sierra Leone", "West Africa", 8.4, 0.004, 0.04, False, 0.40, 0.42, 0.12, "Presidential Republic"),
    ("LR", "Liberia", "West Africa", 5.2, 0.004, 0.03, False, 0.35, 0.42, 0.10, "Presidential Republic"),
    ("TG", "Togo", "West Africa", 8.8, 0.008, 0.04, False, 0.40, 0.25, 0.12, "Presidential Republic"),
    ("BJ", "Benin", "West Africa", 13, 0.018, 0.04, False, 0.50, 0.52, 0.15, "Presidential Republic"),
    ("MR", "Mauritania", "West Africa", 4.7, 0.010, 0.05, False, 0.40, 0.28, 0.12, "Presidential Republic"),
    ("GM", "Gambia", "West Africa", 2.6, 0.002, 0.02, False, 0.45, 0.42, 0.10, "Presidential Republic"),
    ("GW", "Guinea-Bissau", "West Africa", 2.1, 0.002, 0.02, False, 0.25, 0.30, 0.08, "Semi-Presidential Republic"),
    ("CV", "Cape Verde", "West Africa", 0.6, 0.002, 0.02, False, 0.70, 0.72, 0.25, "Semi-Presidential Republic"),

    # ═══════════════════ EAST AFRICA ═══════════════════
    ("ET", "Ethiopia", "East Africa", 125, 0.16, 0.18, False, 0.25, 0.25, 0.18, "Federal Parliamentary Republic"),
    ("KE", "Kenya", "East Africa", 55, 0.11, 0.12, False, 0.50, 0.48, 0.28, "Presidential Republic"),
    ("TZ", "Tanzania", "East Africa", 65, 0.075, 0.10, False, 0.55, 0.38, 0.20, "Presidential Republic"),
    ("UG", "Uganda", "East Africa", 47, 0.046, 0.08, False, 0.40, 0.30, 0.18, "Presidential Republic"),
    ("RW", "Rwanda", "East Africa", 14, 0.013, 0.06, False, 0.65, 0.22, 0.22, "Presidential Republic"),
    ("SO", "Somalia", "East Africa", 18, 0.008, 0.06, False, 0.10, 0.10, 0.05, "Federal Parliamentary Republic"),
    ("SD", "Sudan", "East Africa", 47, 0.026, 0.12, False, 0.10, 0.08, 0.12, "Military Junta"),
    ("SS", "South Sudan", "East Africa", 11, 0.004, 0.06, False, 0.08, 0.08, 0.05, "Presidential Republic"),
    ("ER", "Eritrea", "East Africa", 3.6, 0.002, 0.08, False, 0.35, 0.02, 0.08, "One-Party Presidential Republic"),
    ("DJ", "Djibouti", "East Africa", 1.1, 0.004, 0.04, False, 0.50, 0.18, 0.15, "Presidential Republic"),
    ("MG", "Madagascar", "East Africa", 29, 0.015, 0.04, False, 0.35, 0.38, 0.12, "Semi-Presidential Republic"),
    ("MU", "Mauritius", "East Africa", 1.3, 0.013, 0.02, False, 0.75, 0.78, 0.42, "Parliamentary Republic"),
    ("SC", "Seychelles", "East Africa", 0.1, 0.002, 0.01, False, 0.72, 0.55, 0.35, "Presidential Republic"),
    ("KM", "Comoros", "East Africa", 0.9, 0.001, 0.01, False, 0.35, 0.35, 0.10, "Federal Presidential Republic"),
    ("BI", "Burundi", "East Africa", 13, 0.003, 0.04, False, 0.25, 0.15, 0.08, "Presidential Republic"),

    # ═══════════════════ CENTRAL AFRICA ═══════════════════
    ("CD", "DR Congo", "Central Africa", 100, 0.065, 0.12, False, 0.15, 0.20, 0.10, "Semi-Presidential Republic"),
    ("CM", "Cameroon", "Central Africa", 28, 0.045, 0.08, False, 0.35, 0.22, 0.15, "Presidential Republic"),
    ("AO", "Angola", "Central Africa", 35, 0.12, 0.10, False, 0.40, 0.22, 0.18, "Presidential Republic"),
    ("TD", "Chad", "Central Africa", 17, 0.012, 0.06, False, 0.20, 0.12, 0.08, "Presidential Republic"),
    ("CG", "Republic of Congo", "Central Africa", 6, 0.014, 0.05, False, 0.35, 0.18, 0.12, "Presidential Republic"),
    ("GA", "Gabon", "Central Africa", 2.3, 0.020, 0.05, False, 0.45, 0.22, 0.18, "Presidential Republic"),
    ("GQ", "Equatorial Guinea", "Central Africa", 1.7, 0.012, 0.03, False, 0.45, 0.08, 0.15, "Presidential Republic"),
    ("CF", "Central African Republic", "Central Africa", 5.5, 0.002, 0.04, False, 0.10, 0.15, 0.05, "Presidential Republic"),
    ("ST", "Sao Tome and Principe", "Central Africa", 0.22, 0.001, 0.01, False, 0.55, 0.60, 0.12, "Semi-Presidential Republic"),

    # ═══════════════════ SOUTHERN AFRICA ═══════════════════
    ("ZA", "South Africa", "Southern Africa", 60, 0.40, 0.22, False, 0.45, 0.62, 0.42, "Parliamentary Republic"),
    ("MZ", "Mozambique", "Southern Africa", 33, 0.018, 0.06, False, 0.30, 0.30, 0.12, "Presidential Republic"),
    ("ZW", "Zimbabwe", "Southern Africa", 16, 0.028, 0.06, False, 0.30, 0.22, 0.15, "Presidential Republic"),
    ("ZM", "Zambia", "Southern Africa", 20, 0.029, 0.05, False, 0.50, 0.52, 0.18, "Presidential Republic"),
    ("MW", "Malawi", "Southern Africa", 20, 0.013, 0.04, False, 0.45, 0.48, 0.12, "Presidential Republic"),
    ("BW", "Botswana", "Southern Africa", 2.6, 0.019, 0.04, False, 0.72, 0.72, 0.30, "Parliamentary Republic"),
    ("NA", "Namibia", "Southern Africa", 2.6, 0.013, 0.04, False, 0.65, 0.62, 0.22, "Presidential Republic"),
    ("SZ", "Eswatini", "Southern Africa", 1.2, 0.005, 0.02, False, 0.40, 0.12, 0.12, "Absolute Monarchy"),
    ("LS", "Lesotho", "Southern Africa", 2.2, 0.002, 0.02, False, 0.35, 0.45, 0.10, "Constitutional Monarchy"),

    # ═══════════════════ SUPRANATIONAL ═══════════════════
    ("EU", "European Union", "Europe", 450, 18.0, 0.60, True, 0.70, 0.85, 0.78, "Supranational Union"),
]
# fmt: on


def get_all_country_codes() -> list[str]:
    return [c[0] for c in COUNTRIES_RAW]


def get_country_data(code: str) -> tuple | None:
    for c in COUNTRIES_RAW:
        if c[0] == code:
            return c
    return None


def get_countries_by_region(region: str) -> list[tuple]:
    return [c for c in COUNTRIES_RAW if c[2] == region]


def get_all_regions() -> list[str]:
    return sorted(set(c[2] for c in COUNTRIES_RAW))


TOTAL_COUNTRIES = len(COUNTRIES_RAW)
