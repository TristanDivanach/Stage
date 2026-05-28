# -*- coding: utf-8 -*-
from setuphelpers import *
import glob

# Paramètre de votre serveur GLPI
# À MODIFIER avec votre URL (ex: "https://glpi.mondomaine.local/front/inventory.php")
GLPI_SERVER_URL = "http://glpi.technature.bzh/"

def install():
    print("Début de l'installation ou mise à jour du GLPI Agent...")
    
    # Récupération automatique du nom du fichier MSI présent dans le paquet
    msi_filename = glob.glob('GLPI-Agent-*.msi')[0]
    
    # Propriétés spécifiques au MSI de l'agent GLPI
    msi_properties = {
        'SERVER': GLPI_SERVER_URL,
        'RUNNOW': '1',                # Lance un inventaire immédiatement après l'installation
        'EXECMODE': '1',              # Installe l'agent en tant que service Windows
        'ADD_FIREWALL_EXCEPTION': '1' # Autorise l'agent dans le pare-feu Windows
        # Décommentez la ligne ci-dessous si vous utilisez de l'HTTPS sans certificat valide (non recommandé en prod)
        # 'NO_SSL_CHECK': '1' 
    }
    
    # Installation silencieuse avec les paramètres définis
    # Le timeout est fixé à 600s car le premier inventaire peut allonger le temps d'exécution
    install_msi_if_needed(msi_filename,
                          properties=msi_properties,
                          timeout=600)
    
    print("Installation terminée avec succès.")

#def uninstall():
    #print("Début de la désinstallation du GLPI Agent...")
    
    # WAPT gère souvent l'uninsall des MSI automatiquement. 
    # Cependant, forcer la désinstallation via la clé de registre garantit un retrait propre.
    #for soft in installed_softwares('GLPI Agent'):
        #print(f"Désinstallation de {soft['name']}...")
        #run(uninstall_cmd(soft['key']))
        
    # Le désinstalleur MSI du GLPI Agent laisse souvent des traces (logs, configs locales).
    # Nous nettoyons le dossier d'installation de force pour éviter tout conflit futur.
    #agent_dir = makepath(programfiles, 'GLPI-Agent')
    #if isdir(agent_dir):
        #print("Nettoyage du dossier résiduel...")
        #remove_tree(agent_dir)
        
    #print("Désinstallation et nettoyage terminés.")


