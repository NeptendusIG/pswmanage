# ----------------------------
#
# ----------------------------
"""
"""
# -- IMPORTS --
# Modules
from utilitaire.utility import File, Settings, GUI
from class_dir.account import AccountLib
from typing import Any, Optional
import pickle, hashlib, os, logging, sys, shutil, datetime
import tkinter as tk
import ttkbootstrap as ttk  # remplace: from tkinter import ttk


# Paramètres
logger = Settings.setup_logging("debugging")

# Classes


# -- FONCTIONS DÉFINIES --

# 1 - Fonctions de chiffrement/déchiffrement
def encrypt(data: Any, password: str) -> bytes:  # Traduit des dictionnaires dans ce cas
    # 1 - Convertir en bytes
    data_bytes = pickle.dumps(data)
    key = extend_the_key(hashlib.sha256(password.encode('utf-8')).digest())
    logger.info(f"Encryption: data serialized and key hashed \n({len(data_bytes)} bytes and key {key})")
    # 2 - Chiffrer les bytes : opération XOR
    encrypted_bytes = bytes(xor_encrypt_bytes(data_bytes, key))
    logger.info(f"Encryption: data encrypted)")
    # 3 - Effacer la mémoire
    del key, data_bytes
    return encrypted_bytes


def decrypt(crypted_bytes: bytes, password: str) -> Any:  # Des dictionnaires dans ce cas
    logger.info("Récup Data: Decryption")
    # 1 - Convertir clé en bytes (hashage)
    key = extend_the_key(hashlib.sha256(password.encode('utf-8')).digest())  # hashlib.sha256(password.encode('utf-8')).digest()
    # 2 - Déchiffrement : opération XOR
    data_bytes = bytes(xor_encrypt_bytes(crypted_bytes, key))
    logger.info("Récup Data: XOR applied")
    # 3 - Désérialisation (traduire les bytes en objet)
    try:
        data = pickle.loads(data_bytes)
        logger.info("Récup Data: BYTES deserialized")
    except pickle.UnpicklingError:
        logger.error("Récup Data: PSW not valid")
        return None
    except UnicodeDecodeError:
        logger.error("Récup Data: PSW not valid")
        return None
    # 4 - Effacer la mémoire
    del key, data_bytes
    return data


def xor_encrypt_bytes(data: bytes, key: bytes) -> bytes:
    """encode bytes with XOR operation
    @pre : data to encode/decode (any length)
            key to encode/decode data (any length)
    @post : apply XOR on data with key (loop on key if necessary)"""
    if (overloop := len(data)/len(key)) > 10:
        logger.info(f'key overloop {overloop} times on data (bytes{len(data)} key {len(key)})\n')
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])


def extend_the_key(initial_hash: bytes, extend: Optional[int] = None) -> bytes:
    if extend is None:
        extend = File.JsonFile.get_value_jsondict('PasswordManager/main_settings.json', 'key_extensions')
    upper_hash = hashlib.sha256(initial_hash).digest()
    extended_key = initial_hash + (extend_the_key(upper_hash, extend - 1) if extend > 0 else b'')
    logger.info(f"{extended_key = }, {extend=}")
    return extended_key


def check_password(accounts_lib: AccountLib, psw_input: str) -> bool:
    key_ext = File.JsonFile.get_value_jsondict('PasswordManager/main_settings.json', 'key_extensions')
    hashed_psw = extend_the_key(hashlib.sha256(psw_input.encode()).digest(), key_ext)
    logger.info(f"Vérification: {hashed_psw} ({key_ext} ext) vs {accounts_lib.password_hash}")
    return hashed_psw == accounts_lib.password_hash


# TODO: Potentiellement à déplacer dans un module interfaces/messageBOX
# TODO: Ajouter "Choisir" pour choisir un fichier chiffré existant
# TODO: Ajouter "Créer" même si un fichier existe déjà
# 2 - Fonctions d'interface utilisateur
def ask_mdp_on_open(window) -> str:
    """Demande mot de passe maitre.
    Si ANNULER : Stop le programme
    Si FileNotFound: Bouton Nouveau : Créer un fichier"""
    source_path = File.JsonFile.get_value_jsondict('PasswordManager/main_settings.json', 'source_location', handle_keyERROR=True, default_val=False)
    # Variable pour stocker le mot de passe
    password = tk.StringVar()

    # Fonctions pour les boutons
    def on_validate(args=None):
        logger.info("Récup: entry SEND")
        password.set(entry.get())
        if os.path.isfile(source_path):
            logger.debug("Récup: entry CAPTURED")
            window.quit()
            window.withdraw()
        else:
            logger.debug("Récup: FileNotFound")

    # Libellé, champ de saisie
    label = ttk.Label(window, text="Entrez le mot de passe :")
    label.pack(pady=10)
    entry = ttk.Entry(window, show="*", textvariable=password)
    entry.pack(pady=5)
    entry.bind('<Return>', on_validate)
    # Frame pour contenir les BOUTONS
    button_frame = ttk.Frame(window)
    button_frame.pack(padx=10, pady=10, fill=tk.X)
    # Boutons
    button_cancel = ttk.Button(button_frame, text="Annuler", command=lambda: sys.exit("Programme annulé"))
    button_cancel.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)
    button_validate = ttk.Button(button_frame, text="Valider", command=on_validate)
    button_validate.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)
    # Bouton de création d'une librairie
    if not os.path.isfile(source_path):
        button_new = ttk.Button(button_frame, text="Créer", command=creation_new_library)
        button_new.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)

    # Lancement de la fenêtre
    window.mainloop()
    return password.get()


