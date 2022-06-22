from flask import Flask,render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import helpers
import datetime

import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json


app = Flask(__name__)
#app.secret_key = "Secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/app_382P'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Banks(db.Model):
    __tablename__ = 'banks'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    tests = db.relationship('Tests', backref='banks')

    def __init__(self, name):
        self.name = name

class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(10000))
    group_id = db.Column(db.Integer)
    tests = db.relationship('Tests', backref='questions')

    def __init__(self, name, group_id):
        self.name = name
        self.group_id = group_id


class Recommendations(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(10000))
    group_id = db.Column(db.Integer)


    def __init__(self, name, group_id):
        self.name = name
        self.group_id = group_id


class Tests(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key = True)
    answer = db.Column(db.Float())
    question_id = db.Column(db.Integer(), db.ForeignKey('questions.id'))
    bank_id = db.Column(db.Integer(), db.ForeignKey('banks.id'))
    created_date = db.Column(db.Date, default=datetime.date.today().strftime("%d.%m.%Y"))

    def __init__(self, answer, question_id, bank_id):
        self.answer = answer
        self.question_id = question_id
        self.bank_id = bank_id


class Results(db.Model):
    __tablename__ = 'results'
    bank_id = db.Column(db.Integer())
    created_date = db.Column(db.Date)
    results = db.Column(db.String(10000))

    def __init__(self, bank_id, created_date, results):
        self.bank_id = bank_id
        self.created_date = created_date
        self.results = results



@app.route('/', methods=['GET'])
def main():
    banks = Banks.query.all()
    rate = helpers.find_rates()
    return render_template("index.html", banks=banks, data=rate)


@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        my_data = Banks(name)
        db.session.add(my_data)
        db.session.commit()
        return redirect(url_for('main'))


@app.route('/update', methods = ['GET', 'POST'])
def update():
    if request.method == 'POST':
        my_data = Banks.query.get(request.form.get('id'))
        my_data.name = request.form['name']
        db.session.commit()
        return redirect(url_for('main'))


@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = Banks.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    return redirect(url_for('main'))



@app.route('/tests/<id>', methods = ['GET'])
def tests(id):
    all_questions = Questions.query.all()
    my_data = Banks.query.get(id)
    return render_template("tests.html", questions=all_questions, banks=my_data)


@app.route('/answers_banks', methods = ['GET', 'POST'])
def answers_banks():
    if request.method == 'POST':
        id = request.form['id']
        list_ = [request.form[f'answer{i}'] for i in range(1,168)]
        tests_from_banks = Tests.query.filter(Tests.created_date == datetime.date.today().strftime("%d.%m.%Y"), Tests.bank_id == id).all()
        print(tests_from_banks)
        if tests_from_banks is None:
            print("first")
            for i in range(len(list_)):
                my_data = Tests(list_[i], i + 1, id)
                db.session.add(my_data)
            # расчитываем оценку
            #res = helpers.find_rates()
            #my_data = Results(res[])
            #db.session.add(my_data)
        else:
            print("second")
            for element in tests_from_banks:
                db.session.delete(element)
            db.session.commit()
            for i in range(len(list_)):
                my_data = Tests(list_[i], i + 1, id)
                db.session.add(my_data)
        db.session.commit()

        return "Оценка успешно выполнена!"


@app.route('/back', methods = ['GET'])
def back():
    return redirect(url_for('main'))


@app.route('/plot/<id>', methods = ['GET'])
def plot(id):
    my_data = Banks.query.get(id)

    bar = create_plot(id)
    return render_template("plot.html", plot=bar, banks=my_data)



