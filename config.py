import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
TEXTS_DIR = DATA_DIR / "texts"
LEXICONS_DIR = DATA_DIR / "lexicons"
GRAMMARS_DIR = DATA_DIR / "grammars"

# Create directories
DATA_DIR.mkdir(exist_ok=True)
TEXTS_DIR.mkdir(exist_ok=True)
LEXICONS_DIR.mkdir(exist_ok=True)
GRAMMARS_DIR.mkdir(exist_ok=True)

# 🏛️ Classical Lexicon Paths (The Quad-Lexical Suite)
LISAN_PATH = DATA_DIR / "lisanclean.json"
KITAB_AL_AYN_PATH = LEXICONS_DIR / "kitab_al_ayn" / "kitab_al_ayn_dictionary.json"
RAGHIB_MUFRADAT_PATH = LEXICONS_DIR / "raghib_mufradat" / "raghib_mufradat_dictionary.json"
ZAMAKHSHARI_ASAS_PATH = LEXICONS_DIR / "zamakhshari_asas" / "asas_balagha_dictionary.json"

# 📜 Sibawayh Grammar Path
SIBAWAYH_RULES_PATH = GRAMMARS_DIR / "sibawayh_kitab" / "sibawayh_rules.json"

# LLM & DeepSeek Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")

BASE_OPENITI = "https://raw.githubusercontent.com/OpenITI"

# All Digitized Classical Sources
SOURCES = {
    # 1. Lexicographical & Rhetorical Engines
    "raghib_mufradat": {
        "title": "Al-Mufradat fi Gharib al-Quran",
        "author": "Al-Raghib al-Isfahani (d. 502 AH)",
        "url": f"{BASE_OPENITI}/0525AH/master/data/0502RaghibIsbahani/0502RaghibIsbahani.Mufradat/0502RaghibIsbahani.Mufradat.Shamela0023636-ara1",
        "filename": "raghib_mufradat.txt"
    },
    "zamakhshari_asas": {
        "title": "Asas al-Balaghah",
        "author": "Al-Zamakhshari (d. 538 AH)",
        "url": f"{BASE_OPENITI}/0550AH/master/data/0538JarAllahZamakhshari/0538JarAllahZamakhshari.AsasBalagha/0538JarAllahZamakhshari.AsasBalagha.Shamela0021568-ara1",
        "filename": "zamakhshari_asas.txt"
    },
    "sibawayh_kitab": {
        "title": "Kitab Sibawayh (Grammar Engine)",
        "author": "Sibawayh (d. 180 AH)",
        "url": f"{BASE_OPENITI}/0200AH/master/data/0180Sibawayhi/0180Sibawayhi.KitabSibawayhi/0180Sibawayhi.KitabSibawayhi.JK006989-ara1",
        "filename": "sibawayh_kitab.txt"
    },
    
    # 2. Imam Fakhr al-Din al-Razi Masterworks
    "razi_tafsir_kabir": {
        "title": "Tafsir al-Kabir / Mafatih al-Ghayb",
        "author": "Fakhr al-Din al-Razi (d. 606 AH)",
        "url": f"{BASE_OPENITI}/0625AH/master/data/0606FakhrDinRazi/0606FakhrDinRazi.MafatihGhayb/0606FakhrDinRazi.MafatihGhayb.Tafsir01004-ara1",
        "filename": "razi_tafsir_kabir.txt"
    },
    "razi_matalib": {
        "title": "Al-Matalib al-'Aliya",
        "author": "Fakhr al-Din al-Razi (d. 606 AH)",
        "url": f"{BASE_OPENITI}/0625AH/master/data/0606FakhrDinRazi/0606FakhrDinRazi.MatalibCaliya/0606FakhrDinRazi.MatalibCaliya.Rafed0003630Vols-ara1",
        "filename": "razi_matalib.txt"
    },
    "razi_asas": {
        "title": "Asas al-Taqdis",
        "author": "Fakhr al-Din al-Razi (d. 606 AH)",
        "url": f"{BASE_OPENITI}/0625AH/master/data/0606FakhrDinRazi/0606FakhrDinRazi.AsasTaqdis/0606FakhrDinRazi.AsasTaqdis.JK001259-ara1",
        "filename": "razi_asas.txt"
    },
    "razi_arbain": {
        "title": "Al-Arba'in fi Usul al-Din",
        "author": "Fakhr al-Din al-Razi (d. 606 AH)",
        "url": f"{BASE_OPENITI}/0625AH/master/data/0606FakhrDinRazi/0606FakhrDinRazi.ArbacinFiUsulDin/0606FakhrDinRazi.ArbacinFiUsulDin.Rafed0003314Vols-ara1",
        "filename": "razi_arbain.txt"
    },
    "razi_ismat_anbiya": {
        "title": "'Ismat al-Anbiya'",
        "author": "Fakhr al-Din al-Razi (d. 606 AH)",
        "url": f"{BASE_OPENITI}/0625AH/master/data/0606FakhrDinRazi/0606FakhrDinRazi.CismatAnbiya/0606FakhrDinRazi.CismatAnbiya.Shia003701-ara1",
        "filename": "razi_ismat_anbiya.txt"
    },
    "razi_ictiqadat": {
        "title": "I'tiqadat Firaq al-Muslimin wa-l-Mushrikin",
        "author": "Fakhr al-Din al-Razi (d. 606 AH)",
        "url": f"{BASE_OPENITI}/0625AH/master/data/0606FakhrDinRazi/0606FakhrDinRazi.Ictiqadat/0606FakhrDinRazi.Ictiqadat.Shamela0006516-ara1",
        "filename": "razi_ictiqadat.txt"
    },
    "razi_lawami": {
        "title": "Lawami' al-Bayyinat (Sharh Asma' Allah)",
        "author": "Fakhr al-Din al-Razi (d. 606 AH)",
        "url": f"{BASE_OPENITI}/0625AH/master/data/0606FakhrDinRazi/0606FakhrDinRazi.LawamicBayyinat/0606FakhrDinRazi.LawamicBayyinat.Kraken220221161405-ara1",
        "filename": "razi_lawami.txt"
    },
    "razi_macalim": {
        "title": "Ma'alim Usul al-Din",
        "author": "Fakhr al-Din al-Razi (d. 606 AH)",
        "url": f"{BASE_OPENITI}/0625AH/master/data/0606FakhrDinRazi/0606FakhrDinRazi.MacalimUsulDin/0606FakhrDinRazi.MacalimUsulDin.Shamela0006372-ara1",
        "filename": "razi_macalim.txt"
    },
    "razi_asrar_tanzil": {
        "title": "Min Asrar al-Tanzil",
        "author": "Fakhr al-Din al-Razi (d. 606 AH)",
        "url": f"{BASE_OPENITI}/0625AH/master/data/0606FakhrDinRazi/0606FakhrDinRazi.MinAsrarTanzil/0606FakhrDinRazi.MinAsrarTanzil.ShamAY0034048-ara1",
        "filename": "razi_asrar_tanzil.txt"
    },
    "razi_qada_qadar": {
        "title": "Al-Qada' wa-l-Qadar",
        "author": "Fakhr al-Din al-Razi (d. 606 AH)",
        "url": f"{BASE_OPENITI}/0625AH/master/data/0606FakhrDinRazi/0606FakhrDinRazi.QadaWaQadar/0606FakhrDinRazi.QadaWaQadar.Rafed0003462-ara1",
        "filename": "razi_qada_qadar.txt"
    }
}
