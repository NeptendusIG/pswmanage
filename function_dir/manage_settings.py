# ----------------------------
#   Module local de fonctions
#        <PROJET NOM>
# DATE:
# VERSION: 1.0
# ----------------------------
"""  -- Structures des fonctions disponibles --
Classement 1
 - function_name(arg1)
Classement 2
- f2(arg1)
"""


# Modules bases
import os, logging, sys, shutil, time, datetime, pickle, hashlib, subprocess
# Modules renommés
import tkinter as tk
import ttkbootstrap as ttk
import numpy as np
# Importations spécifiques
from typing import Any, Optional
# Modules locaux (et classes)
from utilitaire.utility import File, Settings, GUI  # Classes de fonctions
from class_dir.account import AccountLib
from function_dir.functions import save_accounts_lib, extend_the_key, check_password

# Paramètres
logger = Settings.setup_logging("debugging")


# -- FONCTIONS DÉFINIES --
# Fonction principale
def add_widget_to_access_settings(window: tk.Tk, library=None) -> None:
    """Changer localisation, mot de passe, force de chiffrement, backup"""
    # 1 - Fonctions de modification avec paramètres intégrés (global)
    def move_file():
        change_location(window)

    def show_historic():
        test_historic(window)

    def remove_a_backup():
        show_backup_list(window)

    def change_password():
        change_master_password(library)

    def upgrade_sec():
        change_key_extensions(library, 1)

    def downgrade_sec():
        change_key_extensions(library, -1)
    # 2 - CHAQUE PARAMÈTRE : un nom <A> / un état (valeur) <B> / des actions possibles <C>
    parameters = [
        ("source_location", File.JsonFile.get_value_jsondict('main_settings.json', 'source_location'),
         [move_file]),
        ("historic_locations", "\n".join(File.JsonFile.get_value_jsondict('main_settings.json', 'historic_locations', handle_keyERROR=False)),
         [show_historic]),
        ("backup_locations", "\n".join(File.JsonFile.get_value_jsondict('main_settings.json', 'backup_locations')),
         [add_a_backup, remove_a_backup]),
        ("security", eval_security(), [change_password, upgrade_sec, downgrade_sec])]
    logger.info("OP:Settings: Parameters and functionalities LOADED")
    # 3 - Création du tableau listant les paramètres
    main_frame = ttk.Frame(window)
    for i, name_info_func in zip(range(0, 2 * len(parameters), 2), parameters):  # (0, param1), (2, par2), (4, par3)
        # A - Nom du paramètre, en grand à gauche
        label = ttk.Label(main_frame, text=name_info_func[0].replace("_", " ").capitalize() + ":", font='Calibri 18 bold')
        label.grid(column=0, row=i, padx=5, pady=10, sticky="w")
        # B - État du paramètre
        info = ttk.Label(main_frame, text=name_info_func[1])
        info.grid(column=1, row=i, padx=5)
        # C - Modifications possibles
        for j, action in enumerate(name_info_func[2], 2):
            button = ttk.Button(main_frame, text=action.__name__.replace("_", " "),
                                command=action)  # utilise le nom de la fonction
            button.grid(column=j, row=i, padx=5, sticky="ew")
        # 4 - Séparateur de rangée
        separator1 = tk.Frame(main_frame, height=2, bd=1, relief=tk.SUNKEN)
        separator1.grid(row=i + 1, column=0, columnspan=j + 1, sticky="ew")  # j pour étendre sur les boutons
    main_frame.pack()
    logger.info(f"Settings: Widgets ADDED (start window)")


# 2 - Fonctions de modification majeures
def change_location(window):
    """Déplace le fichier source et sauvegarde le nouvel emplacement"""
    # 1 - Demander le nouvel emplacement
    new_dir_path = GUI.ask_dir(root=window)
    if new_dir_path is None:
        logger.info("Change location: CANCELLED")
        return False
    new_file_path = os.path.join(new_dir_path, "passwors_library.pickle")
    # 2 - Déplacer le fichier
    old_path = File.JsonFile.get_value_jsondict("main_settings.json", "source_location")
    if not os.path.exists(old_path):
        logger.error("Change location: Original FileNotFound")
        return False
    try:
        shutil.move(old_path, new_dir_path)
        logger.info(f"Settings:ChangeLocation: file RELOCATED")
        logger.debug(f"Settings:ChangeLocation: {old_path} moved to {new_dir_path}")
    except Exception as e:
        logger.error(f"Settings:ChangeLocation: CANCELLED \n\tERROR{e}")
        return
    # 3 - Mettre à jour les paramètres
    historic: list = File.JsonFile.get_value_jsondict("main_settings.json", "historic_locations")
    historic.append(new_file_path)
    File.JsonFile.set_value_jsondict("main_settings.json", "historic_locations", historic)
    File.JsonFile.set_value_jsondict("main_settings.json", "source_location", new_file_path)
    logger.info("Settings:ChangeLocation: settings UPDATED")
    return True


