# -*- coding: utf-8 -*-
from waptkeys import *
from setuphelpers import *

def install():
    # 1. Arrêter le service s'il tourne pour libérer les fichiers
    if service_is_running('glpi-agent'):
        print("Arrêt du service glpi-agent...")
        service_stop('glpi-agent')
    if service_is_running('FusionInventory-Agent'):
        print("Arrêt du service FusionInventory...")
        service_stop('FusionInventory-Agent')

    # 2. Chercher et désinstaller proprement toutes les occurrences MSI/EXE de GLPI Agent
    # install_string_contents renvoie les informations de désinstallation trouvées dans le registre
    for uninstall in uninstall_keys_from_registry('GLPI Agent'):
        print(f"Désinstallation trouvée : {uninstall['name']}")
        # Lance la commande de désinstallation d'origine (souvent msiexec /x) avec les arguments silencieux
        run(uninstall_cmd(uninstall['key']) + ' /quiet /norestart')

    # Prise en compte de l'ancien nom de l'agent si présent
    for uninstall in uninstall_keys_from_registry('FusionInventory Agent'):
        print(f"Désinstallation trouvée : {uninstall['name']}")
        run(uninstall_cmd(uninstall['key']) + ' /quiet /norestart')

    # 3. Nettoyage des résidus de fichiers physiques si l'installeur a laissé des miettes
    glpi_dir = makepath(programfiles, 'GLPI-Agent')
    if isdir(glpi_dir):
        print(f"Suppression du dossier résiduel : {glpi_dir}")
        remove_tree(glpi_dir)
        
    fusion_dir = makepath(programfiles, 'FusionInventory-Agent')
    if isdir(fusion_dir):
        print(f"Suppression du dossier résiduel : {fusion_dir}")
        remove_tree(fusion_dir)