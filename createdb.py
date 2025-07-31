import sqlite3

###-------------- DATABASE SETUP --------------###

conn = sqlite3.connect('DataBase.db')
curseur = conn.cursor()

curseur.execute("""CREATE TABLE IF NOT EXISTS questions (
    id primary key,
    questionfr text,
    questionen text,
    correct_answerfr text,
    correct_answeren text,
    date_liste text,
    amount integer
)""")

conn.close()
