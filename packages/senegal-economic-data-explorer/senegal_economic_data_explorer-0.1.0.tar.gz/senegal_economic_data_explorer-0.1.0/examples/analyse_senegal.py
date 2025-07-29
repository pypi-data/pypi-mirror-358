"""
Exemple d'utilisation du package data_explorer pour analyser l'économie du Sénégal
"""

import pandas as pd
import matplotlib.pyplot as plt
from data_explorer import get_export, get_import, get_pib

def main():
    # Configuration
    pays = "SN"
    annee_debut = 2010
    annee_fin = 2023
    
    print(f"Analyse économique du Sénégal ({annee_debut}-{annee_fin})")
    print("=" * 50)
    
    # 1. Récupération des données
    print("\n1. Récupération des données...")
    exports = get_export(pays, annee_debut, annee_fin)
    imports = get_import(pays, annee_debut, annee_fin)
    pib = get_pib(pays, annee_debut, annee_fin)
    
    if exports.empty or imports.empty or pib.empty:
        print("Erreur: Impossible de récupérer les données")
        return
    
    # 2. Fusion des données
    print("2. Traitement des données...")
    df = pd.merge(exports, imports, on=['code_pays', 'nom_pays', 'annee'])
    df = pd.merge(df, pib, on=['code_pays', 'nom_pays', 'annee'])
    
    # 3. Calculs additionnels
    df['balance_commerciale'] = df['exportations_usd'] - df['importations_usd']
    df['ratio_export_import'] = df['exportations_usd'] / df['importations_usd']
    df['ratio_export_pib'] = (df['exportations_usd'] / df['pib_usd']) * 100
    df['ratio_import_pib'] = (df['importations_usd'] / df['pib_usd']) * 100
    df['croissance_pib'] = df['pib_usd'].pct_change() * 100
    
    # 4. Affichage des statistiques
    print("\n3. Statistiques clés:")
    print("-" * 50)
    
    # Dernière année disponible
    derniere_annee = df['annee'].max()
    donnees_recentes = df[df['annee'] == derniere_annee].iloc[0]
    
    print(f"Année: {int(derniere_annee)}")
    print(f"PIB: ${donnees_recentes['pib_usd']:,.0f}")
    print(f"Exportations: ${donnees_recentes['exportations_usd']:,.0f}")
    print(f"Importations: ${donnees_recentes['importations_usd']:,.0f}")
    print(f"Balance commerciale: ${donnees_recentes['balance_commerciale']:,.0f}")
    print(f"Ratio Export/Import: {donnees_recentes['ratio_export_import']:.2f}")
    print(f"Croissance PIB: {donnees_recentes['croissance_pib']:.1f}%")
    
    # Moyennes sur la période
    print(f"\nMoyennes {annee_debut}-{int(derniere_annee)}:")
    print(f"Croissance PIB moyenne: {df['croissance_pib'].mean():.1f}%")
    print(f"Balance commerciale moyenne: ${df['balance_commerciale'].mean():,.0f}")
    
    # 5. Sauvegarde des données
    print("\n4. Sauvegarde des données...")
    df.to_csv('donnees_economiques_senegal.csv', index=False)
    print("Données sauvegardées dans 'donnees_economiques_senegal.csv'")
    
    # 6. Visualisations
    print("\n5. Création des graphiques...")
    create_visualizations(df)
    
    print("\nAnalyse terminée!")


def create_visualizations(df):
    """Crée des visualisations des données économiques"""
    
    # Configuration du style
    plt.style.use('seaborn-v0_8-darkgrid')
    fig = plt.figure(figsize=(15, 10))
    
    # 1. PIB et croissance
    ax1 = plt.subplot(2, 2, 1)
    ax1_twin = ax1.twinx()
    
    ax1.bar(df['annee'], df['pib_usd']/1e9, alpha=0.7, color='skyblue', label='PIB')
    ax1_twin.plot(df['annee'], df['croissance_pib'], color='red', marker='o', label='Croissance')
    
    ax1.set_xlabel('Année')
    ax1.set_ylabel('PIB (Milliards USD)', color='blue')
    ax1_twin.set_ylabel('Croissance (%)', color='red')
    ax1.set_title('PIB et Croissance du Sénégal')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1_twin.tick_params(axis='y', labelcolor='red')
    
    # 2. Commerce extérieur
    ax2 = plt.subplot(2, 2, 2)
    ax2.plot(df['annee'], df['exportations_usd']/1e9, marker='o', label='Exportations', linewidth=2)
    ax2.plot(df['annee'], df['importations_usd']/1e9, marker='s', label='Importations', linewidth=2)
    ax2.fill_between(df['annee'], df['exportations_usd']/1e9, df['importations_usd']/1e9, 
                     alpha=0.3, label='Déficit commercial')
    
    ax2.set_xlabel('Année')
    ax2.set_ylabel('Milliards USD')
    ax2.set_title('Commerce Extérieur')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Balance commerciale
    ax3 = plt.subplot(2, 2, 3)
    colors = ['green' if x > 0 else 'red' for x in df['balance_commerciale']]
    ax3.bar(df['annee'], df['balance_commerciale']/1e9, color=colors, alpha=0.7)
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    ax3.set_xlabel('Année')
    ax3.set_ylabel('Milliards USD')
    ax3.set_title('Balance Commerciale')
    ax3.grid(True, alpha=0.3)
    
    # 4. Ratios économiques
    ax4 = plt.subplot(2, 2, 4)
    ax4.plot(df['annee'], df['ratio_export_pib'], marker='o', label='Exports/PIB', linewidth=2)
    ax4.plot(df['annee'], df['ratio_import_pib'], marker='s', label='Imports/PIB', linewidth=2)
    
    ax4.set_xlabel('Année')
    ax4.set_ylabel('Pourcentage (%)')
    ax4.set_title('Ouverture Commerciale (% du PIB)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('analyse_economique_senegal.png', dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    main()
