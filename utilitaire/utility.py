#####################################
#   Module Utilitaire - dec/2024    #
#####################################
# NOTES :
"""
Fonctions utilitaire classées grâce aux classes
 -> Ce sont exclusivement des méhodes de classes
* ORGANISATION *
- InputUtil
- File
- Formatting
- GetData      -> Fonctions spécifiques à ce projet
"""
# Fonction à caractère générale
# Pour constituer un module utilitaire
import os.path, shutil, sys, math, subprocess, platform, json, logging.config, logging.handlers  # Basic
import smtplib, csv  # Specific
import tkinter as tk
from tkinter import Tk, filedialog
import ttkbootstrap as ttk  # remplace: from tkinter import ttk

logger = logging.getLogger("debugging")
#logger.setLevel(logging.INFO)


# ** Ajouts aux Built-In **
# TYPE : str

# ** settings **
class Settings:
    @classmethod
    def setup_logging_json(cls, path_logconfig="logconfig.json"):
        config_file = os.path.abspath(path_logconfig)
        with open(config_file) as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        return logging.getLogger("main")

    @classmethod
    def setup_logging(cls, logger_name="main"):
        try:
            sys.path.append("utilitaire")
            import log_config as log  # config: dct et Filtres
        except ModuleNotFoundError as e:
            print(f"ModuleNotFoundError: {e}")
            return logging.getLogger("main")
        try:
            logging.config.dictConfig(log.config_dct)
            return logging.getLogger(logger_name)
        except ValueError as e:
            if "file" in str(e):
                print(f"Verify logs directory existence ({e})")
                return
            print(f"ValueError: {e}")
        except Exception as e:
            print(f"Exception: {e}")


# str.isfloat = isfloat

class InputUtil:

    @classmethod
    def ask_int(cls, context, other=[]):
        """Gestion input
        @pre: Phrase posée étant le context
        @post: gère les erreurs

        Notes : obligé d'entrer un entier supp à 0 (pas rien)"""
        print(f"Veuillez saisir {context} ")
        while True:
            try:
                length = int(input(f"Entrez : "))  # {context}
                if length > 0 or length in other:
                    return length
            except TypeError:
                print("La saisie doit être un entier")
            except Exception as e:
                print(f"Erreur : {e}")

    @classmethod
    def ask_iterable(cls, other=[]):
        """Gestion input
        @pre: Phrase posée étant le context, type de donnée à entrer/fournir
        @post: gère les erreurs

        Notes : obligé d'entrer un entier supp à 0 (pas rien)"""
        type1 = list
        type2 = int
        print(f"Veuillez saisir des valeurs séparées par un espace")
        while True:
            try:
                length = type1(type2(dat) for dat in input(f"Entrez : ").split())  # {context}
                if isinstance(length, type1) or length in other:
                    return length
            except TypeError:
                print(f"La saisie doit être un {type}")
            except Exception as e:
                print(f"Erreur : {e}")

    @classmethod
    def commands(cls, cmd_input, dico, obj=None):
        """Traitement de commandes présentes dans dictionnaire
        @pre: command et dictionnaire
            dictionaire = {"cmd": (func, args-len, method/func, type, "context" or <ask_parameters>)}
            Si la longueur des arg ne correspond pas,
                soit type est donné, alors ask_input(type, context)
                soit type est None, alors exécute la func à <ask_parameters> (fonction fournie)
        @post: éxecution de la fonction associée dans le dictionnaire
            (return le return de la fonction)
        """
        parts = cmd_input.strip().split()
        parts = [Formatting.digitpart(part, True) for part in parts]
        cmd = parts[0]
        if cmd not in dico:
            return "cmd not found"
        if all([len(parts) < nbre_args for nbre_args in dico[cmd][1]]):
            if dico[cmd][3] is None:  # dico[cmd][3] (type de donnée)
                parts.append(dico[cmd][4]())
            elif dico[cmd][3] is int:
                parts.append(cls.ask_int(dico[cmd][4]))
        if dico[cmd][2] == "method":
            # get object (else error)
            parts.insert(1, obj)

        result = dico[cmd][0](*parts[1:])
        return result

    @classmethod
    def take_command_one_character(cls, cmd_dict, context=None):
        if context is None:
            context = "\nEntrez Commande: "
        while True:
            cmd, *_ = input(context)
            if cmd not in cmd_dict:
                continue
            if cmd == "":
                break
            cmd_dict[cmd]()