def update_search_list(keywords_in_event, search_wind, library: AccountLib):
    logger.info("OP-Research: begin SORT")
    # 1 - Récupérer les accounts correspondants (potentiellement)
    keywords = keywords_in_event.widget.get().split()
    accounts = set()
    for word in keywords:
        accounts.update(library.find_accounts_from_keywords(word))
        logger.info(f"Research: update: {accounts}")
    if not accounts:
        accounts = library.account_totset
    # 2 - Afficher les comptes dans la fenêtre
    GUI.parse_buttons_on_object(accounts, {"Voir détails": lambda x: x.individual_interface()}, window=search_wind, first_row=1)


# 3 - Fonctions sur fichiers (Création, Lecture, Écriture)
def creation_new_library() -> None:
    """Utilisé pour proposer la création d'une nouvelle librairie si le fichier source n'est pas trouvé.
    - Crée un objet AccountLib (avec un master password)
    - Crée un fichier source (demande un emplacement)
    - Met à jour les paramètres (source et historique)
    """
    logger.info("New library: START")
    # 1 Obtenir infos nécessaires
    source_path = GUI.ask_dir()
    if source_path is None:
        logger.info("New library: CANCELED")
        return
    source_path = os.path.join(source_path, "passwors_library.pickle")
    new_lib = AccountLib(owner="Gaetan L")
    logger.info("New library: AccountLib CREATED")
    # 2 Créer fichier crypter
    encrypted = encrypt(new_lib, GUI.ask_entry("Confirmez le mot de passe", can_cancel=True))
    logger.info("New library: data ENCRYPTED")
    with open(source_path, 'wb') as file:
        file.write(encrypted)
        logger.info("New library: File CREATED")
    # 3 Mettre paramètres à jour
    historic: list = File.JsonFile.get_value_jsondict("PasswordManager/main_settings.json", "historic_locations")
    historic.append(source_path)
    File.JsonFile.set_value_jsondict("PasswordManager/main_settings.json", "historic_locations", historic)
    File.JsonFile.set_value_jsondict("PasswordManager/PasswordManager/main_settings.json", "source_location", source_path)
    logger.info("New library: settings UPDATED (source and historic)")

    logger.info("New library: ACTIVATED (complete)")
    return


def load_encrypt_file() -> Optional[bytes]:
    filepath = File.JsonFile.get_value_jsondict('PasswordManager/main_settings.json', 'source_location')
    logger.info(f"Récup Data: File ({filepath})")
    if os.path.exists(filepath):
        return open(filepath, 'rb').read()
    logger.error(f"Récup Data: FILE NOT FOUND")


def save_accounts_lib(accounts_lib: AccountLib, psw: str, update_backups=False) -> None:
    encrypted_bytes = encrypt(accounts_lib, psw)
    source_path = File.JsonFile.get_value_jsondict('PasswordManager/main_settings.json', 'source_location')
    with open(source_path, 'wb') as file:
        file.write(encrypted_bytes)
    if update_backups:
        save_backups(encrypted_bytes)
    return


def save_backups(encrypted_bytes: bytes):
    """Sauvegarde des données (bytes) dans les emplacements de sauvegarde
    - Seulement si la dernière sauvegarde a plus de 7 jours
    - Crée un fichier .pickle avec la date actuelle (Y_M_D) dans un dossier 'backups'
    """
    backup_paths_dir = File.JsonFile.get_value_jsondict('PasswordManager/main_settings.json', 'backup_locations')
    logger.info(f"Backup: START ({len(encrypted_bytes)} bytes for {len(backup_paths_dir)} locations)")
    for backups_dir in backup_paths_dir:
        logger.info(f"Backup: {backups_dir}")
        # 1 - Vérification de la date de la dernière sauvegarde
        files = os.listdir(backups_dir)
        dates = [os.path.getctime(os.path.join(backups_dir, f)) for f in files]
        last_dtt = max(dates, default=None)
        # last_dtt = max([os.path.getctime(os.path.join(backups_dir, f)) for f in os.listdir(backups_dir)], default=None)
        logger.debug(f"\tlast backup: {last_dtt}")
        logger.info(f"\tBackup: {len(files)} EXISTING previous saved")
        # 2 - Création du fichier de sauvegarde
        today_date = datetime.datetime.now().strftime("%Y_%m_%d")
        file_path_name = os.path.join(backups_dir, today_date+".pickle")
        logger.debug(f'\tBackup: DATE {today_date} FILENAME {today_date+".pickle"}')
        with open(file_path_name, 'wb') as file:
            file.write(encrypted_bytes)
            logger.info(f"\tBackup: File SAVED ({file_path_name})")
    else:
        logger.info(f"Backup: END ({len(backup_paths_dir)} locations tested)")
        return


def add_a_backup():
    """Ajoute un emplacement de sauvegarde"""
    dir_path = GUI.ask_dir()
    new_dir_for_backups = os.path.join(dir_path, "backups")
    if not os.path.exists(new_dir_for_backups):
        os.mkdir(new_dir_for_backups)
    backup_paths = File.JsonFile.get_value_jsondict('PasswordManager/main_settings.json', 'backup_locations')
    backup_paths.append(new_dir_for_backups)
    File.JsonFile.set_value_jsondict('PasswordManager/main_settings.json', 'backup_locations', backup_paths)
    logger.info("Backup: ADDED")
    return


# 4 - Fonctions d'accès aux paramètres










# -- SANDBOX --
if __name__ == '__main__':
    # - Variables -

    # - Programme -
    pass
