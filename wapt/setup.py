from waptkeys import *
from setuphelpers import *

def install():
    if service_is_running('glpi-agent'):
        print("Arrêt du service glpi-agent...")
        service_stop('glpi-agent')

    for uninstall in uninstall_keys_from_registry('GLPI Agent'):
        print(f"Désinstallation trouvée : {uninstall['name']}")
        run(uninstall_cmd(uninstall['key']) + ' /quiet /norestart')



    glpi_dir = makepath(programfiles, 'GLPI-Agent')
    if isdir(glpi_dir):
        print(f"Suppression du dossier résiduel : {glpi_dir}")
        remove_tree(glpi_dir)
