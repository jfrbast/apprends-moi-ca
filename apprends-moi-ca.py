from tkinter import *
import requests
from deep_translator import GoogleTranslator
import datetime
import sqlite3

# -- Variables globales pour stocker les réponses correctes
correct_answer_fr = ""
correct_answer_en = ""
question_id = ""
question_en = ""
question_fr = ""

def get_questions(nb_questions):
    global question_en
    global question_fr
    global correct_answer_en
    global correct_answer_fr
    global question_id
    url = "https://the-trivia-api.com/v2/questions"
    difficulty = difficulty_var.get()

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
            entry_answer.pack(pady=10)

            submit_button.config(text="Valider", command=check_answer)
            submit_button.pack(pady=15)

            menu_frame.pack_forget()
            label_question.pack(pady=10)
            label_question_fr.pack(pady=10)
            label_result.pack(pady=10)
    else:
        print(f"Error fetching questions: {response.status_code}")
        print(response.text)

def check_answer(event=None):
    user_answer = entry_answer.get().strip().lower()
    if user_answer == correct_answer_fr or user_answer == correct_answer_en:
        label_result.config(text=f"✅ Bonne réponse ! ({correct_answer_en} / {correct_answer_fr})", fg="#4F996D")
    else:
        label_result.config(text=f"❌ Mauvaise réponse ! La bonne réponse était : {correct_answer_en} / {correct_answer_fr}", fg="#EE2449")

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
    submit_button.config(text="Retour au menu", command=return_to_menu)

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
    menu_frame.pack(pady=20)

# --- Interface graphique stylée ---
window = Tk()
window.title("Apprends-moi ça !")
window.minsize(400, 300)
window.configure(bg="#242321")

label_question = Label(window, text="", wraplength=400, font=("Arial", 15, "bold"), bg="#242321", fg="#FFFAE8")

label_question_fr = Label(window, text="", wraplength=400, font=("Arial", 15, "bold"), bg="#242321", fg="#B8CBD0")

entry_answer = Entry(window, font=("Arial", 13), bg="#e3f2fd", fg="#1a237e", relief=GROOVE, bd=2, justify="center")
entry_answer.bind("<Return>", check_answer)

label_result = Label(window, text="", font=("Arial", 13, "bold"), bg="#242321")

submit_button = Button(window, font=("Arial", 12, "bold"), bg="#4F996D", fg="white", activebackground="#2E714A", activeforeground="white", relief=RAISED, bd=3, cursor="hand2")

menu_frame = Frame(window, bg="#242321")
menu_frame.pack(pady=20)

difficulty_var = StringVar()
difficulty_var.set("easy")

Label(menu_frame, text="Bienvenue dans Apprends-moi ça !", font=("Arial", 18, "bold"), bg="#242321", fg="#FFFAE8").pack(pady=10)
Label(menu_frame, text="Choisis la difficulté :", font=("Arial", 14, "bold"), bg="#242321", fg="#C9C1B4").pack(pady=10)

radio1 = Radiobutton(menu_frame, text="Facile", variable=difficulty_var, value="easy", font=("Arial", 12), bg="#242321", fg="#4F996D", selectcolor="#000000", activebackground="#242321")
radio2 = Radiobutton(menu_frame, text="Moyen", variable=difficulty_var, value="medium", font=("Arial", 12), bg="#242321", fg="#fbc02d", selectcolor="#000000", activebackground="#242321")
radio3 = Radiobutton(menu_frame, text="Difficile", variable=difficulty_var, value="hard", font=("Arial", 12), bg="#242321", fg="#9F0328", selectcolor="#000000", activebackground="#242321")

radio1.pack(pady=2)
radio2.pack(pady=2)
radio3.pack(pady=2)

start_button = Button(menu_frame, text="Apprends-moi ça !", width=22, height=2, font=("Arial", 13, "bold"), bg="#4F996D", fg="white", activebackground="#2E714A", activeforeground="white", relief=RAISED, bd=3, cursor="hand2", command=lambda: get_questions(1))
start_button.pack(pady=15)

submit_button.pack_forget()

window.mainloop()