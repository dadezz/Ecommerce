from flask import Blueprint, render_template,redirect, request, url_for
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from sqlclass import *
from sqlalchemy.orm import Session
from sqlclass import Prodotti,Utente
from flask_login import current_user, login_required
from extention import *
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import update, and_


product_page_bp = Blueprint('product', __name__)


"""
in product.py sono contenute le funzioni relative alla gestione
dei prodotti: visualizzazione, creazione, eliminazione e modifica
"""

# homepage del sito: lista di tutti i prodotti disponibili
@product_page_bp.route('/')
def root():

    with Session(engine) as s:
        products = s.query(prodotti_disponibili).all()

    _products = []
    img_src = []
    for p in products:
        get_images_for_products(_products, p, img_src)
    s.commit()

    return render_template("list_of_products_page_template.html", products=_products, img_src=img_src, zip=zip)

# pagina del prodotto
@product_page_bp.route('/<int:product_id>')
def product_page(product_id):

    if product_id is None:
        return 'Product Page : product_id Undefined'

    with Session(engine) as s:
        p = s.get(Prodotti, product_id)
        s.close()

    if p is None:
        return "Il prodotto non esiste"

    folderpath = os.path.join(UPLOAD_FOLDER, str(p.autore), str(p.id_prodotto))
    if os.path.exists(folderpath) and os.path.isdir(folderpath):
        files = os.listdir(folderpath)
        files_list= []
        for f in files:
            files_list.append(os.path.join(folderpath, f))

        return render_template('product_page_template.html', product=p,img=files_list)
    else:
        f = [placeholder]
        return render_template('product_page_template.html', product=p,img=f)

# creazione del prodotto
@product_page_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def product_upload():
    if request.method == 'POST':
        if current_user.venditore == False:
            return "Accesso negato , non sei un venditore :("

        title = request.form['Titolo']
        content = request.form['Descrizione']
        category = request.form['Tag']
        payment_methods = request.form.getlist('payment_methods')
        price_ = request.form['prezzo']
        shipment = request.form['shipment']
        place = request.form.get('luogo')
        quantity_ = request.form['quantita']
        condition = request.form['condition']
        images = request.files.getlist('images[]')

        try:
            quantity = int(quantity_)
            if quantity < 0:
                raise ValueError
        except:
            return "quantità non valida"

        try:
            price = float(price_)
            if price == 0:
                raise ValueError
        except:
            return "prezzo non valido"

        #controlla che le immagini siano corrette prima di inserire i dati nel db.
        #in caso lancia una errore alla prima immagine che non va bene.
        try :
            for image in images:
                if image and not allowed_file(image.filename):
                     raise ValueError
        except:
            return "una delle immagini non è nel formato corretto : "+ image.filename

        with Session(engine) as s:
            new_prod = Prodotti(Titolo=title,
                                Descrizione=content,
                                Prezzo=price,
                                visa='visa' in payment_methods,
                                contanti='cash' in payment_methods,
                                baratto='barter' in payment_methods,
                                spedizione= shipment == 'yes',
                                luogo=place,
                                disponibilita=quantity,
                                data_pubblicazione=datetime.utcnow().date(),
                                nuovo=condition == 'yes',
                                autore=current_user.id,
                                tag=category
                                )
            s.add(new_prod)
            s.commit()
            id  = new_prod.id_prodotto

        image_paths = []
        for image in images:
            if image: # qua serve solo controllare che la lista non sia vuota
                filename = secure_filename(image.filename)
                filepath = os.path.join(UPLOAD_FOLDER, str(current_user.id), str(id))
                os.makedirs(filepath, exist_ok=True)
                filepath = os.path.join(str(filepath), str(filename))
                image.save(filepath)
                image_paths.append(filepath)
        return redirect(url_for('product.product_page', product_id=id))
    else:
        if current_user.venditore == True:
            return render_template('upload_form_template.html')
        else :
            return "Accesso negato , non sei un venditore :("

