from tkinter import *
import requests
from deep_translator import GoogleTranslator
import datetime

import sqlite3

###-------------- DATABASE SETUP --------------###

#conn = sqlite3.connect('DataBase.db')
#curseur = conn.cursor()

#curseur.execute("""CREATE TABLE IF NOT EXISTS questions (
#    id integer primary key autoincrement,
#    questionfr text,
#    questionen text,
#    correct_answerfr text,
#    correct_answeren text,
#    date_liste text,
#    amount integer
#)""")

#conn.close()


####-------------- DATABASE SETUP --------------###




# -- Global variables to store the correct answers
correct_answer_fr = ""
correct_answer_en = ""
question_id = ""
question_en = ""
question_fr = ""



# -- Function to fetch questions from the trivia API and display them


def get_questions(nb_questions):
    global question_en
    global question_fr
    global correct_answer_en
    global correct_answer_fr
    global question_id
    url = "https://the-trivia-api.com/v2/questions"
    difficulty = difficulty_var.get()
    print("Selected difficulty:", difficulty)
    params = {
        "limit": nb_questions,
        "difficulty": difficulty,
        "types": "text_choice",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        questions = response.json()
        for q in questions:
            question_en = q['question']
            correct_answer_en = q['correctAnswer']
            question_id = q['id']


            correct_answer_en = correct_answer_en.lower()
            question_clear = str(question_en).strip()
            correct_answer_clear = str(correct_answer_en).strip()

            question_clear = question_clear[10:len(question_clear) - 2]
            question_en = question_clear

            label_question.config(text="(EN) " + question_en)
            question_fr = GoogleTranslator(source='auto', target='fr').translate(question_clear)
            correct_answer_fr = GoogleTranslator(source='auto', target='fr').translate(correct_answer_clear)

            label_question_fr.config(text="(FR) " + question_fr)
            correct_answer_fr = correct_answer_fr.lower()

            entry_answer.delete(0, END)
            label_result.config(text="")
            entry_answer.pack(pady=5)

            submit_button.config(text="Validate", command=check_answer)
            submit_button.pack(pady=10)

            menu_frame.pack_forget()
            label_question.pack()
            label_question_fr.pack()
            label_result.pack()
    else:
        print(f"Error fetching questions: {response.status_code}")
        print(response.text)


# -- Function to check the user's answer and provide feedback


def check_answer(event=None):
    user_answer = entry_answer.get().strip().lower()
    if user_answer == correct_answer_fr or user_answer == correct_answer_en:
        label_result.config(text=f" Correct answer!( {correct_answer_en} / {correct_answer_fr} )")
    else:
        label_result.config(text=f" Wrong! The correct answer was: {correct_answer_en} / {correct_answer_fr}")


    datelist = datetime.datetime.today()

    if question_exists(question_id) == False:
        conn = sqlite3.connect('DataBase.db')
        curseur = conn.cursor()
        curseur.execute(
            "INSERT INTO questions (id, questionfr, questionen, correct_answerfr, correct_answeren, date_liste, amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (question_id, question_fr, question_en, correct_answer_fr, correct_answer_en, datelist.strftime("%Y-%m-%d"),
             1)
        )
        conn.commit()
        conn.close()
    else:
        datelist_str = datetime.datetime.today().strftime("%Y-%m-%d")
        conn = sqlite3.connect('DataBase.db')
        curseur = conn.cursor()

        curseur.execute("SELECT date_liste FROM questions WHERE id = ?", (question_id,))
        current_dates = curseur.fetchone()[0]

        dates = current_dates.split('||') if current_dates else []
        if datelist_str not in dates:
            dates.append(datelist_str)
        new_dates = '||'.join(dates)
        curseur.execute(
            "UPDATE questions SET amount = amount + 1, date_liste = ? WHERE id = ?",
            (new_dates, question_id)
        )
        conn.commit()
        conn.close()


    entry_answer.pack_forget()
    submit_button.config(text="Return to menu", command=return_to_menu)



def question_exists(question_id):
    conn = sqlite3.connect('DataBase.db')
    curseur = conn.cursor()
    curseur.execute("SELECT 1 FROM questions WHERE id = ?", (question_id,))
    exists = curseur.fetchone() is not None
    conn.close()
    return exists

def return_to_menu():
    label_question.pack_forget()
    label_question_fr.pack_forget()
    entry_answer.pack_forget()
    label_result.config(text="")
    submit_button.pack_forget()

    menu_frame.pack(pady=10)



window = Tk()
window.title("Teach me that!")
window.minsize(300, 200)

label_question = Label(window, text="", wraplength=400, font=("Arial", 14))
label_question_fr = Label(window, text="", wraplength=400, font=("Arial", 14))

entry_answer = Entry(window, font=("Arial", 12))
entry_answer.bind("<Return>", check_answer)

label_result = Label(window, text="", font=("Arial", 12))

submit_button = Button(window)

menu_frame = Frame(window)
menu_frame.pack(pady=10)

difficulty_var = StringVar()
difficulty_var.set("easy")

radio1 = Radiobutton(menu_frame, text="Easy", variable=difficulty_var, value="easy")
radio2 = Radiobutton(menu_frame, text="Medium", variable=difficulty_var, value="medium")
radio3 = Radiobutton(menu_frame, text="Hard", variable=difficulty_var, value="hard")

radio1.pack()
radio2.pack()
radio3.pack()

start_button = Button(menu_frame, text="Teach me that!", width=20, height=2, command=lambda: get_questions(1))
start_button.pack(pady=10)

submit_button.pack_forget()

window.mainloop()
