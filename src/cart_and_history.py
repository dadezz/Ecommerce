from werkzeug.utils import secure_filename

from sqlclass import Utente, engine, select,Prodotti, Carrello, ProdottiCarrelli, CarrelloUtenti, ProdottiStorici,Storico
from extention import *

from flask import flash
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import UserMixin,login_user,logout_user,current_user,login_required
from hashlib import sha256
from sqlalchemy import update, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

cart_bp = Blueprint('cart_bp', __name__)

"""
cart_and_history.py contiene tutte le funzioni relative al carrello e allo storico:
visualizzazione, aggiunta e rimozione prodotti etc.
"""

# visualizzazione dei prodotti nel carrello
@cart_bp.route('/carrello')
@login_required
def carrello():

    _products = []
    img_src = []
    cart_id_entries = []
    total_price = 0  
    query = request.args
    c = aliased(Carrello)
    p = aliased(Prodotti)
    pc = aliased(ProdottiCarrelli)
    cu = aliased(CarrelloUtenti)
    
    with Session(engine) as s:

        actualUser = current_user.id
        user_cart = (
            s.query(c, p)
            .join(cu, c.id_carrello_entry == cu.id_carrello_entry)
            .join(pc, c.id_carrello_entry == pc.id_carrello_entry)
            .join(p, pc.id_prodotto == p.id_prodotto)
            .filter(cu.user == actualUser)
            .all()
        )
        for c,p in user_cart:
            cart_id_entries.append(c)
            get_images_for_products(_products, p, img_src)
            total_price += c.qta * p.Prezzo

    s.commit()
    return render_template("cart.html", products=_products, img_src=img_src, zip=zip, id_carrello_entries=cart_id_entries,price = round(total_price,2))

# aggiunta di un articolo al carrello
@cart_bp.route('/added')
@login_required
def add_to_cart():
    if len(request.args) == 0 or 'id' not in request.args or 'qta' not in request.args:
        return "IMPOSSIBILE AGGIUNGERE AL CARRELLO"

    id = request.args['id']
    qta = request.args['qta']
    try:
        qta_int = int(qta)
        if qta_int < 0:
            raise ValueError
    except:
        return "quantità non valida"

    with Session(engine) as s:
        car = Carrello(qta=qta_int)
        s.add(car)
        s.commit()

        car_id = car.id_carrello_entry
        s.add(ProdottiCarrelli(id_prodotto=id,id_carrello_entry=car_id))
        s.add(CarrelloUtenti(id_carrello_entry=car_id,
                             user=current_user.id))
        s.commit()

    return render_template('added.html')

# rimozione di un articolo dal carrello
@cart_bp.route('/Rimosso')
@login_required
def remove_from_cart():
    if len(request.args) == 0 or 'id' not in request.args:
        return "IMPOSSIBILE RIMUOVERE DAL CARRELLO"

    try:
        actual_id = int(request.args["id"])
    except ValueError:
        return "Inserisci un valore numerico valido per l'ID"

    actual_user = current_user.id

    with Session(engine) as s:
        try:
            res = s.query(CarrelloUtenti).filter_by(id_carrello_entry=actual_id).one()

            if res.user != actual_user:
                return "Non hai i permessi necessari per rimuovere questo articolo"
            res = s.query(Carrello).filter_by(id_carrello_entry=actual_id).one()

            s.delete(res)
            s.commit()
        except NoResultFound:
            return "L'elemento specificato non esiste nel carrello"
        except Exception as e:
            s.rollback()
            return f"Si è verificato un errore durante la rimozione: {str(e)}"

    return render_template('removed.html')

# gestione del pagamento
@cart_bp.route('/Payed')
@login_required
def payed():
    try:
        # Ottenere l'ID dell'utente loggato
        actualUser = current_user.id

        # Alias per le tabelle coinvolte
        c = aliased(Carrello)
        p = aliased(Prodotti)
        pc = aliased(ProdottiCarrelli)
        cu = aliased(CarrelloUtenti)

        with Session(engine) as s:
            user_cart = (
                s.query(c, p)
                .join(cu, c.id_carrello_entry == cu.id_carrello_entry)
                .join(pc, c.id_carrello_entry == pc.id_carrello_entry)
                .join(p, pc.id_prodotto == p.id_prodotto)
                .filter(cu.user == actualUser)
                .all()
            )

            # Verifichiamo la disponibilità dei prodotti nel carrello
            insufficient_stock = []

            for cart, product in user_cart:
                if cart.qta <= product.disponibilita:
                    stmt = (
                        update(Prodotti)
                        .where(Prodotti.id_prodotto == product.id_prodotto)
                        .values(disponibilita=Prodotti.disponibilita - cart.qta)
                    )
                    s.execute(stmt)
                else:
                    insufficient_stock.append(product.Titolo)

            if insufficient_stock:
                s.rollback()
                # Costruiamo una stringa con i titoli dei prodotti con disponibilità insufficiente
                stringa = ', '.join(insufficient_stock)
                return f"I prodotti [{stringa}] nel tuo carrello superano la quantità disponibile in magazzino"

            for cart, product in user_cart:
                try:
                    # Aggiungo i prodotti comprati allo storico.
                    st = Storico(
                        Data=datetime.utcnow().date(),
                        Nome=product.Titolo,
                        user=current_user.id
                    )
                    s.add(st)
                    s.flush() # Flush per ottenere l'id_storico_entry senza commit
                    new_id = st.id_storico_entry
                    
                    # Aggiungo anche alla tabella intermedia ProdottiStorici per l'integrità referenziale.
                    id_to_be_added = product.id_prodotto
                    res_ = s.query(Prodotti).where(and_(Prodotti.id_prodotto == id_to_be_added,
                                                        Prodotti.disponibilita > 0)).first()
                    ps = ProdottiStorici(
                        id_storico_entry=new_id,
                        id_prodotto= id_to_be_added  if res_ is not None else None
                    )
                    s.add(ps)
                    
                    # Elimino dal carrello
                    res = s.query(Carrello).filter_by(id_carrello_entry=cart.id_carrello_entry).one()
                    s.delete(res)
                    
                    # Elimino le immagini
                    folderpath = os.path.join(UPLOAD_FOLDER, str(product.autore), str(product.id_prodotto))
                    delete_images_dir(folderpath)

                    # Commit unico alla fine di tutte le operazioni
                    s.commit()
                except Exception as e:
                    print("exception occurred ",e)
                    pass

    except SQLAlchemyError as e:
        s.rollback()
        error_message = f"Errore durante il pagamento: {str(e)}"
        return error_message

    except Exception as e:
        s.rollback()
        error_message = f"Errore imprevisto durante il pagamento: {str(e)}"
        return error_message

    return render_template("payed.html")

# visualizzazione delle voci dello storico acquisti
@cart_bp.route('/storico',methods=['GET'])
@login_required
def purchase_history():
    with Session(engine) as s:
        ps = aliased(ProdottiStorici)
        st = aliased(Storico)
        res = s.query(st, ps).join(ps, st.id_storico_entry == ps.id_storico_entry).filter(st.user == current_user.id).all()
    return render_template('storico.html', ris=res)