def create_plot(id):
    labels = []
    n_o = []
    answer_0 = []
    answer_025 = []
    answer_05 = []
    answer_075 = []
    answer_1 = []
    bank = Banks.query.get(id)
    data_from_bank = helpers.find_test_from_banks()
    for bank_element, info in data_from_bank.items():
        if bank_element.id == bank.id:
            for data_info, tests_info in info.items():
                labels.append(data_info)
                for i,j in tests_info.items():
                    if i == -1:
                        n_o.append(j)
                    if i == 0:
                        answer_0.append(j)
                    if i == 0.25:
                        answer_025.append(j)
                    if i == 0.5:
                        answer_05.append(j)
                    if i == 0.75:
                        answer_075.append(j)
                    if i == 1:
                        answer_1.append(j)

    data_1 = {
        "Н/О": n_o,
        "0": answer_0,
        "0.25": answer_025,
        "0.5": answer_05,
        "0.75": answer_075,
        "1": answer_1,
        "labels": labels
    }
    data=[
        go.Bar(
            name="Н/О",
            x=data_1["labels"],
            y=data_1["Н/О"],
            offsetgroup=0,
        ),
        go.Bar(
            name="0",
            x=data_1["labels"],
            y=data_1["0"],
            offsetgroup=1,
            #marker_color='red'
        ),
        go.Bar(
            name="0.25",
            x=data_1["labels"],
            y=data_1["0.25"],
            offsetgroup=2
        ),
        go.Bar(
            name="0.5",
            x=data_1["labels"],
            y=data_1["0.5"],
            offsetgroup=3
        ),
        go.Bar(
            name="0.75",
            x=data_1["labels"],
            y=data_1["0.75"],
            offsetgroup=4
        ),
        go.Bar(
            name="1",
            x=data_1["labels"],
            y=data_1["1"],
            offsetgroup=5
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/recomendations/<id>/<date>', methods = ['GET'])
def recomendations(id, date):
    my_data = Banks.query.get(id)
    str_ = ["", "", "", "", "", "", "", ""]
    list__ = []
    ff = Recommendations.query.all()
    for i in ff:
        list__.append(i.name)
    recomendations_for_banks = {}
    tests_from_banks_group_1 = Tests.query.filter(Tests.created_date == date, Tests.bank_id == id).filter((Tests.answer == 0) | (Tests.answer == 0.25)).all()
    for element in tests_from_banks_group_1:
        if (element.question_id in [1,2,3,4,5,6,7]):
            recomendations_for_banks['Защита информации при назначении и распределении ролей'] = list__[0]
        if (element.question_id in list(range(8,27))):
            recomendations_for_banks['Защита информации на этапах жизненного цикла'] = list__[1]
        if (element.question_id in list(range(27,51))):
            recomendations_for_banks['Защита информации при доступе к объектам информационной инфраструктуры'] = list__[2]
        if (element.question_id in list(range(51,63))):
            recomendations_for_banks['Защита информации от вредоносного кода'] = list__[3]
        if (element.question_id in list(range(63,79))):
            recomendations_for_banks['Защита информации при использовании Интернет'] = list__[4]
        if (element.question_id in list(range(79,92))):
            recomendations_for_banks['Защита информации с использованием СКЗИ'] = list__[5]
        if (element.question_id in list(range(92,105))):
            recomendations_for_banks['Технологические меры защиты информации'] = list__[6]
        if (element.question_id in list(range(105,116))):
            recomendations_for_banks['Требования к Службе ИБ банка'] = list__[7]
        if (element.question_id in list(range(116,120))):
            recomendations_for_banks['Повышение осведомленности в области ИБ'] = list__[8]
        if (element.question_id in list(range(120,132))):
            recomendations_for_banks['Выявление и реагирование на инциденты'] = list__[9]
        if (element.question_id in list(range(132,138))):
            recomendations_for_banks['Требования к ЗИ при переводах'] = list__[10]
        if (element.question_id == 138):
            recomendations_for_banks['Оценка выполнения требований к ЗИ при переводах'] = list__[11]
        if (element.question_id in list(range(139,146))):
            recomendations_for_banks['Отчетность перед ОПС за ЗИ при переводах'] = list__[12]
        if (element.question_id in list(range(146,155))):
            recomendations_for_banks['Совершенствование системы ЗИ при переводах'] = list__[13]
        if (element.question_id in list(range(155,168))):
            recomendations_for_banks['Защита информации банкоматов и терминалов, пластиковые карты'] = list__[14]
    return render_template("recomendations.html", banks=my_data, data_for_table=recomendations_for_banks)


if __name__ == "__main__":
    db.create_all()
    app.run(threaded=True, debug=True)