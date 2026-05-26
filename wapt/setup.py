from waptkeys import *
from setuphelpers import *

def install():
    if service_is_running('glpi-agent'):
        print("Arrêt du service glpi-agent...")
        service_stop('glpi-agent')
    if service_is_running('FusionInventory-Agent'):
        print("Arrêt du service FusionInventory...")
        service_stop('FusionInventory-Agent')


    for uninstall in uninstall_keys_from_registry('GLPI Agent'):
        print(f"Désinstallation trouvée : {uninstall['name']}")
        run(uninstall_cmd(uninstall['key']) + ' /quiet /norestart')



    glpi_dir = makepath(programfiles, 'GLPI-Agent')
    if isdir(glpi_dir):
        print(f"Suppression du dossier résiduel : {glpi_dir}")
        remove_tree(glpi_dir)
        
    fusion_dir = makepath(programfiles, 'FusionInventory-Agent')
    if isdir(fusion_dir):
        print(f"Suppression du dossier résiduel : {fusion_dir}")
        remove_tree(fusion_dir)
