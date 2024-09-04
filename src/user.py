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

user_manager_bp = Blueprint('user_manager', __name__)

"""
in user.py ci sono tutte le funzioni relatve all'utente:
login, logout, creazione ed eliminazione account, modifica dell'anagrafica, 
visualizzazione dei propri dati e dei propri annunci etc.
"""


'''
Voglio ricordarmi quando un utente è loggato all'interno del sito :
Uso la classe session che mi permette di simulare questo meccanismo.
Ogni volta che faccio il login (dopo aver fatto il confronto dei dati con il dbms)
aggiungo nel campo user di session il fatto ho fatto il login corretto.
session['user'] = user , mi segn
ogni utente quindi potenzialmente ha una sessione diversa che è criptata una chiave
Ogni volta che faccio logout invece rimuovo dalla sessione l'utente con cui ci siè
loggati.

  if session.get('user'): (controllo se effettivamente il campo user esiste)
        if session['user']: (controllo se nel capo user è presente qualcosa)
            session.pop('user',default=None) rimuovo il campo in modo da toglierlo dalla sessione
'''

# classe che modella CurrentUser
class User(UserMixin):
    def __init__(self, id, password,venditore):
        self.id = id
        self.password = password
        self.venditore = venditore

# carica tutte le informazioni per costruire CurrentUser
@login_manager.user_loader
def user_loader(user_id):
    with Session(engine) as s:
        u = s.get(Utente, user_id)
    return User(id=u.user, password=u.password,venditore=u.venditore)

# funzione ausiliaria: hash della password
def hash_password(password):
    salt = os.urandom(16)  # Genera un sale casuale di 16 byte
    pwd_hash = sha256(salt + password.encode('utf-8')).digest()
    return salt + pwd_hash  # Concatena sale e hash

# gestione del login
@user_manager_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password'].encode('utf8')
        with Session(engine) as s:
            try:
                u = s.query(Utente).where(Utente.user == user).one()
                stored_pwd = u.password
                salt = stored_pwd[:16]
                stored_pwd_hash = stored_pwd[16:]
                pwd_hash = sha256(salt + pwd).digest()
                if pwd_hash == stored_pwd_hash:
                    login_user(User(id=u.user, password=u.password,venditore=u.venditore))
                    return redirect(url_for('user_manager.dashboard'))
                else:
                    flash("Credenziali errate: username o password errati")
            except NoResultFound:
                    flash("Credenziali errate: username o password errati")
                    return render_template('login_page_template.html')
    return  render_template("login_page_template.html") # if not post method

# gestione del logout
@user_manager_bp.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('product.root'))

# creazione account
@user_manager_bp.route('/sign_in', methods=['GET', 'POST'])
def account_creation():
    if request.method == 'POST':
        email = request.form['email']
        user = request.form['username']
        pwd1 = request.form['password1']
        pwd2 = request.form['password2']
        v = request.form['vendor']

        print("venditore : ",v)
        v = v == 'yes' #variabile booleana : venditore ? si , no.

        '''
          per rendere più pulito il messaggio di errore : controllo
          sia che lo user al momento dell'inserimento sia univoco
          che anche la email.
        '''
        print(user, pwd1, pwd2)
        with Session(engine) as s:
            stmt = select(Utente).where(Utente.user == user)

            # controllo se esiste già un utente con lo stesso nome.
            # se non ne esistono, la variabile è none
            try:
                user_result = s.execute(stmt).one()
            except NoResultFound:
                user_result = None
                print("exc")

            if user_result is not None:
                flash("Nome utente già utilizzato da un altro utente")
                return redirect(url_for("user_manager.account_creation"))

        # se arrivo qui, l'utente può essere aggiunto senza problemi
        if pwd1 == pwd2:
            hashed_pwd = hash_password(pwd1)
            with Session(engine) as s:
                s.add(Utente(user= user,password=hashed_pwd,contatto_mail=email,
                      venditore = v))
                s.commit()
                return render_template("success_sign_in.html")
        else:
            flash("le password immesse devono essere uguali")
            return redirect(url_for('user_manager.account_creation'))
    else:
        return render_template('create_account_page.html')

