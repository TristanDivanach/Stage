# -*- coding: utf-8 -*-
from setuphelpers import *

uninstallkey = []

def install():
    print("=== Desinstallation de l'agent GLPI ===")

    if service_installed('glpi-agent'):
        if service_is_running('glpi-agent'):
            print("Arret du service glpi-agent...")
            service_stop('glpi-agent')
        print("Desactivation du service glpi-agent...")
        run('sc config glpi-agent start= disabled', accept_returncodes=[0, 1060])
    else:
        print("Service glpi-agent absent")

    softs = installed_softwares('glpi agent')
    if not softs:
        print("Aucun logiciel 'GLPI Agent' trouve dans le registre")
    else:
        for soft in softs:
            print(f"Trouve : {soft['name']} (cle: {soft['key']})")
            key = soft['key']
            if key.startswith('{') and key.endswith('}'):
                cmd = f'msiexec /x "{key}" /quiet /norestart'
            else:
                cmd = soft.get('uninstall_string', '') + ' /quiet /norestart'
            print(f"Commande : {cmd}")
            run(cmd, accept_returncodes=[0, 1605, 3010])

    glpi_dir = makepath(programfiles, 'GLPI-Agent')
    if isdir(glpi_dir):
        print(f"Suppression du dossier residuel : {glpi_dir}")
        remove_tree(glpi_dir)
    else:
        print("Pas de dossier residuel")

    print("=== Termine ===")