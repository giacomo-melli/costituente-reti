"""Crea il file di verifica manuale: un emendamento per riga, con link alla pagina del PDF."""
import sys, os, pandas as pd
D = sys.argv[1]; OUT = sys.argv[2]
n = pd.read_csv(os.path.join(D, 'tools', 'costituenti_nomi.csv')).set_index('id_dep')
E = pd.read_csv(os.path.join(OUT, 'emendamenti.csv')); M = pd.read_csv(os.path.join(OUT, 'menzioni.csv'))
first = M.sort_values(['seduta', 'pagina']).groupby('id_emendamento').first()
E['come_stampato'] = E.id_emendamento.map(first.testo_stampato)
E['firmatari_abbinati'] = E.firmatari.map(lambda s: ', '.join(f"{n.loc[i,'cognome']} {n.loc[i,'nome']}" for i in s.split('|')))
E['completo'] = E.completo.map({1: 'sì', 0: 'no (ed altri)'})
E['fonte'] = E.fonte.map({'firma': 'blocco di firma', 'presentazione': 'formula di presentazione'})
V = E[['id_emendamento', 'prima_seduta', 'data', 'pagina', 'url_pdf', 'fonte', 'completo', 'come_stampato', 'n_firmatari', 'firmatari_abbinati']].copy()
for c in ['emendamento_vero_(s/n)', 'firmatari_corretti_(s/n)', 'firmatari_mancanti_o_errati', 'note']:
    V[c] = ''
V.to_csv(os.path.join(OUT, 'VERIFICA.csv'), index=False, encoding='utf-8-sig')
print(len(V), 'righe da verificare')
