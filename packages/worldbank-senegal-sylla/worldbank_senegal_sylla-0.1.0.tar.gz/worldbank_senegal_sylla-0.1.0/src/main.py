
from src.worldbank import get_export, get_import, get_pib

def main():
    print("=== Exemple d'utilisation WorldBank Sénégal ===\n")
    
    # 1. Exportations du Sénégal
    print("1. Exportations du Sénégal (2020-2023)")
    exports = get_export("SN", "2020", "2023")
    print(f"Nombre de lignes: {len(exports)}")
    if not exports.empty:
        print(exports.head())
        print(f"Dernière valeur: {exports.iloc[-1]['valeur']:.0f} USD\n")
    
    # 2. Importations du Sénégal
    print("2. Importations du Sénégal (2020-2023)")
    imports = get_import("SN", "2020", "2023")
    print(f"Nombre de lignes: {len(imports)}")
    if not imports.empty:
        print(imports.head())
        print(f"Dernière valeur: {imports.iloc[-1]['valeur']:.0f} USD\n")
    
    # 3. PIB de plusieurs pays
    print("3. PIB Sénégal vs France (2020-2023)")
    pib_data = get_pib(["SN", "FR"], "2020", "2023")
    print(f"Nombre de lignes: {len(pib_data)}")
    if not pib_data.empty:
        print(pib_data.head())
        
        # Comparaison par pays
        for pays in ["SN", "FR"]:
            pays_data = pib_data[pib_data["code_pays"] == pays]
            if not pays_data.empty:
                derniere_valeur = pays_data.iloc[-1]["valeur"]
                print(f"PIB {pays} (dernière année): {derniere_valeur:.0f} USD")

if __name__ == "__main__":
    main() 
