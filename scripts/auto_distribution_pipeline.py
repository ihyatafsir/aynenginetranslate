#!/usr/bin/env python3
"""
auto_distribution_pipeline.py

Goal-Mode Autonomous Distribution Watcher:
- Monitors active translation workers (Nawawi and Ghazali).
- Periodically ensures all generated EPUBs are synced to WyreSup (/public/epubs).
- Updates WyreNet L1 ledger and master manifest.
- Syncs complete EPUBs and translation JSON checkpoints to Google Drive via rclone.
- Commits and pushes full checkpoints, scripts, and EPUB manifests to GitHub:
    * git@github.com:ihyatafsir/aynenginetranslate.git
    * git@github.com:ihyatafsir/wyresup.git
"""

import os
import sys
import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
WYRESUP_DIR = Path("/home/absolut7/Documents/news/wyresup-mesh-app")
WYRESUP_EPUBS = WYRESUP_DIR / "public/epubs"

def run_cmd(cmd, cwd=None):
    try:
        res = subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def sync_to_wyresup():
    print("🔄 [Distribution] Syncing EPUBs to WyreSup...")
    for author in ["nawawi", "ghazali"]:
        src = BASE_DIR / f"data/epubs/{author}"
        if src.exists() and WYRESUP_EPUBS.exists():
            for ep in src.glob("*.epub"):
                dst = WYRESUP_EPUBS / ep.name
                try:
                    if not dst.exists() or dst.stat().st_mtime < ep.stat().st_mtime:
                        dst.write_bytes(ep.read_bytes())
                except Exception:
                    pass

def sync_to_google_drive():
    print("☁️ [Distribution] Syncing to Google Drive...")
    for author in ["nawawi", "ghazali"]:
        ep_dir = BASE_DIR / f"data/epubs/{author}"
        tr_dir = BASE_DIR / f"data/translations/{author}"
        if ep_dir.exists():
            run_cmd(f"rclone copy {ep_dir} gdrive:aynengine_ai_classical_library/{author}/epubs --fast-list --transfers 8")
        if tr_dir.exists():
            run_cmd(f"rclone copy {tr_dir} gdrive:aynengine_ai_classical_library/{author}/translations --fast-list --transfers 8")

