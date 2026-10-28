# =====================================================================
# Costituente 1946-48: dai CSV del dataset agli oggetti igraph
# From the dataset CSVs to igraph objects
#
# Uso / usage:  setwd("<cartella del repository>"); source("R/00_build_networks.R")
# Richiede / requires: igraph (install.packages("igraph"))
# Crea / creates:
#   g_cofirma_bip   costituenti x emendamenti (two-mode), con ruolo e abbinamento
#   g_cofirma       proiezione sui costituenti, peso = emendamenti firmati insieme
#   g_presentatore  rete diretta firmatario -> presentatore
#   g_voti_bip      costituenti x votazioni, segno +1 si', -1 no, 0 astenuto
#   g_menzioni      rete diretta delle menzioni nei discorsi (chi parla -> chi e' menzionato)
#   g_altri_bip     costituenti x altri atti co-firmati
# Con conservativa = TRUE usa solo gli archi con abbinamento esatto o corretto a mano.
# Gli stessi grafi sono gia' in data/graphml/ (scritti da pipeline/tools/esporta_graphml.py).
# =====================================================================
library(igraph)
conservativa <- FALSE
it <- function(f) read.csv(file.path("data", "it", f), stringsAsFactors = FALSE, encoding = "UTF-8")

nodi  <- it("costituenti_nodi.csv")
nodi_v <- nodi[, c("id_dep", "cognome", "nome", "lista_partito", "gruppo_iniziale", "gruppo_finale", "donna")]

# --- co-firma degli emendamenti ---
L  <- it(if (conservativa) "edgelist_emendamenti_conservativa.csv" else "edgelist_emendamenti.csv")
E  <- it("emendamenti_nodi.csv")
em_v <- data.frame(id_dep = E$id_emendamento, tipo = "emendamento", seduta = E$prima_seduta,
                   esito = E$esito, materia = E$materia, stringsAsFactors = FALSE)
v_bip <- merge(transform(nodi_v, tipo = "costituente"), em_v, all = TRUE)
g_cofirma_bip <- graph_from_data_frame(L[, c("id_dep", "id_emendamento", "ruolo", "abbinamento")],
                                       directed = FALSE, vertices = v_bip)
V(g_cofirma_bip)$type <- V(g_cofirma_bip)$tipo == "emendamento"
g_cofirma <- bipartite_projection(g_cofirma_bip, which = "false", multiplicity = TRUE)   # peso in E(g)$weight

# --- rete diretta: chi firma -> chi presenta ---
pres <- L[L$ruolo == "presentatore", c("id_emendamento", "id_dep")]; names(pres)[2] <- "presentatore"
dir  <- merge(L[L$ruolo == "firmatario", c("id_emendamento", "id_dep")], pres)
dir  <- aggregate(list(weight = rep(1, nrow(dir))), dir[, c("id_dep", "presentatore")], sum)
g_presentatore <- graph_from_data_frame(dir, directed = TRUE, vertices = nodi_v)

# --- voti per appello nominale, con segno ---
Ev <- it(if (conservativa) "edgelist_voti_conservativa.csv" else "edgelist_voti.csv")
Ev$segno <- ifelse(Ev$voto == "sì", 1, ifelse(Ev$voto == "no", -1, 0))
Vn <- it("voti_nodi.csv")
v_voti <- merge(transform(nodi_v, tipo = "costituente"),
                data.frame(id_dep = Vn$id_voto, tipo = "votazione", seduta = Vn$seduta, stringsAsFactors = FALSE), all = TRUE)
g_voti_bip <- graph_from_data_frame(Ev[, c("id_dep", "id_voto", "voto", "segno")], directed = FALSE, vertices = v_voti)
V(g_voti_bip)$type <- V(g_voti_bip)$tipo == "votazione"

# --- menzioni nei discorsi ---
M <- it("menzioni_discorso.csv")
M <- M[M$id_parlante != "" & !is.na(M$id_parlante) & M$id_menzionato != "" & !is.na(M$id_menzionato) & M$id_parlante != M$id_menzionato, ]
M <- aggregate(list(weight = rep(1, nrow(M))), M[, c("id_parlante", "id_menzionato")], sum)
g_menzioni <- graph_from_data_frame(M, directed = TRUE, vertices = nodi_v)

# --- altri atti co-firmati (strato multiplex) ---
A  <- it("altri_atti_nodi.csv"); LA <- it("edgelist_altri_atti.csv")
v_alt <- merge(transform(nodi_v, tipo = "costituente"),
               data.frame(id_dep = A$id_atto, tipo = A$tipo_atto, seduta = A$seduta, stringsAsFactors = FALSE), all = TRUE)
g_altri_bip <- graph_from_data_frame(LA, directed = FALSE, vertices = v_alt)
V(g_altri_bip)$type <- V(g_altri_bip)$tipo != "costituente"

# --- riepilogo / summary ---
cat("co-firma:", vcount(g_cofirma), "nodi,", ecount(g_cofirma), "legami; densita'", round(edge_density(g_cofirma), 4), "\n")
cat("presentatore: reciprocita'", round(reciprocity(g_presentatore), 3), "\n")
cat("menzioni: reciprocita'", round(reciprocity(g_menzioni), 3), "\n")
cat("assortativita' per gruppo (co-firma):",
    round(assortativity_nominal(g_cofirma, as.integer(factor(V(g_cofirma)$gruppo_finale)), directed = FALSE), 3), "\n")
# Esportazione / export (facoltativa):
# write_graph(g_cofirma, "cofirma.graphml", format = "graphml")
