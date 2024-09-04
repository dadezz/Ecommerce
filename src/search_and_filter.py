from flask import Blueprint, render_template,request
from numpy import double
from sqlclass import engine, and_, Prodotti, prodotti_disponibili
from sqlalchemy.orm import Session
from extention import *

"""
in search_page.py ci sono le funzionalità di ricerca degli annunci, 
con relativa applicazione dei filtri
"""

search_page_bp = Blueprint('search', __name__)

# funzione ausiliaria: creazione lista dei filtri usando come condizioni gli attributi della vista
def filters(min_price,max_price,min_date,max_date,condition,payment_methods,sped,tag):

    tags = [
            "motori",
            "motori2",
            "elettronica",
            "elettronica2",
            "casa",
            "casa2",
            "casa3",
            "casa4",
            "persona",
            "persona2",
            "sport",
            "libri",
            "bici",
            "collezionismo",
            "altro"
    ]

    filt = []
    if min_price and min_price != '':
        if double(min_price) >= DOUBLEMIN:
            filt.append(prodotti_disponibili.columns.Prezzo >= double(min_price))
    if max_price and max_price != '':
        if double(max_price) <= DOUBLEMAX:
            filt.append(prodotti_disponibili.columns.Prezzo <= double(max_price))
    if min_date and min_date != '':
            filt.append(prodotti_disponibili.columns.data_pubblicazione >= min_date)
    if max_date and max_date != '':
            filt.append(prodotti_disponibili.columns.data_pubblicazione <= max_date)

    if condition and condition != '':
        if condition == 'new':
            filt.append(prodotti_disponibili.columns.nuovo == True)
        else:
            filt.append(prodotti_disponibili.columns.nuovo == False)

    if tag and tag in tags:
        filt.append(prodotti_disponibili.columns.tag == tag)

    if payment_methods and '' not in payment_methods:
         if 'visa' in payment_methods:
             filt.append(prodotti_disponibili.columns.visa == True)
         if 'cash' in payment_methods:
             filt.append(prodotti_disponibili.columns.contanti == True)
         if 'barter' in payment_methods:
             filt.append(prodotti_disponibili.columns.baratto == True)
    if sped and sped != '':
        if sped == "yes":
            filt.append(prodotti_disponibili.columns.spedizione == True)
        else :
            filt.append(prodotti_disponibili.columns.spedizione == False)
    return  filt

# applicazione dei filtri
@search_page_bp.route('/search')
def search_page():

    """
    valori possibili che ricevo :
        min 0
        max maxDouble
        data_min : 01/01/2024
        data_max : current_date
        usato : undefined,new,second_hand

        Spiegazione :

        nel primo caso uso la search bar per filtrare i prodotti.
        nel secondo caso uso i filtri per ottenere i prodotti desiderati.
        La parte più difficile è stata fare i filtri
    """
    if request.method == 'GET':
        _products = []
        img_src = []

        with Session(engine) as s:
            tag = request.args.get('Tag')
            min_price = request.args.get('prezzo_min')
            max_price = request.args.get('prezzo_max')
            min_date = request.args.get('data_min')
            max_date = request.args.get('data_max')
            condition = request.args.get('condition')
            payment_methods = request.args.getlist('payment_methods[]')
            sped = request.args.get('Sped')
            search = request.args.get('query')

            """
            come fosse una lambda, sto mettendo in ris la lista con tutte le condizioni che devono essere soddisfatte.
            nella query sottostante, le metto in "and" e applico questi filtri alla query.
            Così facendo la query scritta è sempre una e cambiano dinamicamente i filtri
            """
            ris = filters(min_price, max_price, min_date, max_date, condition, payment_methods, sped,tag)
            products = s.query(prodotti_disponibili).filter(and_(*ris)).all()

            for p in products:
                if search in p.Descrizione or search in p.Titolo:
                    get_images_for_products(_products, p, img_src)

        s.commit()
        return render_template("list_of_products_page_template.html", products=_products, img_src=img_src, zip=zip)

    return render_template("list_of_products_page_template.html")

# semplice render_template
@search_page_bp.route("/filter")
def filter_query():
    return render_template("filters_form_template.html")