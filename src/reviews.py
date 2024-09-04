from werkzeug.utils import secure_filename

from sqlclass import ProdottiRecensioni, Recensioni, engine, Prodotti, func, Recensioni, ProdottiRecensioni
from extention import *
from flask import flash
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import UserMixin,login_user,logout_user,current_user,login_required
from hashlib import sha256
from sqlalchemy import desc
from sqlalchemy import update, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

reviews_page_bp = Blueprint('reviews', __name__)

"""
in reviews.py ci sono tutte le funzioni relative alle recensioni:
visualizzazione e creazione
"""

# visualizzazione 
@reviews_page_bp.route("/reviews/<int:id>")
@reviews_page_bp.route("/reviews/", defaults={'id': None}) #nel caso in cui si scrive solo la route
def reviews(id):

    if id is None:
        return "Error: in Reviews id is Undefined"

    with (Session(engine) as s):
        pr = aliased(ProdottiRecensioni)
        r = aliased(Recensioni)
        p = s.query(Prodotti).filter(Prodotti.id_prodotto == id).first()
        if not p:
            return "Il prodotto non esiste"

        if len(request.args) == 0 or 'sortby' not in request.args or request.args['sortby'] == 'date':
            ris = (
                s.query(r)
                .join(pr, r.id_recensione_entry == pr.id_recensione_entry)
                .filter(pr.id_prodotto == id)
                .all()
            )
        elif request.args['sortby'] == 'asc':
            ris = (
                s.query(r)
                .join(pr, r.id_recensione_entry == pr.id_recensione_entry)
                .filter(pr.id_prodotto == id)
                .order_by(r.numero_stelle)  # Ordina in modo decrescente per data_recensione
                .all()
            )
        elif request.args['sortby'] == 'desc':
            ris = (
                s.query(r)
                .join(pr, r.id_recensione_entry == pr.id_recensione_entry)
                .filter(pr.id_prodotto == id)
                .order_by(desc(r.numero_stelle))  # Ordina in modo decrescente per data_recensione
                .all()
            )
        else:
            return "Parametro non valido"

        # media delle recensioni
        average = s.query(func.avg(r.numero_stelle)).join(pr, r.id_recensione_entry == pr.id_recensione_entry).filter(pr.id_prodotto == id).scalar()
        if average is None:
            average = 0
        else:
            average = round(average, 1)

    return render_template('reviews_template.html', ris=ris, media=average, id = id)

# creazione
@reviews_page_bp.route("/write_review/<int:id>", methods=['GET', 'POST'])
@reviews_page_bp.route("/write_review/", defaults={'id': None})
@login_required
def review_upload(id):

    if id is None:
        return "Error: in Write review id is Undefined"

    if request.method == 'POST':
        title = request.form['Titolo']
        content = request.form['Descrizione']
        star_number = request.form['star']

        with Session(engine) as s:
            # Aggiungi la nuova recensione e committala
            new_rec = Recensioni(user=current_user.id,titolo=title, descrizione=content, numero_stelle=star_number)
            s.add(new_rec)
            s.commit()

            # Recupera l'ID della nuova recensione
            new_rec_id = new_rec.id_recensione_entry

            # Aggiungi la relazione nella tabella ProdottiRecensioni
            s.add(ProdottiRecensioni(id_recensione_entry=new_rec_id, id_prodotto=id))
            s.commit()

        return redirect(url_for('product.product_page', product_id=id))
    else:
        return render_template('write_review.html', product_id=id)
