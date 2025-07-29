from tkinter import *
import requests
from deep_translator import GoogleTranslator

# -- Global variables to store the correct answers
correct_answer_fr = ""
correct_answer_en = ""


# -- Function to fetch questions from the trivia API and display them


def get_questions(nb_questions):
    global correct_answer_en
    global correct_answer_fr
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
        label_result.config(text=" Correct answer!")
    else:
        label_result.config(text=f" Wrong! The correct answer was: {correct_answer_en} / {correct_answer_fr}")

    submit_button.config(text="Return to menu", command=return_to_menu)


# -- Function to return to the main menu and reset the interface


def return_to_menu():
    label_question.pack_forget()
    label_question_fr.pack_forget()
    entry_answer.pack_forget()
    label_result.config(text="")
    submit_button.pack_forget()

    menu_frame.pack(pady=10)


# -- Main application setup


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


