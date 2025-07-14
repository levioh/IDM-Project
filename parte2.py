import pandas as pd
import numpy as np
from   mlxtend.frequent_patterns import fpgrowth
from   mlxtend.frequent_patterns import association_rules

path = "Project-file.csv" #pathname file
dataset = pd.read_csv(path)
dataset.isna().sum()

print("Elementi nel database prima della pulizia: {}".format(len(dataset)))
dataset.dropna(inplace=True)
print("Elementi nel database dopo  la pulizia: {}".format(len(dataset)))

required_cols = ['liv4', 'descr_liv4', 'descr_liv3', 'scontrino_id', 'r_qta_pezzi']

if all(col in dataset.columns for col in required_cols):
    dataset.loc[:, 'oggetto_completo'] = (
        dataset['liv4'].astype(str) + " - " +
        dataset['descr_liv3'] + " (" +
        dataset['descr_liv4'] + ")"
    )

    basket = pd.pivot_table(
        dataset,
        index='scontrino_id',
        columns='oggetto_completo',
        values='r_qta_pezzi',
        fill_value=0,
        aggfunc='sum' # Se uno scontrino ha lo stesso oggetto su più righe, somma le quantità
    )
else:
    print("Mancano una o più colonne necessarie nel DataFrame 'dataset'.")

print(basket)

#creiamo una matrice one-hot-encoded se l'item è presente o meno
def encode_values(x):
    return 0 if x <= 0 else 1

basket_encoded = basket.map(lambda element: encode_values(element))

#filtrare elementi con un solo elemento
condizione = (basket_encoded > 0).sum(axis=1) >= 2
basket_encoded_filter = basket_encoded[condizione]

basket_encoded_filter_bool = basket_encoded_filter.astype(bool)

frequent_itemsets = fpgrowth(
    basket_encoded_filter_bool, 
    min_support=0.03, 
    use_colnames=True
).sort_values("support",ascending=False)

print(frequent_itemsets)

print(association_rules(frequent_itemsets, metric="lift", min_threshold=1).sort_values("lift",ascending=False).reset_index(drop=True))