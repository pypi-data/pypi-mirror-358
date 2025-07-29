# Senegal Economic Data Explorer

Un package Python pour analyser facilement les données économiques du Sénégal et d'autres pays via l'API World Bank.

## 🚀 Installation

### Depuis PyPI (recommandé)
```bash
pip install senegal-economic-data-explorer
```

### Depuis les sources
```bash
git clone https://github.com/MARAMATA/senegal-economic-data-explorer.git
cd senegal-economic-data-explorer
pip install -e .
```

## 📖 Utilisation

### Import du package
```python
from data_explorer import get_export, get_import, get_pib
```

### Exemples d'utilisation

#### 1. Récupérer les exportations du Sénégal
```python
# Exportations du Sénégal de 2010 à 2023
df_export = get_export("SN", 2010, 2023)
print(df_export.head())
```

#### 2. Récupérer les importations
```python
# Importations du Sénégal
df_import = get_import("SN", 2015, 2023)
print(f"Total des importations en 2023: ${df_import[df_import['annee']==2023]['importations_usd'].values[0]:,.0f}")
```

#### 3. Récupérer le PIB d'un ou plusieurs pays
```python
# PIB du Sénégal uniquement
df_pib_sn = get_pib("SN", 2000, 2023)

# PIB de plusieurs pays
df_pib_multiple = get_pib(["SN", "FR", "US", "CN"], 2020, 2023)
print(df_pib_multiple.pivot(index='annee', columns='code_pays', values='pib_usd'))
```

### Exemple complet d'analyse
```python
import pandas as pd
import matplotlib.pyplot as plt
from data_explorer import get_export, get_import, get_pib

# Récupération des données
exports = get_export("SN", 2010, 2023)
imports = get_import("SN", 2010, 2023)
pib = get_pib("SN", 2010, 2023)

# Fusion des données
df = pd.merge(exports, imports, on=['code_pays', 'nom_pays', 'annee'])
df = pd.merge(df, pib, on=['code_pays', 'nom_pays', 'annee'])

# Calcul de la balance commerciale
df['balance_commerciale'] = df['exportations_usd'] - df['importations_usd']
df['ratio_export_pib'] = (df['exportations_usd'] / df['pib_usd']) * 100

# Visualisation
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Balance commerciale
ax1.plot(df['annee'], df['balance_commerciale']/1e9, marker='o')
ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5)
ax1.set_title('Balance commerciale du Sénégal')
ax1.set_ylabel('Milliards USD')
ax1.grid(True, alpha=0.3)

# Ratio exports/PIB
ax2.plot(df['annee'], df['ratio_export_pib'], marker='s', color='green')
ax2.set_title('Ratio Exportations/PIB')
ax2.set_xlabel('Année')
ax2.set_ylabel('Pourcentage (%)')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## 📊 Indicateurs disponibles

Le package utilise les indicateurs suivants de la World Bank :

- **PIB** : `NY.GDP.MKTP.CD` - Produit Intérieur Brut en USD courants
- **Population** : `SP.POP.TOTL` - Population totale
- **Exportations** : `NE.EXP.GNFS.CD` - Exportations de marchandises en USD
- **Importations** : `NE.IMP.GNFS.CD` - Importations de marchandises en USD
- **Dépenses publiques** : `GC.XPN.TOTL.GD.ZS` - Dépenses publiques en % du PIB

## 🔧 Développement

### Installation en mode développement
```bash
git clone https://github.com/MARAMATA/senegal-economic-data-explorer.git
cd senegal-economic-data-explorer
pip install -e ".[dev]"
```

### Lancer les tests
```bash
pytest
# ou avec coverage
pytest --cov=data_explorer
```

### Formater le code
```bash
black data_explorer tests
flake8 data_explorer tests
```

## 📦 Publier sur PyPI

1. Créer un compte sur [PyPI](https://pypi.org/account/register/)

2. Installer les outils nécessaires
```bash
pip install twine build
```

3. Construire le package
```bash
python -m build
```

4. Vérifier le package
```bash
twine check dist/*
```

5. Publier sur TestPyPI (optionnel, pour tester)
```bash
twine upload --repository testpypi dist/*
```

6. Publier sur PyPI
```bash
twine upload dist/*
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [World Bank API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation) pour l'accès aux données
- La communauté Python pour les excellentes bibliothèques pandas et requests

## 📞 Contact

Maramata DIOP - [GitHub](https://github.com/MARAMATA) - maramatad@gmail.com - Tel: +221 76 024 95 83

Lien du projet : [https://github.com/MARAMATA/senegal-economic-data-explorer](https://github.com/MARAMATA/senegal-economic-data-explorer)
