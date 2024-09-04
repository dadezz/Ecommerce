from sqlalchemy import URL,create_engine,func,and_,select,  Table, MetaData
from sqlalchemy.ext.automap import automap_base

"""
sqlclass.py è la pagina in cui vengono caricate le tabelle e ci si connette al DB
"""

# Usa l'engine che hai già creato
url_code = URL.create(
    drivername="postgresql",
    username="utente",
    password="password",
    host="localhost",
    port=5432,
    database="Ecommerce"
)
engine = create_engine(url=url_code,echo=False)
Base = automap_base()
Base.prepare(autoload_with=engine)

# è una vista
metadata = MetaData()
prodotti_disponibili = Table(
    'prodotti_disponibili',
    metadata,
    autoload_with=engine
)

# carica le tabelle
Utente = Base.classes['Utenti']
Prodotti = Base.classes['Prodotti']
Carrello = Base.classes['Carrello']
Recensioni = Base.classes['Recensioni']
ProdottiRecensioni = Base.classes['ProdottiRecensioni']
ProdottiCarrelli = Base.classes['ProdottiCarrelli']
CarrelloUtenti = Base.classes['CarrelloUtenti']
ProdottiStorici = Base.classes['ProdottiStorici']
Storico = Base.classes['Storico']