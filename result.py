from aleacult import *

if __name__ == "__main__":
    year, classement = bouton_magique()
    link = give_album_link(year,classement)
    print("Tu as tiré l\'album classé n°{} de l\'année {}".format(classement,year))
    print("voici le lien vers cet album :", link)