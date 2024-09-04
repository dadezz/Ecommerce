# Ecommerce
Web application che simula un ecommerce. Ispirata principalmente a subito.it. Grafica minimale, focus sul backend.
## Linguaggi 
Frontend scritto con template html-css minimali con due funzioni in javascript; backend scritto in python, col framework Flask e Flask-login per interfacciarsi col frontend, e col framework sqlalchemy per interfacciarsi col database. Per quest'ultimo abbiamo usato PostgreSQL
## Installazione e avvio
### Creazione del database
Creare in postgre un database vuoto di nome Ecommerce (usare l'applicativo pgadmin4 per semplicità). NB questo punto è importante. se modificate, è da cambiare anche il corrispondente nome nel file `src/sqlclass.py` a riga 15. Da riga di comando, accedere con l'account postgres e digitare questo comando  
```bash
psql -h your_host -p your_port -U your_user -d your_name -f "/your_path/Ecommerce/dump.sql"
```  
`your_host` tipicamente è `localhost` per farlo girare in locale  
`your_port` di default è 5432  
`your_user` di default è postgres  
`your_name` è il nome del database precedentemente creato. Nel nostro caso, Ecommerce
### requirements python
Nel file requirements.txt si trovano le librerie usate. per installarle, lanciare da terminale:  
```bash
pip install -r requirements.txt
```  
può essere sia necessaria la creazione di un virtual environment  
```bash
cd Ecommerce
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```  
È comunque sempre consigliato usare un ambiente virtuale per ogni progetto per evitare conflitti tra versioni di pacchetti.
### avvio
Da terminale, per avviare l'app spostarsi sulla cartella principale `Ecommerce` e lanciare semplicemente  
```bash
python3 ./src/app.py
```  
Notare che è necessaria l'attivazione del virtual environment, se esso esiste e non è già attivato
## Dettagli della webapp
Consultare "Relazione.pdf"
### Dati precaricati
Sono stati inseriti alcuni prodotti di esempio:  
* un annuncio con 5 foto 
* un annuncio con tante recensioni
* un annuncio con disponibilità 0 (quindi non visibile in homepage)
l'unico account creato, per testare il funzionamento, ha nome utente "username" e password "password"