class File:
    """Functions on files
    - window to select a file
    - window to select a directory
    - copy file to a directory
    - open a file (with system)
    - création d'un fichier sous n'importe quel cas (existe déjà, requiers dirs, ...)
    -
    """



    @classmethod
    def copy_file_to(cls, base_file_path, directory_location):
        """Copy a file to a dir and return the new path if successful"""
        try:
            file_name = os.path.basename(base_file_path)
            new_file_path = os.path.join(directory_location, file_name)
            shutil.copy2(base_file_path, new_file_path)
            logger.info(f"Fichier copié: {new_file_path}")
        except Exception as e:
            logger.warning(f"Copie fichier : Error {e}")
            return False
        return new_file_path

    @classmethod
    def open_file(cls, file_path):
        """Show/open a file (any type)
        pre:  - file_path
              - import subprocess, platform
        """
        try:
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['start', '""', file_path], shell=True)
            elif system == 'Darwin':
                subprocess.run(['open', file_path])
            elif system == 'Linux':
                subprocess.run(['xdg-open', file_path])
            else:
                print("Unsupported operating system")
        except Exception as e:
            print(f"An error occurred: {e}")

    @classmethod
    def create_file(cls, path, can_make_dirs=True, default_content=None, indent=4):
        """If it does not exist, Create the specified file and dirs if needed."""
        if os.path.exists(path):
            logger.info("\tAlready exists")
            return
        if not os.path.exists(parents_dir := os.path.dirname(path)) and not can_make_dirs:
            logger.warning(f"Parent DirNotFound: {parents_dir}")
            return
        (os.makedirs(parents_dir, exist_ok=True) if parents_dir else None)
        with open(path, 'w') as file:
            if isinstance(default_content, str):
                file.write(default_content)
            elif isinstance(default_content, (list, dict)):
                json.dump(default_content, file, indent=indent)
        logger.info("File created")

    @classmethod
    def add_line(cls, filepath, information, line_index=-1):
        logger.info(f"AddLine: START: ({information}) in {filepath} (at {line_index})")
        if not os.path.exists(filepath):
            logger.warning(f"FileNotFound: {filepath}")
            return
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if line_index > len(lines) - 1:
            logger.warning(f"Selected Out of the List ({line_index} +1)")
            return
        lines.insert(line_index, str(information) + "\n")
        with open(filepath, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    @classmethod
    def delete_line(cls, filepath, line_index):
        if not os.path.exists(filepath):
            logger.warning(f"FileNotFound: {filepath}")
            return
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if line_index > len(lines) - 1:
            logger.warning(f"Selected Out of the List ({line_index} +1)")
            return
        del lines[line_index]
        with open(filepath, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    class JsonFile:

        @classmethod
        def check_and_load_jsondict(cls, jsonfile_path: str) -> dict | None:
            """Check if file exists and load it in python"""
            if not os.path.exists(jsonfile_path):
                logger.warning(f"FileNotFound: {jsonfile_path}")
                return
            if os.path.splitext(jsonfile_path)[1] != '.json':
                logger.warning(f"JsonFileError: type must be json ({jsonfile_path})")
                return
            with open(jsonfile_path, 'rb') as jfile:
                content = json.load(jfile)
            if not isinstance(content, dict):
                logger.warning(f"JsonFileContentError: content must be dict")
                return
            return content

        @classmethod
        def get_value_jsondict(cls, jsonfile_path: str, key: str, handle_keyERROR=False, default_val=None):
            """get key for json file
            @pre: a path to settings
                  a key for the dictionary
                  set error managing"""
            # Error handling
            if (dict_content := cls.check_and_load_jsondict(jsonfile_path)) is None:
                return
            # return value
            if handle_keyERROR:
                if key not in dict_content: logger.info(f"JsonFileContent: key not in j-dict")
                return dict_content.get(key, default_val)
            return dict_content[key]

        @classmethod
        def set_value_jsondict(cls, jsonfile_path, key, value, can_modify_key=True, can_add_key=True):
            """Set value for a key in a json file"""
            # Error handling
            if (dict_content := cls.check_and_load_jsondict(jsonfile_path)) is None:
                return
            if not can_modify_key and key in dict_content:
                logger.warning(f"JsonFileContent: key already exists")
                return False
            if not can_add_key and key not in dict_content:
                logger.warning(f"JsonFileContent: key not in json-dict")
                return False
            # Set value
            dict_content[key] = value
            with open(jsonfile_path, 'w') as jfile:
                json.dump(dict_content, jfile, indent=4)

    class JsonLine:

        @classmethod
        def made_list_of_jsonline(cls, filename):
            """Traduit un fichier json line liste de tuple (1line -> 1tuple)"""
            if not os.path.exists(filename):
                logger.warning("DATAFileNotFound: %s" % filename)
                return
            path_data = []
            with open(filename, "rb") as file:
                for line in file:
                    path_data.append(tuple(json.loads(line)))
                logger.info("Sources: \n%s\n" % path_data)
            return path_data

        @classmethod
        def add_a_jsonline(cls, information, filename="data/paths_list.json", tuple_rather_list=True):
            """Add a json line with [the source path, and the target path]"""
            if not os.path.exists(filename):
                logger.warning("DATAFileNotFound: %s" % filename)
                return
            line_type = tuple if tuple_rather_list else list
            with open(filename, 'r') as file:
                data = [line_type(json.loads(line)) for line in file]
            data.append(information)
            with open(filename, 'w') as file:
                for entry in data:
                    json.dump(entry, file)
                    file.write('\n')

    class CSV:
        pass



class Formatting:

    @classmethod
    def reforme(cls, data):
        """Rend les données entrées dans le type approprié
        @pre : nombre (entier, flaot, Complex) ou txt"""
        try:  # n est un nombre
            if float(data) >= 0:
                return max(abs(int(data)), float(data))
            else:
                return min(abs(int(data)), float(data))
        except:
            if isinstance(data, complex):  # AttributeError  #n est un complex
                if data == 0:
                    return 0  # sinon il donne 0+0j
                return data
            if ("−") in data:  # nombre négatif mal écrit
                return reforme(data.replace("−", "-"))
            if any(char in data for char in ".,;[](){}"):  # n est entr crochet/parenthèses
                for caract in ".,;[](){}":
                    data = data.replace(caract, "")
                data = reforme(data)  # re-tester
            else:
                print("Rentrez des données séparées par un espace")
                return False
            return data

    @classmethod
    def digitpart(cls, part, could_be_txt=False):
        """Retourne un nombre pour une chaine contenant une expression math"""
        parametre = ""
        for c in part:
            if c.isdigit() or c in "+/=.":
                parametre += c
        try:
            return eval(parametre)
        except ZeroDivisionError:
            print("Division par 0")
        except SyntaxError:
            if could_be_txt and parametre == "":
                return part
            else:
                print(f"Syntaxe invalide for {part} or {parametre}")
        except Exception as e:
            print(f"Erreur : {e}")

    @classmethod
    def round_significant(cls, number, n=2, base=10):
        if number == 0:
            return 0.0
        magnitude = n - int(math.floor(math.log(abs(number), base))) - 1
        return round(number, magnitude)


class OutNetwork:

    @classmethod
    def send_notif_mail(cls, receiver, message, subject="NOTIFICATION"):
        """
        Attention : n'encode pas les caractères {é, }
        """
        # SENDER CONFIG
        try:
            sender = File.JsonFile.get_value_jsondict("sender_mail", "main_settings.json")
            psw = File.JsonFile.get_value_jsondict("sender_mail_key", "main_settings.json")
        except Exception as e:
            logger.warning(f"Couldn't (get) SETTINGS mail sender : {e}")
            return
        # CONTENT
        text = f"Subject: {subject}\n\n{message}"
        # SET UP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, psw)
        # SENDING
        server.sendmail(sender, receiver, text)


class GetData:
    file_of_filepath = "files_history.txt"

    @classmethod
    def get_current_file(cls):
        with open("files_history.txt", 'r') as file:
            filepath = file.read()
        if os.path.exists(filepath):
            return filepath
        logging.error(f"Error NotFoundFile: {filepath}")


class GUI:
    _last_active_window = None
    main_window = None

    @classmethod
    @property
    def last_active_window(cls):
        print(f"Getting last_active_window")
        return cls._last_active_window

    @classmethod
    def set_basic_window(cls, title="Tableau des commandes", level="auto", themename="journal", size=""):
        """Create a window in proper level"""

        def master_window_is_open() -> bool:
            if tk._default_root is None:
                return False  # Aucune fenêtre principale n'est ouverte
            elif tk._default_root.winfo_exists():
                return True  # Une fenêtre principale est déjà ouverte
            return False

        if level == "master" or (level == "auto" and not master_window_is_open()):
            window = ttk.Window(themename=themename)
            logger.info(f'Window created: MASTER level ("{title}")')
        elif level == "toplevel" or (level == "auto" and master_window_is_open()):
            window = ttk.Toplevel()
            logger.info(f'Window created: TOPLEVEL level ("{title}")')
            def close():
                logger.debug(f'Toplevel window: withdraw and quit ("{title}")')
                window.quit()
                window.withdraw()
            window.protocol("WM_DELETE_WINDOW", close)
        else:
            logger.error(f"Window creation error: get UNKNOWN state ({level=}, {master_window_is_open()})")
            return

        window.title(title)
        window.geometry(size)
        return window

    @classmethod
    def ask_yes_no(cls, titre, question):

        result = None
        popup = GUI.set_basic_window(title=titre)
        popup.geometry("200x100")

        def manage_response(response):
            if response == "yes":
                result = True
            else:
                result = False
            popup.quit()
            popup.destroy()

        label = ttk.Label(popup, text=question)
        label.pack(pady=10)

        button_frame = ttk.Frame(popup)
        ttk.Button(button_frame, text="Oui", command=lambda : manage_response("yes")).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Non", command=lambda: manage_response("no")).pack(padx=5, side=tk.LEFT)
        button_frame.pack(pady=10)
        popup.mainloop()
        return result

    @classmethod
    def ask_file(cls, context="fichier", types=[("Fichier", "*.*")], multiple=False):
        """Ask for a file (not a dir)
        pre:  context, filetype(optional)
        post: file navigation window
              if file selected, file path
        - Peut entrainer un coonfli entre fenêtre Tkinter"""
        root1 = Tk()
        root1.withdraw()  # cacher la fenlêtre principale

        filepath = filedialog.askopenfilename(
            # initialdir=None,  # Répertoire initial où la boîte de dialogue s'ouvre
            title=f"Choisir {context}",  # Titre de la boîte de dialogue
            filetypes=types,    # Types de fichiers autorisés, par exemple [("Fichiers image", "*.png;*.jpg")]
            # defaultextension="",  # Extension par défaut si l'utilisateur ne spécifie pas d'extension
            # initialfile="",    # Nom de fichier pré-rempli dans la boîte de dialogue
            # parent=None,       # Widget parent de la boîte de dialogue
            multiple=multiple,  # Permettre la sélection de plusieurs fichiers (True/False)
        )
        logger.info(filepath)
        return filepath

    @classmethod
    def ask_dir(cls, root=None, initialdir=os.getcwd(), can_cancel=True):
        """Can only select a directory"""
        if root is None:
            logger.info("Root not provided -> default root")
            folder_path = filedialog.askdirectory(initialdir=initialdir)  # Open a dialog for folder selection
        else:
            logger.info("Root provided -> root")
            folder_path = filedialog.askdirectory(parent=root, initialdir=initialdir)
        logger.info(f"Folder selected: {folder_path}")

        if os.path.isdir(folder_path):
            return folder_path
        elif not can_cancel:
            logger.info("Aucun dossier sélectionné -> return current cwd")
            return os.getcwd()
        logger.info("Aucun dossier sélectionné -> return None")

    @classmethod
    def set_cmd_buttons(cls, window, commandes):
        # Input field
        input_frame = ttk.Frame(master=window)
        # Create buttons
        buttons = {}
        for name, func in commandes.items():
            logger.info(name)
            buttons[name] = ttk.Button(master=input_frame, text=name, command=func)
        # Add buttons to input field
        for button in buttons.values():
            button.pack(pady=5)
        # Ajouter les éléments (to window)
        input_frame.pack()

    @classmethod
    def ask_entry(cls, title="Entrez le mot de passe", size="250x100", can_cancel=True) -> str:
        # Pop-up window
        window: tk.Toplevel = GUI.set_basic_window(title=title, size=size)
        # Variable pour stocker le mot de passe
        password = tk.StringVar()
        password.set("")

        # Fonctions pour les boutons
        def on_validate(x=None):
            logger.info("<ask_entry> field filled")
            password.set(entry.get())
            window.quit()
            window.destroy()

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
        validate_button = ttk.Button(button_frame, text="Valider", command=on_validate)
        validate_button.pack(side=tk.RIGHT)
        if can_cancel:
            cancel_button = ttk.Button(button_frame, text="Annuler", command=lambda x: window.destroy())
            cancel_button.pack(side=tk.LEFT)

        # Lancement de la fenêtre
        window.mainloop()
        return password.get()

    @classmethod
    def window_with_entry_labeled(cls, fields_entries, title="Enregistrer un compte", window=None):
        """Fonction pour créer une fenêtre avec des champs de saisie.
        Can add labels to existing window if arg window= provided"""
        if not window:
            # Création de la fenêtre
            logger.debug(f"\tAddAccount: Window not provided -> creating new window")
            window = cls.set_basic_window(title=title, size=None)

        validation = tk.BooleanVar()

        def save_account():
            validation.set(True)
            for name in fields_entries.keys():
                fields_entries[name] = entries[name].get()
            logger.info(f"\tDonnées : \n{fields_entries}")
            window.quit()
            window.destroy()

        def cancel():
            validation.set(False)
            logger.info(f"\tAddAccount: CANCELLED")
            window.quit()
            window.destroy()

        entries = {}
        name: str = ""
        for row, name in enumerate(fields_entries.keys()):
            name = name.capitalize() + ":"
            ttk.Label(window, text=name.capitalize()).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            entries[name] = ttk.Entry(window)
            entries[name].grid(row=row, column=1, padx=5, pady=5)

        # Bouton pour enregistrer le compte
        save_button = ttk.Button(window, text="Enregistrer", command=save_account)
        save_button.grid(row=len(fields_entries), column=1, padx=5, pady=10)
        # Bouton pour annuler
        save_button = ttk.Button(window, text="Annuler", command=cancel)
        save_button.grid(row=len(fields_entries), column=0, padx=5, pady=10)
        # Exécution de la boucle principale
        logger.info(f"Window STARTED")
        window.mainloop()
        return validation.get()

    @classmethod
    def parse_buttons_on_object(cls, objet_to_str_list: iter, buttons_func_dict: dict[str: callable], window,
                                title="Liste d'informations", first_row=0) -> None:
        """Fonction pour afficher une liste d'informations avec un bouton 'Copier' à droite de chaque ligne."""
        # Affichage des informations avec un bouton par ligne pour chaque fonction
        buttons_obj = {}
        for row, info in enumerate(objet_to_str_list, first_row):  # Chaque object
            ttk.Label(window, text=str(info)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            for column, (label, func) in enumerate(buttons_func_dict.items(), 1):
                logger.debug(f'Création du bouton "{label}" pour rangée n°{row}')
                general_func = lambda function=func, data=info: function(data)
                buttons_obj[label + str(row)] = ttk.Button(window, text=label, command=general_func)
                buttons_obj[label + str(row)].grid(row=row, column=column, padx=10, pady=5)




class Anki():
    @classmethod
    def create_cards_fromlist_ofdict(cls, dict_list):
        """Create cards from a list of dict
        pre:  list of dict
                dict = {"front": <type>, "back": <type>, "template": str}
        post: deck of genanki
        """
