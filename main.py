from flask import Flask
from aleacult import bouton_magique,give_album_link

app = Flask(__name__)

@app.route("/")
def index():
    year, classement = bouton_magique()
    link = give_album_link(year,classement)
    return (
        "<p>Voici l\'album classé n°{} de l\'année {}".format(classement,year)
        + "\n <p>Voici le lien vers cet album :"
        + "<a href={}>lien fiche sens critique".format(str(link)))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)