# eliminazione account
@user_manager_bp.route('/deleteAccount')
@login_required
def account_deletion():
    try:
        with Session(engine) as s:
            user = s.get(Utente, current_user.id)

            if user:
                s.delete(user)
                s.commit()

                # Elimino le immagini
                folderpath = os.path.join(UPLOAD_FOLDER, str(user.user))
                if os.path.exists(folderpath):
                    delete_images_dir(folderpath)
                logout_user()
                return render_template("removed.html")
            else:
                logout_user()
                return "<h1>utente non trovato</h1>"

    except Exception as e:
        s.rollback()  # In caso di errore, fa rollback della sessione
        print(f"Errore durante l'eliminazione dell'account: {e}")  # Per il log
        return f"Si è verificato un errore durante l'eliminazione dell'account: {str(e)}"

# pagina informazioni utente
@user_manager_bp.route('/dashboard')
@login_required
def dashboard():
    print(type(current_user))
    with Session(engine) as s:
        u = s.get(Utente,current_user.id)
    return render_template('dashboard.html', user=current_user.id,
                                       email=u.contatto_mail, telefono=u.contatto_tel,venditore = u.venditore)

# aggiunta ruolo venditore
@user_manager_bp.route('/add_role')
@login_required
def add_vendor():
    print(type(current_user))
    with Session(engine) as s:
        stmt = (
            update(Utente)
            .where(Utente.user == current_user.id)
            .values(venditore = True)
        )
        s.execute(stmt)
        s.commit()

    return render_template('success.html')

# lista degli annunci pubblicati dall'utente
@user_manager_bp.route('/My_sales')
@login_required
def user_sales_list():

    with Session(engine) as s:
        products = s.query(Prodotti).where(Prodotti.autore == current_user.id).all()
    _products = []
    img_src = []
    for p in products:
        get_images_for_products(_products, p, img_src)
    s.commit()

    return render_template("list_of_products_page_template.html", products=_products, img_src=img_src, zip=zip)

# cambio anagrafica: mail
@user_manager_bp.route("/Change_Mail",methods=["GET","POST"])
@login_required
def change_mail():
    usr = current_user.id
    with Session(engine) as s:
        old_mail = s.query(Utente.contatto_mail).filter(Utente.user == usr).one()[0]
        s.close()
    if request.method == "POST":
        mail1 = request.form['mail1']
        mail2 = request.form['mail2']

        if mail1 != mail2:
            flash("Le email non combaciano")
            return render_template('change_mail.html', vecchia_mail=old_mail)
        with Session(engine) as s:
            stmt = (
                update(Utente)
                .where(Utente.user == usr)
                .values(contatto_mail = mail1)
            )
            s.execute(stmt)
            s.commit()
        return render_template("success.html")
    else:
        return render_template('change_mail.html', vecchia_mail=old_mail)

# cambio anagrafica: telefono
@user_manager_bp.route("/Change_Phone",methods=["GET","POST"])
@login_required
def change_number():
    usr = current_user.id
    with Session(engine) as s:
        old_number = s.query(Utente.contatto_tel).filter(Utente.user == usr).one()[0]

    if request.method == "POST":
        num1 = request.form['tel1']
        num2 = request.form['tel2']

        if num1 != num2:
            flash("I numeri non combaciano")
            return render_template('change_tel.html', vecchio_numero=old_number)
        with Session(engine) as s:
            stmt = (
                update(Utente)
                .where(Utente.user == usr)
                .values(contatto_tel = num1)
            )
            s.execute(stmt)
            s.commit()
        return render_template("success.html")

    else:
        return render_template('change_phone.html', vecchio_numero=old_number)
