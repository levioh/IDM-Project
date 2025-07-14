import pandas as pd
import numpy as np

path = "Project-file.csv" #pathname file
database = pd.read_csv(path)

#primo punto parte 1
store_id = 'puntovendita_id'  #se il csv dovesse avere un identificatore diverso sta puntovendita_id si può cambiare
id_negozi = database[store_id].unique()
print(f"ID dei punti vendita unici:{id_negozi}")

lista_negozi = {}

for id_negozio in id_negozi:
    db_negozio = database[database[store_id] == id_negozio]
    lista_negozi[id_negozio] = db_negozio
    print (f"\n--- Scontrini per il punto vendita ID: {id_negozio} ---")
    print (db_negozio)

#codice di debug per vedere se gli scontrini sono stati separati con successo

#dir_output = 'negozi separati'

#for id_negozio, db_negozio in lista_negozi.items():                
#    nome_file = f"{dir_output} scontrini_negozio_{id_negozio}.csv"
#    db_negozio.to_csv(nome_file,index=False)
#    print(f"\nScontrini per il punto vendita ID '{id_negozio}' salvati in: {nome_file}")

#secondo punto parte 1
for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Top 50 Articoli per il Negozio ID: {id_negozio} ###")

    # Verifica se il DataFrame del negozio ha tutte le colonne necessarie
    if all(col in db_negozio.columns for col in ['liv4', 'descr_liv4', 'descr_liv3']):
        # Crea una nuova colonna temporanea che combina ID, descrizione dell'articolo e descrizione della categoria
        #uso .loc perchè mi dava warning setting with copy.
        db_negozio.loc[:, 'oggetto_completo'] = (
            db_negozio['liv4'].astype(str) + " - " +
            db_negozio['descr_liv3'] + " (" +
            db_negozio['descr_liv4'] + ")"
        )
        top_articoli_negozio = db_negozio['oggetto_completo'].value_counts()

        # Seleziona i primi 50 articoli
        top_50_articoli_negozio = top_articoli_negozio.head(50)

        # Stampa i risultati
        if not top_50_articoli_negozio.empty:
            print(top_50_articoli_negozio)
        else:
            print("Nessun articolo trovato per questo negozio o le colonne rilevanti sono vuote.")
    else:
        # Se mancano una o più colonne, stampa un messaggio di avviso
        missing_cols = [col for col in ['liv4', 'descr_liv4', 'descr_liv3'] if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'.")

#terzo punto parte 1
print("--- Analisi Top 50 Articoli (ID, Descrizione Articolo, Categoria) per Ogni Negozio e Trimestre ---\n")


for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Analisi per il Negozio ID: {id_negozio} ###")
    if all(col in db_negozio.columns for col in ['liv4', 'descr_liv4', 'descr_liv3', 'data']):
        # Converti la colonna 'data' in formato datetime.
        db_negozio.loc[:, 'data_convertita'] = pd.to_datetime(db_negozio.loc[:,'data'], errors='coerce')

  
        db_negozio = db_negozio.dropna(subset=['data_convertita']).copy()

        # Estrai anno e trimestre utilizzando le funzioni .dt
        db_negozio.loc[:, 'anno'] = db_negozio['data_convertita'].dt.year
        db_negozio.loc[:, 'trimestre'] = db_negozio['data_convertita'].dt.quarter

        # Combina anno e trimestre
        db_negozio.loc[:, 'anno_trimestre'] = db_negozio['anno'].astype(str) + '-Q' + db_negozio['trimestre'].astype(str)

        db_negozio.loc[:, 'oggetto_completo'] = (
            db_negozio['liv4'].astype(str) + " - " +
            db_negozio['descr_liv4'] + " (" +
            db_negozio['descr_liv3'] + ")"
        )

        vendite_per_trimestre = db_negozio.groupby('anno_trimestre')['oggetto_completo'].value_counts().reset_index(name='conteggio')
        
        # top_50_per_trimestre = vendite_per_trimestre.nlargest(50, 'conteggio') questo non funziona perchè prende i top 50 più grandi 
        #a prescindere dal trimestre  dopo avere fatto il conteggio quindi mi prendeva solo 50 elementi , invece lambda mi prende 50 elementi
        # per ciascun trimestre

        top_50_per_trimestre = vendite_per_trimestre.groupby('anno_trimestre').apply(lambda x: x.nlargest(50, 'conteggio'), include_groups=False).reset_index()
        
        trimestri_unici = top_50_per_trimestre['anno_trimestre'].unique()
        # Ordina i trimestri per una visualizzazione più logica
        trimestri_ordinati = sorted(trimestri_unici)
        # Rimuovi le colonne di indice aggiuntive create da reset_index()
        
        columns_to_drop = [col for col in top_50_per_trimestre.columns if col.startswith('level_')]
        if columns_to_drop:
            top_50_per_trimestre = top_50_per_trimestre.drop(columns=columns_to_drop)
        for trimestre in trimestri_ordinati:
            print(f"\n--- Trimestre: {trimestre} ---")
            print(top_50_per_trimestre[top_50_per_trimestre['anno_trimestre'] == trimestre].to_string(index=False))
    else:
        missing_cols = [col for col in ['liv4', 'descr_liv4', 'descr_liv3', 'data'] if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'. Salto l'analisi per questo negozio.")

#quarto punto parte 1
print("--- Analisi Top 50 Articoli per Reddito (ID, Descrizione Articolo, Categoria) per Ogni Negozio ---\n")

for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Top 50 Articoli per Reddito per il Negozio ID: {id_negozio} ###")

    # Verifica se il DataFrame del negozio ha tutte le colonne necessarie per questa analisi
    required_cols_revenue = ['liv4', 'descr_liv4', 'descr_liv3', 'r_imponibile']
    if all(col in db_negozio.columns for col in required_cols_revenue):
        # Assicurati che 'r_imponibile' sia numerico e gestisci eventuali valori non validi
        db_negozio.loc[:, 'r_imponibile_numeric'] = pd.to_numeric(db_negozio['r_imponibile'], errors='coerce')

        # Rimuovi le righe dove 'r_imponibile' non è un numero valido
        db_negozio_cleaned = db_negozio.dropna(subset=['r_imponibile_numeric']).copy()

        if not db_negozio_cleaned.empty:
            # Crea la colonna 'oggetto_completo' se non esiste già
            if 'oggetto_completo' not in db_negozio_cleaned.columns:
                db_negozio_cleaned.loc[:, 'oggetto_completo'] = (
                    db_negozio_cleaned['liv4'].astype(str) + " - " +
                    db_negozio_cleaned['descr_liv3'] + " (" +
                    db_negozio_cleaned['descr_liv4'] + ")"
                )

            # Calcola il reddito totale per ogni oggetto completo
            reddito_per_oggetto = db_negozio_cleaned.groupby('oggetto_completo')['r_imponibile_numeric'].sum()

            # Seleziona i primi 50 articoli che hanno generato più reddito
            top_50_reddito_negozio = reddito_per_oggetto.nlargest(50)

            # Stampa i risultati
            if not top_50_reddito_negozio.empty:
                #stampa solo le prime due cifre decimali le altre cifre decimali non sono importanti per il reddito
                print(top_50_reddito_negozio.to_string(float_format="%.2f"))
            else:
                print("Nessun articolo con reddito valido trovato per questo negozio.")
        else:
            print("Nessun dato valido per 'r_imponibile' dopo la pulizia per questo negozio.")
    else:
        missing_cols = [col for col in required_cols_revenue if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'. Salto l'analisi del reddito per questo negozio.")

#quinto punto parte 1

for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Analisi Reddito per Trimestre per il Negozio ID: {id_negozio} ###")
    required_cols_quarterly_revenue = ['liv4', 'descr_liv4', 'descr_liv3', 'data', 'r_imponibile']
    if all(col in db_negozio.columns for col in required_cols_quarterly_revenue):
        # Converti la colonna 'data' in formato datetime.
        db_negozio.loc[:, 'data_convertita'] = pd.to_datetime(db_negozio.loc[:,'data'], errors='coerce')
        # Assicurati che 'r_imponibile' sia numerico
        db_negozio.loc[:, 'r_imponibile_numeric'] = pd.to_numeric(db_negozio['r_imponibile'], errors='coerce')

        # Rimuovi le righe con date o redditi non validi
        db_negozio_cleaned = db_negozio.dropna(subset=['data_convertita', 'r_imponibile_numeric']).copy()

        if not db_negozio_cleaned.empty:
            # Estrai anno e trimestre utilizzando le funzioni .dt
            db_negozio_cleaned.loc[:, 'anno'] = db_negozio_cleaned['data_convertita'].dt.year
            db_negozio_cleaned.loc[:, 'trimestre'] = db_negozio_cleaned['data_convertita'].dt.quarter

            # Combina anno e trimestre
            db_negozio_cleaned.loc[:, 'anno_trimestre'] = db_negozio_cleaned['anno'].astype(str) + '-Q' + db_negozio_cleaned['trimestre'].astype(str)

            # Crea la colonna 'oggetto_completo'
            db_negozio_cleaned.loc[:, 'oggetto_completo'] = (
                db_negozio_cleaned['liv4'].astype(str) + " - " +
                db_negozio_cleaned['descr_liv3'] + " (" +
                db_negozio_cleaned['descr_liv4'] + ")"
            )

            # Calcola il reddito totale per oggetto per ogni trimestre
            reddito_per_trimestre = db_negozio_cleaned.groupby(['anno_trimestre', 'oggetto_completo'])['r_imponibile_numeric'].sum().reset_index(name='reddito_totale')

            # Seleziona i primi 50 articoli per reddito per ogni trimestre
            top_50_reddito_per_trimestre = reddito_per_trimestre.groupby('anno_trimestre').apply(lambda x: x.nlargest(50, 'reddito_totale'), include_groups=False).reset_index()

            # Rimuovi le colonne di indice aggiuntive create da reset_index()
            columns_to_drop = [col for col in top_50_reddito_per_trimestre.columns if col.startswith('level_')]
            if columns_to_drop:
                top_50_reddito_per_trimestre = top_50_reddito_per_trimestre.drop(columns=columns_to_drop)
            
            # Stampa i risultati per ogni trimestre ordinato
            trimestri_unici = top_50_reddito_per_trimestre['anno_trimestre'].unique()
            trimestri_ordinati = sorted(trimestri_unici)
            for trimestre in trimestri_ordinati:
                print(f"\n--- Trimestre: {trimestre} ---")
                # Filtra per il trimestre corrente e stampa, formattando il reddito
                print(top_50_reddito_per_trimestre[top_50_reddito_per_trimestre['anno_trimestre'] == trimestre].to_string(index=False, float_format="%.2f"))
        else:
            print("Nessun dato valido per 'data' o 'r_imponibile' dopo la pulizia per questo negozio.")
    else:
        missing_cols = [col for col in required_cols_quarterly_revenue if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'. Salto l'analisi del reddito per trimestre per questo negozio.")

"parte 1 punto 6 simile al punto 2"

for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Top 100 Utenti per il Negozio ID: {id_negozio} ###")

    # Verifica se la colonna 'tessera' è presente nel DataFrame del negozio
    if 'tessera' in db_negozio.columns:
        db_negozio_cleaned = db_negozio.dropna(subset=['tessera']).copy()

        if not db_negozio_cleaned.empty:
            frequenza_tessere = db_negozio_cleaned['tessera'].value_counts()

            top_100_tessere_negozio = frequenza_tessere.head(100)

            if not top_100_tessere_negozio.empty:
                print(top_100_tessere_negozio.to_string())

            else:
                print("Nessuna tessera valida trovata per questo negozio o le colonne rilevanti sono vuote.")
    else:
        print(f"Attenzione: La colonna 'tessera' non è presente nel DataFrame del negozio '{id_negozio}'. Salto l'analisi degli utenti per questo negozio.")

"settimo punto parte 1"


for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Top 100 Utenti per Spesa nel Negozio ID: {id_negozio} ###")

    # Verifica se le colonne 'tessera' e 'r_imponibile' sono presenti
    required_cols_user_revenue = ['tessera', 'r_imponibile']
    if all(col in db_negozio.columns for col in required_cols_user_revenue):
        # Converti 'r_imponibile' in numerico e gestisci i non validi
        db_negozio.loc[:, 'r_imponibile_numeric'] = pd.to_numeric(db_negozio['r_imponibile'], errors='coerce')

        # Pulisci il DataFrame rimuovendo righe con tessera o imponibile non validi
        db_negozio_cleaned = db_negozio.dropna(subset=['tessera', 'r_imponibile_numeric']).copy()

        if not db_negozio_cleaned.empty:
            # Calcola la spesa totale per ogni tessera
            spesa_per_tessera = db_negozio_cleaned.groupby('tessera')['r_imponibile_numeric'].sum()

            # Seleziona le prime 100 tessere che hanno speso di più
            top_100_spesa_tessere_negozio = spesa_per_tessera.nlargest(100)

            # Stampa i risultati formattando il reddito a 2 cifre decimali
            if not top_100_spesa_tessere_negozio.empty:
                print(top_100_spesa_tessere_negozio.to_string(float_format="%.2f"))
            
            else:
                print("Nessuna tessera con spesa valida trovata per questo negozio o le colonne rilevanti sono vuote.")
    else:
        missing_cols = [col for col in required_cols_user_revenue if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'. Salto l'analisi della spesa degli utenti per questo negozio.")

#ottavo punto parte 1
print("--- Analisi Top 100 Utenti per Ogni Negozio e Trimestre ---\n")


for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Analisi per il Negozio ID: {id_negozio} ###")
    if all(col in db_negozio.columns for col in ['tessera', 'data']):
        # Converti la colonna 'data' in formato datetime.
        db_negozio.loc[:, 'data_convertita'] = pd.to_datetime(db_negozio.loc[:,'data'], errors='coerce')

  
        db_negozio = db_negozio.dropna(subset=['data_convertita']).copy()

        # Estrai anno e trimestre utilizzando le funzioni .dt
        db_negozio.loc[:, 'anno'] = db_negozio['data_convertita'].dt.year
        db_negozio.loc[:, 'trimestre'] = db_negozio['data_convertita'].dt.quarter

        # Combina anno e trimestre
        db_negozio.loc[:, 'anno_trimestre'] = db_negozio['anno'].astype(str) + '-Q' + db_negozio['trimestre'].astype(str)

        vendite_per_trimestre = db_negozio.groupby('anno_trimestre')['tessera'].value_counts().reset_index(name='conteggio')

        top_100_per_trimestre = vendite_per_trimestre.groupby('anno_trimestre').apply(lambda x: x.nlargest(100, 'conteggio'), include_groups=False).reset_index()
 
        trimestri_unici = top_100_per_trimestre['anno_trimestre'].unique()
        # Ordina i trimestri per una visualizzazione più logica
        trimestri_ordinati = sorted(trimestri_unici)
        # Rimuovi le colonne di indice aggiuntive create da reset_index()
        columns_to_drop = [col for col in top_100_per_trimestre.columns if col.startswith('level_')]
        if columns_to_drop:
            top_100_per_trimestre = top_100_per_trimestre.drop(columns=columns_to_drop)
        for trimestre in trimestri_ordinati:
            print(f"\n--- Trimestre: {trimestre} ---")
            print(top_100_per_trimestre[top_100_per_trimestre['anno_trimestre'] == trimestre].to_string(index=False))
    else:
        missing_cols = [col for col in ['tessera', 'data'] if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'. Salto l'analisi per questo negozio.")

#nono punto parte 1

for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Analisi Top 100 utenti che spendono di più per Trimestre per il Negozio ID: {id_negozio} ###")
    required_cols_quarterly_revenue = ['tessera', 'data', 'r_imponibile']
    if all(col in db_negozio.columns for col in required_cols_quarterly_revenue):
        # Converti la colonna 'data' in formato datetime.
        db_negozio.loc[:, 'data_convertita'] = pd.to_datetime(db_negozio.loc[:,'data'], errors='coerce')
        # Assicurati che 'r_imponibile' sia numerico
        db_negozio.loc[:, 'r_imponibile_numeric'] = pd.to_numeric(db_negozio['r_imponibile'], errors='coerce')

        # Rimuovi le righe con date o redditi non validi
        db_negozio_cleaned = db_negozio.dropna(subset=['data_convertita', 'r_imponibile_numeric']).copy()

        if not db_negozio_cleaned.empty:
            # Estrai anno e trimestre utilizzando le funzioni .dt
            db_negozio_cleaned.loc[:, 'anno'] = db_negozio_cleaned['data_convertita'].dt.year
            db_negozio_cleaned.loc[:, 'trimestre'] = db_negozio_cleaned['data_convertita'].dt.quarter

            # Combina anno e trimestre
            db_negozio_cleaned.loc[:, 'anno_trimestre'] = db_negozio_cleaned['anno'].astype(str) + '-Q' + db_negozio_cleaned['trimestre'].astype(str)

            # Calcola il reddito totale per oggetto per ogni trimestre
            reddito_per_trimestre = db_negozio_cleaned.groupby(['anno_trimestre', 'tessera'])['r_imponibile_numeric'].sum().reset_index(name='reddito_totale')

            # Seleziona i primi 50 articoli per reddito per ogni trimestre
            top_100_reddito_per_trimestre = reddito_per_trimestre.groupby('anno_trimestre').apply(lambda x: x.nlargest(100, 'reddito_totale'), include_groups=False).reset_index()

            # Rimuovi le colonne di indice aggiuntive create da reset_index()
            columns_to_drop = [col for col in top_100_reddito_per_trimestre.columns if col.startswith('level_')]
            if columns_to_drop:
                top_100_reddito_per_trimestre = top_100_reddito_per_trimestre.drop(columns=columns_to_drop)
            
            # Stampa i risultati per ogni trimestre ordinato
            trimestri_unici = top_100_reddito_per_trimestre['anno_trimestre'].unique()
            trimestri_ordinati = sorted(trimestri_unici)
            for trimestre in trimestri_ordinati:
                print(f"\n--- Trimestre: {trimestre} ---")
                # Filtra per il trimestre corrente e stampa, formattando il reddito
                print(top_100_reddito_per_trimestre[top_100_reddito_per_trimestre['anno_trimestre'] == trimestre].to_string(index=False, float_format="%.2f"))
        else:
            print("Nessun dato valido per 'data' o 'r_imponibile' dopo la pulizia per questo negozio.")
    else:
        missing_cols = [col for col in required_cols_quarterly_revenue if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'. Salto l'analisi del reddito per trimestre per questo negozio.")

#punto decimo e undicesimo parte 1

print("--- Analisi Top/Bottom 100 Utenti per Acquisti Scontati per Ogni Negozio ---\n")

for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Analisi Sconti per il Negozio ID: {id_negozio} ###")

    # Verifica se le colonne necessarie sono presenti
    required_cols_discount = ['tessera', 'r_sconto']

    if all(col in db_negozio.columns for col in required_cols_discount):
        # Assicurati che 'r_sconto' sia numerico e gestisci eventuali valori non validi
        db_negozio.loc[:, 'r_sconto_numeric'] = pd.to_numeric(db_negozio['r_sconto'], errors='coerce')

        # Rimuovi le righe con tessera o r_sconto non validi
        db_negozio_cleaned = db_negozio.dropna(subset=['tessera', 'r_sconto_numeric']).copy()

        if not db_negozio_cleaned.empty:
            # --- Utenti che comprano PRODOTTI SCONTATI (r_sconto > 0.01) ---
            df_scontati = db_negozio_cleaned[db_negozio_cleaned['r_sconto_numeric'] > 0.01].copy()

            if not df_scontati.empty:
                frequenza_tessere_scontati = df_scontati['tessera'].value_counts()

                # Top 100 utenti più frequenti con prodotti scontati
                top_100_scontati = frequenza_tessere_scontati.head(100)
                print("\n--- Top 100 Utenti che comprano PRODOTTI SCONTATI ---")
                if not top_100_scontati.empty:
                    print(top_100_scontati.to_string())
                else:
                    print("Nessuna tessera trovata che abbia comprato prodotti scontati in questo negozio.")
            else:
                print("Nessun prodotto scontato trovato per questo negozio.")


            # --- Utenti che comprano MENO prodotti SCONTATI (r_sconto = 0) ---
            # Questo significa utenti che acquistano a prezzo pieno (o con sconti irrilevanti <= 0.01)
            df_non_scontati = db_negozio_cleaned[db_negozio_cleaned['r_sconto_numeric'] == 0].copy()

            if not df_non_scontati.empty:
                frequenza_tessere_non_scontati = df_non_scontati['tessera'].value_counts()

                # Le 100 tessere più frequenti che comprano *solo* prodotti a prezzo pieno
                # Per "comprano meno prodotti scontati" si intende che hanno una frequenza più alta sugli articoli a prezzo pieno
                # o una frequenza molto bassa (o nulla) su quelli scontati.
                #identifichiamo le 100 tessere che hanno la più alta frequenza di acquisti *non scontati*.
                top_100_non_scontati = frequenza_tessere_non_scontati.head(100)
                print("\n--- Top 100 Utenti che comprano PRODOTTI NON SCONTATI (o con meno prodotti scontati) ---")
                if not top_100_non_scontati.empty:
                    print(top_100_non_scontati.to_string())
                else:
                    print("Nessuna tessera trovata che abbia comprato prodotti non scontati in questo negozio.")
            else:
                print("Nessun prodotto non scontato trovato per questo negozio.")

        else:
            print("Nessun dato valido per 'tessera' o 'r_sconto' dopo la pulizia per questo negozio.")
    else:
        missing_cols = [col for col in required_cols_discount if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'. Salto l'analisi degli sconti per questo negozio.")


#dodicesimo punto parte 1
for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Top 100 Cassieri per il Negozio ID: {id_negozio} ###")

    # Verifica se il DataFrame del negozio ha tutte le colonne necessarie
    if all(col in db_negozio.columns for col in ['cassiere']):
        top_cassieri_negozio = db_negozio['cassiere'].value_counts()

        # Seleziona i primi 100 articoli
        top_100_cassieri = top_cassieri_negozio.head(100)

        # Stampa i risultati
        if not top_100_cassieri.empty:
            print(top_100_cassieri)
        else:
            print("Nessun cassiere trovato per questo negozio o le colonne rilevanti sono vuote.")
    else:
        # Se mancano una o più colonne, stampa un messaggio di avviso
        missing_cols = [col for col in ['cassiere'] if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'.")

#tredicesimo punto parte 1
print("--- Analisi Top 100 Cassieri per Reddito per Ogni Negozio ---\n")

for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Top 100 Cassieri per Reddito per il Negozio ID: {id_negozio} ###")

    # Verifica se il DataFrame del negozio ha tutte le colonne necessarie per questa analisi
    required_cols_revenue = ['cassiere', 'r_imponibile']
    if all(col in db_negozio.columns for col in required_cols_revenue):
        # Assicurati che 'r_imponibile' sia numerico e gestisci eventuali valori non validi
        db_negozio.loc[:, 'r_imponibile_numeric'] = pd.to_numeric(db_negozio['r_imponibile'], errors='coerce')

        # Rimuovi le righe dove 'r_imponibile' non è un numero valido
        db_negozio_cleaned = db_negozio.dropna(subset=['r_imponibile_numeric']).copy()

        if not db_negozio_cleaned.empty:

            # Calcola il reddito totale per ogni cassiere
            reddito_per_cassiere = db_negozio_cleaned.groupby('cassiere')['r_imponibile_numeric'].sum()

            # Seleziona i primi 50 articoli che hanno generato più reddito
            top_100_reddito_negozio = reddito_per_cassiere.nlargest(100)

            # Stampa i risultati
            if not top_100_reddito_negozio.empty:
                #stampa solo le prime due cifre decimali le altre cifre decimali non sono importanti per il reddito
                print(top_100_reddito_negozio.to_string(float_format="%.2f"))
            else:
                print("Nessun cassiere con reddito valido trovato per questo negozio.")
        else:
            print("Nessun dato valido per 'r_imponibile' dopo la pulizia per questo negozio.")
    else:
        missing_cols = [col for col in required_cols_revenue if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'. Salto l'analisi del reddito per questo negozio.")


#quattordicesimo punto 

for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Top 100 livelli merceologici per il Negozio ID: {id_negozio} ###")

    # Verifica se il DataFrame del negozio ha tutte le colonne necessarie
    if all(col in db_negozio.columns for col in ['liv1', 'liv2', 'liv3', 'liv4', 'descr_liv4', 'descr_liv3']):

        top_liv1_negozio = db_negozio['liv1'].value_counts()
        top_liv2_negozio = db_negozio['liv2'].value_counts()
        top_liv3_negozio = db_negozio['liv3'].value_counts()
        top_liv4_negozio = db_negozio['liv4'].value_counts()

        # Seleziona i primi 50 articoli
        top_100_liv1_negozio = top_liv1_negozio.head(100)
        top_100_liv2_negozio = top_liv2_negozio.head(100)
        top_100_liv3_negozio = top_liv3_negozio.head(100)
        top_100_liv4_negozio = top_liv4_negozio.head(100)

        # Stampa i risultati
        if not top_100_liv1_negozio.empty:
            print(top_100_liv1_negozio)
            print("\n")
        else:
            print("Nessun articolo trovato per questo negozio o le colonne rilevanti sono vuote.")
        if not top_100_liv2_negozio.empty:
            print(top_100_liv2_negozio)
            print("\n")
        else:
            print("Nessun articolo trovato per questo negozio o le colonne rilevanti sono vuote.")
        if not top_100_liv3_negozio.empty:
            print(top_100_liv3_negozio)
            print("\n")
        else:
            print("Nessun articolo trovato per questo negozio o le colonne rilevanti sono vuote.")
        if not top_100_liv4_negozio.empty:
            print(top_100_liv4_negozio)
            print("\n")
        else:
            print("Nessun articolo trovato per questo negozio o le colonne rilevanti sono vuote.")
    else:
        # Se mancano una o più colonne, stampa un messaggio di avviso
        missing_cols = [col for col in ['liv1', 'liv2', 'liv3', 'liv4', 'descr_liv4', 'descr_liv3'] if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'.")

#quindicesimo punto

for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Top 100 Reddito livelli merceologici per il Negozio ID: {id_negozio} ###")

    # Verifica se il DataFrame del negozio ha tutte le colonne necessarie
    if all(col in db_negozio.columns for col in ['liv1', 'liv2', 'liv3', 'liv4', 'descr_liv4', 'descr_liv3','r_imponibile']):

        db_negozio.loc[:, 'r_imponibile_numeric'] = pd.to_numeric(db_negozio['r_imponibile'], errors='coerce')

        db_negozio_cleaned = db_negozio.dropna(subset=['r_imponibile_numeric']).copy()

        reddito_liv1_negozio = db_negozio_cleaned.groupby('liv1')['r_imponibile_numeric'].sum()    
        reddito_liv2_negozio = db_negozio_cleaned.groupby('liv2')['r_imponibile_numeric'].sum()
        reddito_liv3_negozio = db_negozio_cleaned.groupby('liv3')['r_imponibile_numeric'].sum()
        reddito_liv4_negozio = db_negozio_cleaned.groupby('liv4')['r_imponibile_numeric'].sum()

        # Seleziona i primi 50 articoli
        top_100_liv1_negozio = reddito_liv1_negozio.head(100)
        top_100_liv2_negozio = reddito_liv2_negozio.head(100)
        top_100_liv3_negozio = reddito_liv3_negozio.head(100)
        top_100_liv4_negozio = reddito_liv4_negozio.head(100)

         # Stampa i risultati
        if not top_100_liv1_negozio.empty:
            print(top_100_liv1_negozio)
            print("\n")
        else:
            print("Nessun articolo trovato per questo negozio o le colonne rilevanti sono vuote.")
        if not top_100_liv2_negozio.empty:
            print(top_100_liv2_negozio)
            print("\n")
        else:
            print("Nessun articolo trovato per questo negozio o le colonne rilevanti sono vuote.")
        if not top_100_liv3_negozio.empty:
            print(top_100_liv3_negozio)
            print("\n")
        else:
            print("Nessun articolo trovato per questo negozio o le colonne rilevanti sono vuote.")
        if not top_100_liv4_negozio.empty:
            print(top_100_liv4_negozio)
            print("\n")
        else:
            print("Nessun articolo trovato per questo negozio o le colonne rilevanti sono vuote.")
    else:
        # Se mancano una o più colonne, stampa un messaggio di avviso
        missing_cols = [col for col in ['liv1', 'liv2', 'liv3', 'liv4', 'descr_liv4', 'descr_liv3'] if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'.")

#sedicesimo punto

for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Top 100 livelli merceologici per il Negozio ID per i trimestri: {id_negozio} ###")

    # Verifica se il DataFrame del negozio ha tutte le colonne necessarie
    if all(col in db_negozio.columns for col in ['liv1', 'liv2', 'liv3', 'liv4', 'descr_liv4', 'descr_liv3','data']):

        db_negozio.loc[:, 'data_convertita'] = pd.to_datetime(db_negozio.loc[:,'data'], errors='coerce')

        db_negozio = db_negozio.dropna(subset=['data_convertita']).copy()

        #Estrai anno e trimeste utilizzando le funzioni .dt
        db_negozio.loc[:, 'anno'] = db_negozio['data_convertita'].dt.year
        db_negozio.loc[:, 'trimestre'] = db_negozio['data_convertita'].dt.quarter

        #combina anno e trimestre
        db_negozio.loc[:,'anno_trimestre'] = db_negozio['anno'].astype(str) + '-Q' + db_negozio['trimestre'].astype(str)
        
        top_liv1_negozio = db_negozio.groupby('liv1')['anno_trimestre'].value_counts().reset_index(name='conteggio')
        top_liv2_negozio = db_negozio.groupby('liv2')['anno_trimestre'].value_counts().reset_index(name='conteggio')
        top_liv3_negozio = db_negozio.groupby('liv3')['anno_trimestre'].value_counts().reset_index(name='conteggio')
        top_liv4_negozio = db_negozio.groupby('liv4')['anno_trimestre'].value_counts().reset_index(name='conteggio')

        # Seleziona i primi 100 articoli
        
        top_100_liv1_negozio = top_liv1_negozio.groupby('anno_trimestre').apply(lambda x: x.nlargest(100, 'conteggio'), include_groups=False).reset_index()
        top_100_liv2_negozio = top_liv2_negozio.groupby('anno_trimestre').apply(lambda x: x.nlargest(100, 'conteggio'), include_groups=False).reset_index()
        top_100_liv3_negozio = top_liv3_negozio.groupby('anno_trimestre').apply(lambda x: x.nlargest(100, 'conteggio'), include_groups=False).reset_index()
        top_100_liv4_negozio = top_liv4_negozio.groupby('anno_trimestre').apply(lambda x: x.nlargest(100, 'conteggio'), include_groups=False).reset_index()

        trimestri_unici_liv1 = top_100_liv1_negozio['anno_trimestre'].unique()

        trimestri_ordinati_liv1 = sorted(trimestri_unici_liv1)

        trimestri_unici_liv2 = top_100_liv2_negozio['anno_trimestre'].unique()

        trimestri_ordinati_liv2 = sorted(trimestri_unici_liv2)

        trimestri_unici_liv3 = top_100_liv3_negozio['anno_trimestre'].unique()

        trimestri_ordinati_liv3 = sorted(trimestri_unici_liv3)

        trimestri_unici_liv4 = top_100_liv4_negozio['anno_trimestre'].unique()

        trimestri_ordinati_liv4 = sorted(trimestri_unici_liv3)

        for trimestre in trimestri_ordinati_liv1:
            print(f"\n--- Trimestre: {trimestre} ---")
            print(top_100_liv1_negozio[top_100_liv1_negozio['anno_trimestre'] == trimestre].to_string(index=False))

        for trimestre in trimestri_ordinati_liv2:
            print(f"\n--- Trimestre: {trimestre} ---")
            print(top_100_liv2_negozio[top_100_liv2_negozio['anno_trimestre'] == trimestre].to_string(index=False))

        for trimestre in trimestri_ordinati_liv3:
            print(f"\n--- Trimestre: {trimestre} ---")
            print(top_100_liv3_negozio[top_100_liv3_negozio['anno_trimestre'] == trimestre].to_string(index=False))

        for trimestre in trimestri_ordinati_liv4:
            print(f"\n--- Trimestre: {trimestre} ---")
            print(top_100_liv4_negozio[top_100_liv4_negozio['anno_trimestre'] == trimestre].to_string(index=False))
    else:
        # Se mancano una o più colonne, stampa un messaggio di avviso
        missing_cols = [col for col in ['liv1', 'liv2', 'liv3', 'liv4', 'descr_liv4', 'descr_liv3', 'data'] if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'.")

#diciassettesimo punto

for id_negozio, db_negozio in lista_negozi.items():
    print(f"\n### Top 100 Reddito livelli merceologici per il Negozio ID per i Trimestri: {id_negozio} ###")

    # Verifica se il DataFrame del negozio ha tutte le colonne necessarie
    if all(col in db_negozio.columns for col in ['liv1', 'liv2', 'liv3', 'liv4', 'descr_liv4', 'descr_liv3','r_imponibile','data']):

        db_negozio.loc[:, 'data_convertita'] = pd.to_datetime(db_negozio.loc[:,'data'], errors='coerce')
        
        db_negozio.loc[:, 'r_imponibile_numeric'] = pd.to_numeric(db_negozio['r_imponibile'], errors='coerce')
        
        db_negozio_cleaned= db_negozio.dropna(subset=['data_convertita', 'r_imponibile_numeric']).copy()
        
        #Estrai anno e trimeste utilizzando le funzioni .dt
        db_negozio_cleaned.loc[:, 'anno'] = db_negozio['data_convertita'].dt.year
        db_negozio_cleaned.loc[:, 'trimestre'] = db_negozio['data_convertita'].dt.quarter
        
        #combina anno e trimestre
        db_negozio_cleaned.loc[:,'anno_trimestre'] = db_negozio_cleaned['anno'].astype(str) + '-Q' + db_negozio_cleaned['trimestre'].astype(str)
        
#mi da errore
        reddito_liv1_negozio = db_negozio_cleaned.groupby(['liv1','anno_trimestre'])['r_imponibile_numeric'].sum().reset_index(name='reddito')   
        reddito_liv2_negozio = db_negozio_cleaned.groupby(['liv2','anno_trimestre'])['r_imponibile_numeric'].sum().reset_index(name='reddito')  
        reddito_liv3_negozio = db_negozio_cleaned.groupby(['liv3','anno_trimestre'])['r_imponibile_numeric'].sum().reset_index(name='reddito')  
        reddito_liv4_negozio = db_negozio_cleaned.groupby(['liv4','anno_trimestre'])['r_imponibile_numeric'].sum().reset_index(name='reddito')  

        # Seleziona i primi 100 articoli
        top_100_liv1_negozio = reddito_liv1_negozio.groupby('anno_trimestre').apply(lambda x: x.nlargest(100, 'reddito'), include_groups=False).reset_index()
        top_100_liv2_negozio = reddito_liv2_negozio.groupby('anno_trimestre').apply(lambda x: x.nlargest(100, 'reddito'), include_groups=False).reset_index()
        top_100_liv3_negozio = reddito_liv3_negozio.groupby('anno_trimestre').apply(lambda x: x.nlargest(100, 'reddito'), include_groups=False).reset_index()
        top_100_liv4_negozio = reddito_liv4_negozio.groupby('anno_trimestre').apply(lambda x: x.nlargest(100, 'reddito'), include_groups=False).reset_index()

        columns_to_drop = [col for col in top_100_liv1_negozio.columns if col.startswith('level_')]
        if columns_to_drop:
            top_100_liv1_negozio = top_100_liv1_negozio.drop(columns=columns_to_drop)

        columns_to_drop = [col for col in top_100_liv2_negozio.columns if col.startswith('level_')]
        if columns_to_drop:
            top_100_liv2_negozio = top_100_liv2_negozio.drop(columns=columns_to_drop)   

        columns_to_drop = [col for col in top_100_liv3_negozio.columns if col.startswith('level_')]
        if columns_to_drop:
            top_100_liv3_negozio = top_100_liv3_negozio.drop(columns=columns_to_drop)

        columns_to_drop = [col for col in top_100_liv4_negozio.columns if col.startswith('level_')]
        if columns_to_drop:
            top_100_liv4_negozio = top_100_liv4_negozio.drop(columns=columns_to_drop)
            
         # Stampa i risultati
        trimestri_unici_liv1 = top_100_liv1_negozio['anno_trimestre'].unique()

        trimestri_ordinati_liv1 = sorted(trimestri_unici_liv1)

        trimestri_unici_liv2 = top_100_liv2_negozio['anno_trimestre'].unique()

        trimestri_ordinati_liv2 = sorted(trimestri_unici_liv2)

        trimestri_unici_liv3 = top_100_liv3_negozio['anno_trimestre'].unique()

        trimestri_ordinati_liv3 = sorted(trimestri_unici_liv3)

        trimestri_unici_liv4 = top_100_liv4_negozio['anno_trimestre'].unique()

        trimestri_ordinati_liv4 = sorted(trimestri_unici_liv3)

        for trimestre in trimestri_ordinati_liv1:
            print(f"\n--- Trimestre: {trimestre} ---")
            print(top_100_liv1_negozio[top_100_liv1_negozio['anno_trimestre'] == trimestre].to_string(index=False))

        for trimestre in trimestri_ordinati_liv2:
            print(f"\n--- Trimestre: {trimestre} ---")
            print(top_100_liv2_negozio[top_100_liv2_negozio['anno_trimestre'] == trimestre].to_string(index=False))

        for trimestre in trimestri_ordinati_liv3:
            print(f"\n--- Trimestre: {trimestre} ---")
            print(top_100_liv3_negozio[top_100_liv3_negozio['anno_trimestre'] == trimestre].to_string(index=False))

        for trimestre in trimestri_ordinati_liv4:
            print(f"\n--- Trimestre: {trimestre} ---")
            print(top_100_liv4_negozio[top_100_liv4_negozio['anno_trimestre'] == trimestre].to_string(index=False))
        
    else:
        # Se mancano una o più colonne, stampa un messaggio di avviso
        missing_cols = [col for col in ['liv1', 'liv2', 'liv3', 'liv4', 'descr_liv4', 'descr_liv3'] if col not in db_negozio.columns]
        print(f"Attenzione: Le colonne {missing_cols} non sono presenti nel DataFrame del negozio '{id_negozio}'.")