def change_master_password(lib):
    """Changer le mot de passe de la librairie"""
    logger.info("Settings:ChangePassword: START")
    # 1 - Demander ancien mot de passe
    old_psw = GUI.ask_entry("Entrez l'ancien mot de passe", can_cancel=True)
    if not check_password(lib, old_psw):
        logger.error("Settings:ChangePassword: WRONG")
        return False
    # 2 - Demander nouveau mot de passe
    new_psw = GUI.ask_entry("Entrez le nouveau mot de passe", can_cancel=True)
    confirm = GUI.ask_entry("Confirmez le nouveau mot de passe", can_cancel=True)
    # 3 - Changer le mot de passe
    if new_psw != confirm:
        logger.error("Settings:ChangePassword: NOT MATCH")
        return False
    lib.password_hash = hashlib.sha256(new_psw.encode()).digest()
    logger.info("Settings:ChangePassword: CHANGED")
    save_accounts_lib(lib, new_psw)
    logger.info("Settings:ChangePassword: data RE-SAVED")
    return


# 3 - Fonctions de modification mineures
def change_key_extensions(lib: AccountLib, new_extensions: int):
    """Changer le nombre de fois que la clé est étendue"""
    logger.info("Settings:ChangeKeyExtensions: START")
    # 1 - Demander ancien mot de passe
    password = GUI.ask_entry("Entrez le mot de passe", can_cancel=True)
    if not check_password(lib, password):
        logger.error("Settings:ChangeKeyExtensions: WRONG access")
        return False
    # 2 - make new key and change it
    old_set = File.JsonFile.get_value_jsondict('main_settings.json', 'key_extensions')
    if new_extensions == 0:
        logger.error("Settings:ChangeKeyExtensions: NO CHANGE")
        return  # Does not re-write the data
    if old_set + new_extensions >= 0:
        lib.password_hash = extend_the_key(hashlib.sha256(password.encode('utf-8')).digest(), old_set + new_extensions)
        type_change = "UPGRADE" if new_extensions > 0 else "DOWNGRADE"
        logger.info(f"Settings:ChangeKeyExtensions: {type_change} ({new_extensions})")
    else:
        logger.error("Settings:ChangeKeyExtensions: négative LENGTH extension not allowed")
        return
    # 3 - Update the settings
    File.JsonFile.set_value_jsondict('main_settings.json', 'key_extensions', old_set + new_extensions)
    # 3 - Re-write the data with new key
    save_accounts_lib(lib, password)
    logger.info("Settings:ChangeKeyExtensions: data RE-SAVED")


def add_a_backup():
    """Ajoute un emplacement de sauvegarde"""
    dir_path = GUI.ask_dir()
    if not dir_path:
        logger.info("Settings:AddBackup: CANCELLED")
        return
    logger.info(f"Settings:AddBackup: SELECTED {dir_path}")
    new_backups_dir = os.path.join(dir_path, "backups")
    if not os.path.exists(new_backups_dir):
        os.mkdir(new_backups_dir)
        logger.debug("BackupDir: CREATED")
    backup_paths = File.JsonFile.get_value_jsondict('main_settings.json', 'backup_locations')
    backup_paths.append(new_backups_dir)
    File.JsonFile.set_value_jsondict('main_settings.json', 'backup_locations', backup_paths)
    logger.info(f"Settings:AddBackup: List UPDATED ({new_backups_dir})")
    return True


