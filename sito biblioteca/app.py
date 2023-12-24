from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = 'uploads'

# funzione per controllare le credenziali
def check_credentials(filename, username, password):
    with open(filename, 'r') as f:
        for line in f:
            # split the line into username and password
            line_parts = line.strip().split(',')
            if len(line_parts) == 2:
                file_username = line_parts[0]
                file_password = line_parts[1]

                # check if the username and password match
                if username == file_username and password == file_password:
                    return True

    # if no matching username and password were found, return False
    return False


@app.route('/about')
def about():
    return render_template('info.html')

@app.route('/registrazione')
def registrazione():
    return render_template('registrazione.html')


@app.route('/')
def index():
    try:
        # legge i dati dei libri dal file "book.txt"
        with open('file/book.txt', 'r') as f:
            books = f.readlines()

        # crea una lista di dizionari contenente i dati dei libri
        book_list = []
        for book in books:
            book_parts = book.strip().split(',')
            if len(book_parts) >= 3:  # controlla che ci siano almeno 3 elementi (titolo, autore, copertina)
                book_dict = {
                'title': book_parts[0],
                'author': book_parts[1],
                'cover': book_parts[2].strip(),
                'file_path': book_parts[3].strip()
                }
                book_list.append(book_dict)

        return render_template('index.html', book_list=book_list, logged_in=session.get('logged_in'))

    except Exception as e:
        error_message = f"Si è verificato un errore: {str(e)}"
        return render_template("error.html", error_message=error_message)

@app.route('/registrati', methods=['POST'])
def registrati():
    # recupera i valori inseriti dall'utente nel form
    username = request.form['username']
    password = request.form['password']

    # scrive le credenziali nel file "accessi.txt"
    with open('file/accessi.txt', 'a') as f:
        f.write(f"{username},{password}\n")

    # mostra un messaggio di successo e reindirizza l'utente alla pagina di login
    flash('Registrazione avvenuta con successo! Effettua il login per accedere.')
    return redirect(url_for('form'))

@app.route('/form')
def form():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('form.html')

@app.route('/accesso')
def accesso():
    return render_template('accesso.html')

@app.route('/check-login', methods=['POST'])
def check_login():
    # recupera i valori inseriti dall'utente
    username = request.form['username']
    password = request.form['password']

    # controlla le credenziali
    if check_credentials('file/accessi.txt', username, password):
        # se le credenziali sono corrette, imposta la sessione dell'utente come autenticata
        session['logged_in'] = True
        # reindirizza l'utente alla pagina "form"
        return redirect(url_for('form'))
    else:
        # altrimenti, reindirizza l'utente alla pagina "accesso" e mostra un messaggio di errore
        flash('Credenziali non valide, riprova.')
        return redirect(url_for('accesso'))

@app.route('/delete-book', methods=['POST'])
def delete_book():
    # recupera il titolo del libro da eliminare dal form
    title = request.form['title']

    # controlla se il file "book.txt" esiste
    if not os.path.isfile('file/book.txt'):
        message = "Errore: il file 'book.txt' non esiste."
        return jsonify({'message': message, 'redirect': url_for('form')})

    # legge i dati dei libri dal file "book.txt"
    with open('file/book.txt', 'r') as f:
        books = f.readlines()

    # cerca il libro da eliminare
    book_index = None
    for i, book in enumerate(books):
        book_parts = book.strip().split(',')
        if book_parts[0] == title:
            book_index = i
            break

    # se il libro è stato trovato, lo elimina dalla lista dei libri
    if book_index is not None:
        del books[book_index]

        # scrive la lista aggiornata dei libri nel file "book.txt"
        with open('file/book.txt', 'w') as f:
            f.writelines(books)

        # crea un messaggio di successo da mostrare in un alert
        message = f"Il libro '{title}' è stato eliminato."
        return jsonify({'message': message})
    else:
        # crea un messaggio di errore da mostrare in un alert
        message = f"Non è stato trovato nessun libro con il titolo '{title}'."
        return jsonify({'message': message, 'redirect': url_for('form')})


@app.route('/logout')
def logout():
    # rimuove la chiave 'logged_in' dalla sessione
    session.pop('logged_in', None)
    # reindirizza l'utente alla pagina principale
    return redirect(url_for('form'))

@app.route('/users')
def users_page():
    return render_template('users.html')

 
    


@app.route('/add-book', methods=['POST'])
def add_book():
    try:
        # recupera i valori inseriti dall'utente nel form
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        cover_file = request.files['cover']

        # salva il file dell'immagine di copertina nella cartella "uploads"
        filename = secure_filename(cover_file.filename)
        cover_file.save(os.path.join('uploads', filename))

        # crea il dizionario del libro
        book_dict = {
            'title': title,
            'author': author,
            'isbn': isbn,
            'cover': os.path.join('uploads', filename)
        }

        # scrive il dizionario del libro nel file "book.txt"
        with open('file/book.txt', 'a') as f:
            f.write(f"{book_dict['title']},{book_dict['author']},{book_dict['isbn']},{book_dict['cover']}\n")

        # reindirizza l'utente alla pagina principale
        return redirect(url_for('form'))

    except Exception as e:
        error_message = f"Si è verificato un errore durante l'aggiunta del libro: {str(e)}"
        return render_template("error.html", error_message=error_message)
    
from flask import Flask, send_file

@app.route('/books/<int:book_id>/download')
def download_book1(book_id):
    # Ottiene la lista dei libri dal file "book.txt"
    with open('file/book.txt', 'r') as f:
        books = f.readlines()

    # Ottiene il percorso del file del libro dalla lista dei libri
    book_parts = books[book_id-1].strip().split(',')
    file_path = book_parts[3].strip()

    # Invia il file al client come allegato
    return send_file(file_path, as_attachment=True)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)