# rimozione del prodotto
@product_page_bp.route('/ArticoloRimosso')
@login_required
def product_removal():

    # controlli
    if current_user.venditore == False:
        return "Accesso negato , non sei un venditore :("
    if len(request.args) == 0 or 'id' not in request.args:
        return "IMPOSSIBILE RIMUOVERE L'ARTICOLO"
    try:
        actual_id = int(request.args["id"])
    except ValueError:
        return "Inserisci un valore numerico valido per l'ID"

    actual_user = current_user.id

    with Session(engine) as s:
        try:
            ris = s.query(Prodotti).filter_by(id_prodotto=actual_id).one()
            if ris.autore != actual_user:
                return "Non hai i permessi necessari per rimuovere questo articolo (Non sei l'autore)"

            s.delete(ris)
            s.commit()
            # Elimino le immagini
            folderpath = os.path.join(UPLOAD_FOLDER, str(current_user.id),str(actual_id))
            print(folderpath)
            if os.path.exists(folderpath):
                delete_images_dir(folderpath)

        except NoResultFound:
            return "L'elemento specificato non esiste"
        except Exception as e:
            s.rollback()
            return f"Si è verificato un errore durante la rimozione: {str(e)}"
        
    return render_template('removed.html')

# modifica del prodotto
@product_page_bp.route('/Modifica')
@login_required
def product_modification():
    # controlli
    if current_user.venditore == False:
        return "Accesso negato , non sei un venditore :("
    if len(request.args) == 0 or 'id' not in request.args:
        return "IMPOSSIBILE MODIFICARE L'ARTICOLO"
    try:
        actual_id = int(request.args["id"])
    except ValueError:
        return "Inserisci un valore numerico valido per l'ID"

    return  render_template("modify_form_template.html", id = actual_id)

# prodotto modificato
@product_page_bp.route('/Modificato', methods=['GET', 'POST'])
@login_required
def product_modified():
    if request.method == 'POST':
        # tutto cio che mi serve
        title = request.form['Titolo']
        content = request.form['Descrizione']
        category = request.form['Tag']
        payment_methods = request.form.getlist('payment_methods')
        price_ = request.form['prezzo']
        shipment = request.form['shipment']
        place = request.form.get('luogo')
        quantity_ = request.form['quantita']
        condition = request.form['condition']
        id = int(request.form['id'])
        images = request.files.getlist('images[]')

        # controllo sulla quantità
        try:
            quantity = int(quantity_)
            if quantity < 0:
                raise ValueError
        except:
            return "quantità non valida"

        # controllo sul prezzo
        try:
            price = float(price_)
            if price == 0:
                raise ValueError
        except:
            return "prezzo non valido"

        #controlla che le immagini siano corrette prima di inserire i dati nel db.
        #in caso lancia una errore alla prima immagine che non va bene.
        try :
            for image in images:
                if image and not allowed_file(image.filename):
                    raise ValueError
        except:
            return "una delle immagini non è nel formato corretto"

        # connessione al db
        try:
            with Session(engine) as s:
                # autorizzazioni valide?
                actual_user = current_user.id
                try:
                    ris = s.query(Prodotti).filter_by(id_prodotto=id).one()
                except NoResultFound:
                    return "L'articolo specificato non esiste"
                if ris.autore != actual_user:
                    return "Non hai i permessi necessari per rimuovere questo articolo (Non sei l'autore)"

                # statement di update
                stmt = (
                    update(Prodotti)
                    .where(Prodotti.id_prodotto == id)
                    .values(Titolo=title,
                            Descrizione=content,
                            Prezzo=price,
                            visa='visa' in payment_methods,
                            contanti='cash' in payment_methods,
                            baratto='barter' in payment_methods,
                            spedizione= shipment == 'yes',
                            luogo=place,
                            disponibilita=quantity,
                            data_pubblicazione=datetime.utcnow().date(),
                            nuovo=condition == 'yes',
                            autore=current_user.id,
                            tag=category)
                )
                # eseguo
                s.execute(stmt)
                s.commit()

            # rimozione immagini vecchie
            folderpath = os.path.join(UPLOAD_FOLDER, str(current_user.id),str(id))
            if os.path.exists(folderpath):
                delete_images_dir(folderpath)

            # metto immagini nuove
            image_paths = []
            for image in images:
                if image: # qua serve solo controllare che la lista non sia vuota
                    filename = secure_filename(image.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, str(current_user.id), str(id))
                    os.makedirs(filepath, exist_ok=True)
                    filepath = os.path.join(str(filepath), str(filename))
                    image.save(filepath)
                    image_paths.append(filepath)

            # tutto dovrebbe essere andato ok
            return render_template("success.html")

        # per qualsiasi errore:
        except Exception as e:
            s.rollback()
            return f"Si è verificato un errore durante la rimozione: {str(e)}"

    # come ci arrivi in "modificato" senza post?
    else:
        return "non so come sei arrivato qui (expected: POST method)"