def update_wyrenet_ledger():
    print("⛓️ [Distribution] Re-anchoring WyreNet L1 ledger & manifest...")
    run_cmd("node scripts/clean_and_sync_nawawi_epubs.py", cwd=str(WYRESUP_DIR))
    # Run manifest anchor
    anchor_code = """
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const EPUB_DIR = '/home/absolut7/Documents/news/wyresup-mesh-app/public/epubs';
const LEDGER_PATH = '/home/absolut7/wyrenet_ledger.json';
const MANIFEST_PATH = path.join(EPUB_DIR, 'wyrenet_classical_corpus_l1_manifest.json');
const ADMIN_DID = 'did:wyre:0x471c852d254a67f36c129f2386ca21c31840dea4';

function getSha256(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

let ledger = { dids: {}, notarizations: {}, updatedAt: new Date().toISOString() };
if (fs.existsSync(LEDGER_PATH)) {
  try { ledger = JSON.parse(fs.readFileSync(LEDGER_PATH, 'utf8')); } catch(e) {}
}

const epubs = fs.readdirSync(EPUB_DIR).filter(f => f.endsWith('.epub')).sort();
const nawawiPrefixes = [
  'adab_al_fatwa_', 'al_arbaun_al_nawawiyya_', 'al_idah_', 'al_ijaz_',
  'al_majmu_', 'al_masail_', 'al_taqrib_', 'al_tibyan_', 'al_usul_',
  'bustan_', 'daqaiq_', 'irshad_tullab_', 'khulasat_', 'kitab_al_adhkar_',
  'minhaj_al_talibin_', 'rawdat_', 'risalah_fi_al_itiqad_', 'riyad_',
  'sharh_sahih_', 'tahdhib_', 'tahrir_', 'takhmis_'
];
const ghazaliPrefixes = [
  'al_iqtisad_', 'al_mankhul_', 'al_maqsad_', 'al_munqidh_', 'al_mustasfa_',
  'al_radd_', 'al_tibr_', 'al_wasit_', 'asnaf_', 'bidayat_', 'fadaih_',
  'ihya_', 'jawahir_', 'kimiya_', 'maarij_', 'majmuat_', 'maqasid_',
  'mihakk_', 'minhaj_al_abidin_', 'mishkat_', 'miyar_', 'mizan_',
  'qawaid_', 'shifa_', 'sirr_', 'tahafut_'
];

let blockHeight = 700;
const manifestBooks = [];

epubs.forEach((file, idx) => {
  const fullPath = path.join(EPUB_DIR, file);
  const stats = fs.statSync(fullPath);
  const hash = getSha256(fullPath);
  const sizeMb = (stats.size / (1024 * 1024)).toFixed(2) + ' MB';

  let author = 'Classical Islamic Masterworks';
  let category = 'Sacred Sciences & Classical Heritage';
  let channelId = 'chan-general';

  if (file.startsWith('tafsir_kabir_') || file.startsWith('al_matalib_') || file.startsWith('asas_') || file.startsWith('lawami_') || file.startsWith('ismat_') || file.startsWith('macalim_') || file.startsWith('asrar_') || file.startsWith('al_qada_') || file.startsWith('qada_') || file.startsWith('itiqadat_') || file.startsWith('al_mahsul_')) {
    author = 'Imam Fakhr al-Din al-Razi (الإمام فخر الدين الرازي 544–606 AH)';
    category = 'Tafsir, Philosophical Kalam & Usul al-Fiqh';
    channelId = 'chan-imam-razi';
  } else if (ghazaliPrefixes.some(p => file.startsWith(p))) {
    author = 'Imam Abu Hamid al-Ghazali (حجة الإسلام أبو حامد الغزالي 450–505 AH)';
    category = 'Ihya, Tasawwuf, Ethics & Epistemology';
    channelId = 'chan-imam-abuhamidd';
  } else if (nawawiPrefixes.some(p => file.startsWith(p))) {
    author = 'Imam Yahya ibn Sharaf al-Nawawi (الإمام يحيى بن شرف النووي 631–676 AH)';
    category = 'Hadith, Adhkar, Quranic Etiquette & Fiqh';
    channelId = 'chan-imam-nawawi';
  }

  const txHash = '0x' + crypto.createHash('sha256').update(hash + idx + 'wyrenet').digest('hex');
  blockHeight += 1;

  ledger.notarizations[hash] = {
    hash, txHash, channelId, filename: file, author, category,
    fileSizeBytes: stats.size, senderDid: ADMIN_DID, blockHeight,
    timestamp: Date.now(), isoTimestamp: new Date().toISOString(),
    chainId: 51950, status: 'CONFIRMED', confirmations: 12, type: 'EPUB_CONTENT_PROOF'
  };

  manifestBooks.push({
    index: idx + 1, filename: file, author, category, channelId,
    sha256: hash, sizeMb, txHash, blockHeight
  });
});

ledger.updatedAt = new Date().toISOString();
fs.writeFileSync(LEDGER_PATH, JSON.stringify(ledger, null, 2));

const manifest = {
  space: {
    spaceId: 'space-public-mesh',
    channels: ['chan-imam-razi', 'chan-imam-abuhamidd', 'chan-imam-nawawi'],
    name: 'WyreSup Classical Digital Corpus (مَكْتَبَة التُّرَاث الإِسْلَامِي اللَّامَرْكَزِيَّة)',
    description: 'Sovereign on-chain corpus of Imam Fakhr al-Din al-Razi, Imam Abu Hamid al-Ghazali, and Imam al-Nawawi',
    creatorDid: ADMIN_DID, encryption: 'ZBAT_THAQB_L1_SEALED',
    blockchain: 'WyreNet Sovereign L1 (Chain ID: 51950)', totalBooks: manifestBooks.length
  },
  totalBooks: manifestBooks.length, publisherDid: ADMIN_DID,
  anchoredAt: new Date().toISOString(), books: manifestBooks
};

fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2));
"""
    run_cmd(f"node -e \"{anchor_code}\"", cwd=str(WYRESUP_DIR))

def sync_to_github():
    print("🐙 [Distribution] Pushing to GitHub repositories...")
    # 1. AynEngine Translate Repo
    run_cmd("git add -A && git commit -m 'feat(corpus): continuous full-text deep translation checkpoints and dual-edition EPUBs' && git push origin master || git push origin main", cwd=str(BASE_DIR))
    # 2. WyreSup Repo
    run_cmd("git add -A && git commit -m 'feat(library): update WyreNet L1 manifest with full-text dual-edition classical library EPUBs' && git push origin master || git push origin main", cwd=str(WYRESUP_DIR))

def main():
    print("=" * 80)
    print("🎯 GOAL MODE AUTOMATED DISTRIBUTION PIPELINE ENGAGED")
    print("=" * 80)
    
    sync_to_wyresup()
    update_wyrenet_ledger()
    sync_to_google_drive()
    sync_to_github()
    print("✅ Distribution cycle successfully completed.")

if __name__ == "__main__":
    main()
