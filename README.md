# pswmanage - Password Manager

Auteur(s) : Gaétan Lepage
Création : 2024
Description :

> Gestionnaire de mots de passe et comptes sûr (chiffrement symétrique, backups)

## Prérequis

- **Python** : `Python 3.8+`
- **Dépendances** :
  - `pyperclip==1.9.0`
  - `tk==0.1.0`
  - `ttkbootstrap==1.10.1`
  - utility from utility project
  - a logging configuration like the one in this repo

## Utilisation

```bash
pip install -r requirements.txt
mkdir data
mkdir data/logs
python -m pswmanage
```

## Versions

1.0.0 - 30/08/24 - Mise en fonctionnement
2.0.0 - 01/09/24 - Fonctionnement en package local

## Améliorations futurs

**Road map :**

2.1.0 - // - feat: création/choisir fichier de sauvegarde sur l'ouverture de l'app
2.2.0 - // - fix: corrections et amélioration du log_config.py
...
3.0.0 - // - feat: meilleur fenêtre de recherche (GUI et fonctionnalités)
4.0.0 - // - feat: possibilité de générer une image (blured) imprimable des indentifiants

**Suggestions :**

- (test) Tester l'utilisation de backup

## Plus d'informations

### Structure du projet

### Points techniques interressants
