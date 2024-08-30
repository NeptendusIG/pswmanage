#####################################
#   Password Manager - Date         #
#####################################
# NOTES :
"""
"""

# -- IMPORTS --
import os, sys
if __name__ == '__main__':
    # Ajouter accès aux modules du projet
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Modules
import tkinter as tk
import ttkbootstrap as ttk
import pickle, sys, logging, hashlib
# Local
from utilitaire.utility import GUI, File, Settings
from function_dir.functions import ask_mdp_on_open, decrypt, load_encrypt_file, check_password, save_accounts_lib, encrypt, \
    update_search_list
from function_dir.manage_settings import add_widget_to_access_settings
# Classes
from class_dir.account import AccountLib

# Paramètres
logger = Settings.setup_logging("debugging")
logger.info("Lancement du programme.")

# Classes
# -- VARIABLES INITIALES / GLOBALES --
default_settings = {
    "source_location": "data/mdp.bytes",
    "historic_locations": [],
    "key_extensions": 0
}



# -- FONCTIONS DÉFINIES --
def ajouter_mdp(library):
    logger.info("OP-Add account: START")
    result = library.new_account()
    if result is False:
        logger.info("OP-Add account: CANCELLED\n")
    else:
        logger.info("OP-Add account: ADDED\n")


def chercher_mdp(library):
    logger.info("OP-Research: START")
    search_wind = GUI.set_basic_window("Recherche", themename='minty', size="600x200")
    tk.Label(search_wind, text="Rechercher :").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    champ = ttk.Entry(search_wind)
    champ.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    champ.bind("<Return>", lambda x: update_search_list(x, search_wind, library))
    search_wind.mainloop()


def memorisation_mdp(library):
    logger.info("OP-Memorisation: START")
    library.learn()


def fenetre_controle_parametres(library):
    """Changer localisation, mot de passe, force de chiffrement, backup, choose library"""
    logger.info("OP-Settings: START")
    settings_window = GUI.set_basic_window("Settings", themename='minty')
    add_widget_to_access_settings(settings_window, library)
    settings_window.mainloop()




# -- VARIABLES INITIALES/GLOBALES --
functions_dct = {
    'Ajouter': lambda: ajouter_mdp(accounts),
    'Chercher': lambda: chercher_mdp(accounts),
    'Apprendre': lambda: memorisation_mdp(accounts),
    'Paramètres': lambda: fenetre_controle_parametres(accounts)
}


# -- FONCTIONS MAÎTRES --
def charger_mdp():  # -> AccountLib
    logger.info("\nOP-Recuperation Data : START")
    window = GUI.set_basic_window("Entrez le mot de passe", size="300x150")
    password = ask_mdp_on_open(window)
    encrypt_bytes = load_encrypt_file()  # File path from settings
    return decrypt(encrypt_bytes, password)


def afficher_fenetre_boutons():
    logger.info("\nOP-Command Window: START")
    root_window = GUI.set_basic_window("Password Manager", themename='minty', size="400x200")
    GUI.set_cmd_buttons(root_window, functions_dct)  # GLOBAL functions_dct
    logger.info("OP-Command Window: initialized")
    root_window.mainloop()


def verrouiller_mdp(accounts):
    logger.info("\nOP-Verrouillage : START")
    password = GUI.ask_entry(can_cancel=False)
    if check_password(accounts, password):
        logger.info("OP-Verrouillage : password OK")
        save_accounts_lib(accounts, password, update_backups=True)
        logger.info("OP-Verrouillage : data SAVED")
        del accounts, password
        return True
    logger.info("OP-Verrouillage : WRONG password\n")
    return


# -- PROGRAMME --
if __name__ == '__main__':
    # - Variables -
    # - Environnement -
    File.create_file('main_settings.json', default_content=default_settings)
    # - Programme -
    while True:
        accounts = charger_mdp()
        if accounts:
            logger.info("\nRécupération Data : Data successfully DESERIALIZED")
            logger.info(f"\nOP-Récupération Data : Library OPENED \n({accounts}) ")
            break
        logger.info("OP-Récupération Data : WRONG key password")

    # - Variables update -
    #functions_dct = {
    #    'Ajouter': lambda: ajouter_mdp(accounts),
    #    'Chercher': lambda: chercher_mdp(accounts),
    #    'Apprendre': lambda: memorisation_mdp(accounts),
    #    'Paramètres': acces_parametres
    #}

    # afficher_fenêtre_boutons
    afficher_fenetre_boutons()
    # ... Attendre fermeture de la fenêtre
    logger.debug("--- (3) Verrouillage ---")
    while not verrouiller_mdp(accounts):
        continue
