# -*- coding: utf-8 -*-
from setuphelpers import *

uninstallkey = []

# === CONFIGURATION GLPI - A ADAPTER SI BESOIN ===
GLPI_SERVER = 'https://glpi.example.xxx/glpi/front/inventory.php'
# =================================================

def install():
    print("=== Installation de l'agent GLPI 1.17 ===")

    msi_file = makepath(basedir, 'GLPI-Agent-1.17-x64.msi')
    if not isfile(msi_file):
        error(f"MSI introuvable : {msi_file}")

    properties = {
        'SERVER': GLPI_SERVER,
        'RUNNOW': '1',
        'EXECMODE': '0',
        'INSTALLTASKS': 'Inventory,Collect,ESX,InstallRemove,WakeOnLan,Deploy',
        'ADD_FIREWALL_EXCEPTION': '1',
    }
    

    print(f"Installation depuis : {msi_file}")
    for k, v in properties.items():
        print(f"  {k} = {v}")

    install_msi_if_needed(
        msi_file,
        min_version='1.17',
        properties=properties,
        remove_old_version=True,
    )

    # S'assurer que le service est demarre
    if service_installed('glpi-agent'):
        if not service_is_running('glpi-agent'):
            print("Demarrage du service glpi-agent...")
            service_start('glpi-agent')
        else:
            print("Service glpi-agent deja en cours d'execution")

    print("=== Termine ===")
