from flask import app
from flask_login import LoginManager
import os
import shutil
from numpy import finfo,float64
from datetime import  datetime
from sqlalchemy.orm import aliased

"""
extention.py serve a rendere librerie, funzioni e variabili globali
comuni a tutti i file in cui servono
"""

login_manager = LoginManager()

"""
questo pezzo di codice fa in modo che ogni volta che
si vuole accedere ad una parte in cui è necessario l'accesso 
si viene indirizzati alla pagina di login
"""
login_manager.login_view = 'user_manager.login_page'

# Base directory of the project
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Directory where uploaded files will be stored
UPLOAD_FOLDER = os.path.join('static','uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_PATH = 16 * 1024 * 1024 # Maximum file size: 16MB

placeholder = os.path.join(UPLOAD_FOLDER,"product-placeholder.png")

#controlla che la estensione dei file siano corretti
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#valori massimi per il valore dei prezzi.
DOUBLEMAX = finfo(float64).max
DOUBLEMIN = 0.0

start_date = datetime(2024, 12, 1).date()

"""
eliminazione delle immagini di un prodotto, dato il path della cartella
"""
def delete_images_dir(folder_path):
    # Verifica se il percorso della cartella esiste
    if os.path.exists(folder_path):
        # Elimina tutti i file nella cartella
        for filename in os.listdir(folder_path):
            complete_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(complete_path):
                    os.remove(complete_path)
                elif os.path.isdir(complete_path):
                    shutil.rmtree(complete_path)  # Elimina anche le sotto-cartelle ricorsivamente
            except Exception as e:
                print(f"Errore durante l'eliminazione di {complete_path}: {e}")
                raise e

        # Elimina la cartella stessa
        try:
            os.rmdir(folder_path)
            print(f"Cartella {folder_path} eliminata con successo.")
        except Exception as e:
            print(f"Errore durante l'eliminazione della cartella {folder_path}: {e}")
            raise e
    else:
        print(f"Il percorso {folder_path} non esiste.")

def get_images_for_products(_products, p, img_src) -> None:
    _products.append(p)
    folderpath = os.path.join(UPLOAD_FOLDER, str(p.autore), str(p.id_prodotto))
    if os.path.exists(folderpath) and os.path.isdir(folderpath):
        files = os.listdir(folderpath)
        filepath = os.path.join(folderpath, files[0])

        img_src.append(filepath)
        print(filepath)
    else:
        img_src.append(placeholder)
        print(placeholder)