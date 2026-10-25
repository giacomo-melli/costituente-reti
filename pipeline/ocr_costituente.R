# =====================================================================
# OCR dei resoconti dell'Assemblea Costituente — versione 2 (a colonne)
#
# Per ogni pagina: scarica il PDF della seduta, rende la pagina a 300 dpi,
# toglie l'intestazione, divide le due colonne e trascrive ciascuna con
# Tesseract in italiano. Salva un .txt per pagina in "testi_colonne",
# nello stesso formato usato per il pilota.
#
# Come usarlo:
#   1. Solo la prima volta: esegui la SEZIONE 0 (togli i #).
#   2. Esegui tutto lo script (Cmd + Shift + Invio).
#   3. Puoi interromperlo e rilanciarlo: riparte da dove era arrivato.
# Tempo stimato: alcune ore per tutte le 173 sedute (circa 4.000 pagine).
# =====================================================================

# ---- SEZIONE 0: installazione (solo la prima volta) ------------------
# install.packages(c("pdftools", "tesseract", "magick"))
# tesseract::tesseract_download("ita")

# ---- SEZIONE 1: impostazioni -----------------------------------------
CARTELLA <- path.expand("~/Documents/Insegnamento/Trento ASNA/Costituenti/pipeline")
DPI <- 300
CORE <- max(1, parallel::detectCores() - 2)   # pagine trascritte in parallelo

sedute <- c(49,50,52,54,55,56,58,59,60,62,64,66,68,69,70,72,74,75,76,78,80,81,82,83,84,85,86,87,88,89,90,92,93,94,95,97,98,99,100,101,102,103,104,105,106,109,113,115,116,118,119,120,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,143,147,149,164,168,170,171,173,176,177,178,180,182,183,185,186,188,190,192,195,213,215,216,218,220,222,224,226,229,231,233,248,249,250,251,252,253,254,256,257,258,259,260,261,262,263,265,266,267,268,269,270,271,272,273,276,277,278,281,282,283,284,286,287,288,289,290,292,293,294,296,297,299,301,302,303,304,305,306,307,308,309,310,311,312,313,315,316,317,318,319,320,321,322,328,329,330,332,342,343,346)

# ---- SEZIONE 2: funzioni -----------------------------------------------
library(pdftools); library(tesseract); library(magick)
dir.create(file.path(CARTELLA, "pdf"), showWarnings = FALSE)
dir.create(file.path(CARTELLA, "testi_colonne"), showWarnings = FALSE)
log_file <- file.path(CARTELLA, "registro.txt")
scrivi_log <- function(...) {
  msg <- paste0(format(Sys.time(), "%d/%m %H:%M:%S"), "  ", ...)
  message(msg); cat(msg, "\n", file = log_file, append = TRUE)
}

scarica <- function(n) {
  s <- sprintf("sed%03d", n)
  dest <- file.path(CARTELLA, "pdf", paste0(s, ".pdf"))
  if (file.exists(dest) && file.size(dest) > 10000) return(dest)
  url <- sprintf("https://documenti.camera.it/_dati/costituente/lavori/Assemblea/%s/%snc.pdf", s, s)
  for (i in 1:3) {
    ok <- tryCatch({ download.file(url, dest, mode = "wb", quiet = TRUE,
                                   headers = c("User-Agent" = "Mozilla/5.0")); file.size(dest) > 10000 },
                   error = function(e) FALSE)
    if (isTRUE(ok)) return(dest)
    Sys.sleep(5)
  }
  scrivi_log("ERRORE download seduta ", n); NULL
}

# Divide la pagina: individua l'intestazione (prima riga di testo) e il canale
# bianco tra le due colonne, cercato tra il 40% e il 60% della larghezza.
dividi <- function(bmp) {
  g <- if (length(dim(bmp)) == 3) bmp[1, , ] else bmp        # grigio: [larghezza, altezza]
  scuro <- as.integer(g) < 128; dim(scuro) <- dim(g)
  w <- nrow(scuro); h <- ncol(scuro)
  righe <- colSums(scuro)
  ink <- which(righe > w * 0.01)
  if (length(ink) < 10) return(NULL)
  top <- ink[1]; bot <- ink[length(ink)]
  i <- top; while (i < h && righe[i] > w * 0.005) i <- i + 1   # fine intestazione
  corpo <- scuro[, i:bot, drop = FALSE]
  col <- rowSums(corpo)
  lo <- round(w * 0.4); hi <- round(w * 0.6)
  liscio <- stats::filter(col[lo:hi], rep(1, 21), sides = 2); liscio[is.na(liscio)] <- Inf
  gut <- lo + which.min(liscio) - 1
  list(y0 = i, y1 = min(h, bot + 10), x = gut, w = w)
}

trascrivi_pagina <- function(pdf, s, p) {
  out <- file.path(CARTELLA, "testi_colonne", sprintf("%s_p%03d.txt", s, p))
  if (file.exists(out) && file.size(out) > 0) return(invisible(TRUE))
  eng <- tesseract("ita", options = list(tessedit_pageseg_mode = "6", user_defined_dpi = "300"))
  bmp <- pdf_render_page(pdf, page = p, dpi = DPI, numeric = FALSE, opw = "", upw = "")
  img <- image_convert(image_read(bmp), colorspace = "gray")
  d <- tryCatch(dividi(bmp), error = function(e) NULL)
  if (is.null(d)) {
    testo <- paste0(ocr(img, engine = eng), "<<<COLONNA_DESTRA>>>\n")
  } else {
    hh <- d$y1 - d$y0
    sx <- image_crop(img, sprintf("%dx%d+0+%d", d$x, hh, d$y0))
    dx <- image_crop(img, sprintf("%dx%d+%d+%d", d$w - d$x, hh, d$x, d$y0))
    testo <- paste0(ocr(sx, engine = eng), "<<<COLONNA_DESTRA>>>\n", ocr(dx, engine = eng))
  }
  writeLines(testo, paste0(out, ".tmp"), useBytes = TRUE)
  file.rename(paste0(out, ".tmp"), out)
  invisible(TRUE)
}

# ---- SEZIONE 3: esecuzione ----------------------------------------------
inizio <- Sys.time()
for (n in sedute) {
  pdf <- scarica(n); if (is.null(pdf)) next
  s <- sprintf("sed%03d", n); npag <- pdf_info(pdf)$pages
  fatte <- length(list.files(file.path(CARTELLA, "testi_colonne"), pattern = paste0("^", s, "_p\\d+\\.txt$")))
  if (fatte >= npag) next
  scrivi_log("Seduta ", n, ": ", npag, " pagine")
  parallel::mclapply(seq_len(npag), function(p) tryCatch(trascrivi_pagina(pdf, s, p),
                     error = function(e) scrivi_log("ERRORE ", s, " p.", p, ": ", conditionMessage(e))),
                     mc.cores = CORE)
  Sys.sleep(1)
}
n_txt <- length(list.files(file.path(CARTELLA, "testi_colonne"), pattern = "\\.txt$"))
scrivi_log("Fine: ", n_txt, " pagine in ", round(difftime(Sys.time(), inizio, units = "hours"), 1), " ore")
message("\nFatto. Scrivi in chat che hai finito.")
