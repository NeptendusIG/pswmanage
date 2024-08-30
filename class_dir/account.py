########################
#
#
########################
from hashlib import sha256
from utilitaire.utility import GUI, File
import logging, pyperclip, datetime
import tkinter as tk
import ttkbootstrap as ttk  # remplace: from tkinter import ttk
from typing import Union

logger = logging.getLogger('debugging')


class AccountLib:

    def __init__(self, owner):
        logger.info(f'Account Library initialized for {owner}')
        self.owner = owner
        psw = GUI.ask_entry(title="Set master password", size="300x130")
        self.password_hash = sha256(psw.encode()).digest()
        logger.info(f"password initialised")
        self.length = 0
        self.account_totset = set()
        self.account_by_url = {}
        self.account_by_username = {}
        self.account_by_type = {}
        self.account_by_mail = {}
        self.account_by_keywords = {}
        self.account_by_id = {}
        logger.info(f'Account created')

    def __str__(self):
        sites = '\n'.join([f'{url} : {self.account_by_url[url]}' for url in self.account_by_url])
        return f'Owner: {self.owner}. Accounts: {self.length}\n\n{sites}'

    # def new_account(self, **kwargs):
    #    """The account must be created with a username, a password and an url."""
    #    account = AccountLib.Account(**kwargs, account_proper_lib=self)
    #    self.add_account(account)
    #    return account

    def new_account(self):
        """The account must be created with a username, a password and an url."""
        account = AccountLib.Account(account_proper_lib=self)
        is_validated = account.initialisation_interface()
        if is_validated:
            self.add_account(account)
            return account
        return False

    def add_account(self, account):
        self.length += 1
        self.account_by_url.setdefault(account.url, set()).add(account)
        self.account_by_username.setdefault(account.username, set()).add(account)
        self.account_by_type.setdefault(account.type, set()).add(account)
        self.account_by_mail.setdefault(account.email, set()).add(account)
        self.account_totset.add(account)
        for word in account._key_words:
            self.account_by_keywords.setdefault(word, set()).add(account)

    def remove_account(self, account):
        self.length -= 1
        self.account_by_url[account.url].remove(account)
        self.account_by_username[account.username].remove(account)
        self.account_by_type[account.type].remove(account)
        self.account_by_mail[account.email].remove(account)

    def refresh_struct(self):
        """Remake dictionaries for every account"""
        pass

    def update_account_keywords(self, account: 'AccountLib.Account'):
        for word in account._key_words:
            self.account_by_keywords.setdefault(word, set()).add(account)
        logger.info(f'Account keywords updated : {account._key_words}')

    def find_accounts_from_url(self, url):
        ensemble = self.account_by_url.get(url, set())
        return ensemble

    def find_accounts_from_keywords(self, words: Union[set, list]) -> set:
        ensemble = set()
        for word in words:
            ensemble.update(self.account_by_url.get(word, set()))
        return ensemble

    class Account:

        def __init__(self,
                     username="", password="", url="", email=None, type=None, description=None, phone=None,
                     account_proper_lib=None):
            self.username = username
            self.password = password
            self.url = url
            self.email = email
            self.type = type
            self.description = description
            self.phone = phone
            self._key_words = self.get_key_words()
            # self._account_proper_lib = account_proper_lib
            logger.info('Account initialized')

        def __str__(self):
            return f'{self.url} -> {self.username}, {self.email})'

        def data(self):
            return f'{self.email} - {self.type} - {self.phone}  \n{self.description}'  # - {self._id}

        def get_key_words(self):
            group = set(self.username.split())
            if isinstance(self.description, str):
                logger.debug(f'in description : {self.description}')
                group.update({word for word in self.description.split() if len(word) > 3})
            else:
                logger.debug(f'NOT in description : {self.description}')
            group.add(max(self.url.split("/"), key=len))
            group.add(self.type)
            logger.info(f'Key words created : {group}')
            return group

        def individual_interface(self):
            """Interface pour accéder aux infos d'un compte (copier/modifier)"""
            # Création de la fenêtre
            window = GUI.set_basic_window("Account Information")
            # Attributs à afficher / accessibles
            attributs = ['url', 'username', 'password', 'email', 'type', 'description', 'phone']
            attributs_with_button = ['url', 'username', 'password', 'email']
            # Initialisation des champs
            interact_var = {attribut: tk.StringVar() for attribut in attributs}
            entries: dict[str, ttk.Entry] = {}
            # Pour chaque attribut -> ligne
            for row, attr in enumerate(attributs):
                # Nom du champ
                ttk.Label(window, text=attr.capitalize() + ":").grid(row=row, column=0, sticky="e")
                # Champ de saisie
                interact_var[attr].set(getattr(self, attr))  # Valeur par défaut /actuelle
                entries[attr] = ttk.Entry(window, textvariable=interact_var[attr])  # Champ de saisie
                entries[attr].grid(row=row, column=1)  # Positionnement
                entries[attr].bind('<Return>', lambda event, att=attr: setattr(self, att, entries[
                    att].get()))  # Validation par touche enter
                # Button si nécessaire
                if attr in attributs_with_button:
                    copy = lambda attribut=attr: self.copy_attr(attribut)
                    ttk.Button(window, text=f"Copy {attr}", command=copy).grid(row=row, column=2)
            # Lancement de la fenêtre
            window.mainloop()

        def copy_attr(self, attr):
            pyperclip.copy(getattr(self, attr))
            if attr != 'password':
                logger.info(f'Copy {attr} ({getattr(self, attr)})')
            else:
                logger.info(f'Copy {attr} (*******)')

        def past_to_attr(self, attr):
            setattr(self, attr, pyperclip.paste())
            if attr != 'password':
                logger.info(f'Paste {attr} ({getattr(self, attr)})')
            else:
                logger.info(f'Paste {attr} (*******)')

        def initialisation_interface(self):
            """Interface pour accéder aux infos d'un compte (copier/modifier)"""
            # 1 - Initialisation de la fenêtre, des noms et variables de champs, du stockage des champs (dict)
            window = GUI.set_basic_window("Account Initialization", size="500x250")
            attributs = ['url', 'username', 'password', 'email', 'type', 'description', 'phone']
            attributs_with_button = ['url', 'username', 'password', 'email']
            fields_var = {attribut: tk.StringVar(window, value=getattr(self, attribut)) for attribut in attributs}
            entries: dict[str, ttk.Entry] = {}
            # 2 - Fonctions pour les boutons
            is_validate = False

            def past_to_field(attribut):
                logger.info(f'Pasting to {attribut} <- {pyperclip.paste()}')
                fields_var[attribut].set(pyperclip.paste())

            def quit_window():
                window.quit()
                window.destroy()

            def validate():  # Set True and quit
                nonlocal is_validate
                is_validate = True
                quit_window()

            # 3 - Pour chaque attribut -> (|nom| |champs| |<Button>|)
            for row, attr in enumerate(attributs):
                # Nom
                ttk.Label(window, text=attr.capitalize() + ":").grid(row=row, column=0, sticky="e")
                # Champ
                entries[attr] = ttk.Entry(window, textvariable=fields_var[attr])  # Champ de saisie
                entries[attr].grid(row=row, column=1)  # Positionnement
                # Button
                if attr in attributs_with_button:
                    paste = lambda attribut=attr: past_to_field(attribut)
                    ttk.Button(window, text=f"Paste to {attr}", command=paste).grid(row=row, column=2)
            # 4 - Boutons Valider/Annuler
            ttk.Button(window, text="Validate", command=validate).grid(row=row + 1,
                                                                       column=1)  # row in for loop is accessible after end of loop
            ttk.Button(window, text="Cancel", command=quit_window).grid(row=row + 1, column=0)
            # 5 - Lancement de la fenêtre
            window.mainloop()
            # 6 - Mettre à jour les attributs
            if is_validate:
                for attr, var in fields_var.items():
                    setattr(self, attr, var.get())
                logger.info(f'Account initialized: {self}')
                return True
            else:
                logger.info(f'Account initialization cancelled')
                return False