def show_backup_list(window):
    """Supprimer un emplacement de sauvegarde"""
    # 1 - récupération des données
    backup_paths = File.JsonFile.get_value_jsondict('main_settings.json', 'backup_locations')
    logger.info(f"Settings:RemoveBackup: START ({len(backup_paths)} locations)")
    if not backup_paths:
        logger.info("Settings:RemoveBackup: CANCELLED (no backup locations)")
        return
    # 2 - fonctions d'info et de modification
    def delete(index, rows_var: dict[int, tk.StringVar]):
        nonlocal backup_paths
        logger.info(f"Settings:RemoveBackup: TRY delete {index}")
        rows_var[index].set("deleted")
        backup_paths[index] = None
        new_list = [path for path in backup_paths if path]
        logger.info(f"Settings:RemoveBackup: list Updated {new_list}")
        File.JsonFile.set_value_jsondict('main_settings.json', 'backup_locations', new_list)
        logger.info(f"Settings:RemoveBackup: list SAVED")

    def get_weight(path):
        if os.path.exists(path):
            return f"weight= {os.path.getsize(path)}"
        return None

    def shorten_paths(*paths):
        common = os.path.commonpath(paths)
        relpath = os.path.relpath(paths[0], common)
        shorten_with_one = os.path.split(common)[1] + os.sep + relpath
        return shorten_with_one

    def open_dir(path):
        try:
            subprocess.run(["open", path])
            logger.debug(f"Settings:RemoveBackup: opened view {path}")
        except Exception as e:
            logger.debug(f"Settings:RemoveBackup: Failed to open ({e})")

    def is_access(path):
        if os.path.exists(path):
            return "FOUND"
        return "NOT FOUND"

    # 3 - présentation des données (widgets)
    param_frame = ttk.Frame(window, borderwidth=2, relief="sunken")  # GUI.last_active_window (avant)
    rows_path = {i: tk.StringVar(value=path) for i, path in enumerate(backup_paths)}
    before_path = "/"
    for i, path in enumerate(backup_paths[::-1]):
        # ttk.Label(param_frame, text=get_modif_date(path)+" <> ").grid(column=0, row=i, sticky="e")
        ttk.Label(param_frame, text=shorten_paths(path, before_path), textvariable=rows_path[i]).grid(column=0, row=i, sticky="w")
        ttk.Label(param_frame, text=is_access(path)).grid(column=1, row=i, sticky="w", padx=5)
        ttk.Label(param_frame, text=get_weight(path)).grid(column=2, row=i)
        before_path = path
        ttk.Button(param_frame, text="delete", command=lambda idx=i, rows=rows_path: delete(idx, rows)).grid(column=3, row=i, padx=5)
        ttk.Button(param_frame, text="open", command=lambda path=path: open_dir(path)).grid(column=4, row=i, padx=5)
    logger.info(f"Settings:RemoveBackup: Frame MADE")
    param_frame.pack(padx=10, pady=10)



# 4 - Fonctions d'analyse et d'information
def eval_security():
    """Give a score on ten comparing length of data and key, and the age of the password."""
    extensions = File.JsonFile.get_value_jsondict('main_settings.json', 'key_extensions') + 1
    weight_data = os.path.getsize(File.JsonFile.get_value_jsondict('main_settings.json', 'source_location'))
    rate_data_on_key = weight_data / (32 + extensions * 32)
    date = File.JsonFile.get_value_jsondict('main_settings.json', 'last_key_update')
    months_passed = (datetime.datetime.now() - datetime.datetime.strptime(date, "%Y-%m-%d")).days / 30
    score = 10 / ((rate_data_on_key/10+1) * (months_passed/3 + 1)) ** (0.5)
    return f"SCORE {score:.2}/10 (Key repeat {rate_data_on_key:.3}, password months {months_passed:.2})"


def test_historic(window):
    """Déplace le fichier source et sauvegarde le nouvel emplacement"""
    # 1 - fonctions de test
    def get_modif_date(path):
        if not os.path.exists(path):
            return ""
        dt_time = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        return dt_time.strftime("%Y-%m-%d")

    def is_access(path):
        if os.path.exists(path):
            return "available"
        return "not available"


    def get_weight(path):
        if os.path.exists(path):
            return f"weight= {os.path.getsize(path)}"
        return None

    def shorten_paths(*paths):
        common = os.path.commonpath(paths)
        relpath = os.path.relpath(paths[0], common)
        shorten_with_one = os.path.split(common)[1] + os.sep + relpath
        return shorten_with_one

    # 2 - récupération et présentation des données
    historic_list = File.JsonFile.get_value_jsondict("main_settings.json", "historic_locations")
    param_frame = ttk.Frame(window, borderwidth=2, relief="sunken")  # GUI.last_active_window
    before_path = "/"
    for i, old_path in enumerate(historic_list[::-1]):
        ttk.Label(param_frame, text=get_modif_date(old_path)+" <> ").grid(column=0, row=i, sticky="e")
        ttk.Label(param_frame, text=shorten_paths(old_path, before_path)).grid(column=1, row=i, sticky="e")
        ttk.Label(param_frame, text=is_access(old_path)).grid(column=2, row=i, sticky="w", padx=5)
        ttk.Label(param_frame, text=get_weight(old_path)).grid(column=3, row=i)
        before_path = old_path
    param_frame.pack(fill="both", padx=10, pady=10)  # Ajout dans la fenêtre de settings


# -- TESTS ET EXEMPLES --
if __name__ == '__main__':
    # Environnement
    test_logger = Settings.setup_logging("debugging")
    os.path.exists("main_settings.json")
    # Variables
    main_window = GUI.set_basic_window()
    settings_window = GUI.set_basic_window("Settings", themename='minty', size="400x200")
    # Programme
    add_widget_to_access_settings(settings_window)
    main_window.mainloop()

