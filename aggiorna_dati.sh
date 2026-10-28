#!/bin/bash
# =====================================================================
# Aggiorna tutto il dataset in un colpo solo. Si lancia dal Terminale, da qualunque cartella:
#
#     bash ~/Documents/Papers/SNA-Dataset/Costituenti/aggiorna_dati.sh
#
# Passi (ognuno riprende da dove era arrivato, quindi si puo' interrompere con Ctrl-C e rilanciare):
#   1. scarica le fonti esterne (adesioni ai gruppi dalla Camera, VIAF da Wikidata)   ~1 minuto
#   2. OCR delle sedute non ancora trascritte, a 300 e a 400 dpi                       alcune ore la prima volta
#   3. estrazione di emendamenti, esiti, articoli e voti                              ~5 minuti
#   4. menzioni nei discorsi, esportazione, foglio dei casi aperti, GraphML, test      ~5 minuti
# Tutto quello che compare a schermo finisce anche in pipeline/aggiorna_dati.log.
# Opzioni:  --senza-ocr   salta il passo 2 (utile se l'OCR e' gia' stato fatto)
# =====================================================================
QUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$QUI" || exit 1
LOG="$QUI/pipeline/aggiorna_dati.log"
exec > >(tee -a "$LOG") 2>&1
echo "=== $(date '+%d/%m/%Y %H:%M') — aggiornamento del dataset in $QUI"

PY=python3
command -v "$PY" >/dev/null || { echo "Manca python3"; exit 1; }
"$PY" -c "import pandas, openpyxl" 2>/dev/null || { echo "Installo pandas e openpyxl"; "$PY" -m pip install --quiet pandas openpyxl || exit 1; }

passo() { echo; echo "--- $1"; shift; "$@"; local r=$?; [ $r -ne 0 ] && echo "!!! ERRORE (codice $r) in: $*"; return $r; }

# 1. fonti esterne: un errore qui non ferma il resto
passo "1/4 Fonti esterne (Camera, Wikidata)" "$PY" pipeline/tools/scarica_fonti_esterne.py

# 2. OCR
if [[ " $* " != *" --senza-ocr "* ]]; then
  command -v Rscript >/dev/null || { echo "!!! Manca R (Rscript): installalo da https://cran.r-project.org, poi rilancia"; exit 1; }
  Rscript -e 'p <- c("pdftools","tesseract","magick"); m <- p[!sapply(p, requireNamespace, quietly=TRUE)]; if (length(m)) install.packages(m, repos="https://cloud.r-project.org"); if (!"ita" %in% tesseract::tesseract_info()$available) tesseract::tesseract_download("ita")' || exit 1
  passo "2/4 OCR a 300 dpi" Rscript pipeline/ocr_costituente.R || exit 1
  passo "2/4 OCR a 400 dpi" Rscript pipeline/ocr_400dpi.R || exit 1
fi

# 3. estrazione
passo "3/4 Estrazione" "$PY" pipeline/esegui_estrazione.py || exit 1
passo "3/4 Menzioni nei discorsi" "$PY" pipeline/tools/estrai_menzioni_discorso.py pipeline || exit 1

# 4. esportazione e controlli
passo "4/4 Esportazione" "$PY" pipeline/esporta_dataset.py || exit 1
passo "4/4 Foglio dei casi aperti" "$PY" pipeline/tools/prepara_casi_aperti.py
passo "4/4 GraphML" "$PY" pipeline/tools/esporta_graphml.py
passo "4/4 Coesione di voto" "$PY" pipeline/tools/coesione_voto.py
passo "4/4 Incertezza delle statistiche" "$PY" pipeline/tools/incertezza_rete.py 1000
passo "4/4 Test di non-regressione" "$PY" pipeline/tools/test_regole.py

echo; echo "=== Fatto. Riepilogo in $LOG"
echo "Prossimo passo: aprire pipeline/CASI_APERTI.xlsx, oppure dire alla sessione di lavoro che l'aggiornamento e' finito."
