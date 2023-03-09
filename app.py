import os
from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from pymongo import response
from wtforms import StringField, DateField, SelectField, DecimalField
import requests, json


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(16).hex()
app.config["MONGO_URI"] = "mongodb+srv://steven:Ilovedenver303!@cluster0.rjmtwo5.mongodb.net/db?retryWrites=true&w=majority"
mongo = PyMongo(app)


class Expenses(FlaskForm):
    category = [
        ("rent","rent"),
        ("electricity", "electricity"),
        ("water", "water"),
        ("restaurants", "restaurants"),
        ("groceries", "groceries"),
        ("gas", "gas"),
        ("fun", "fun"),
        ("investments", "investments"),
        ("clothes", "clothes"),
        ("insurance", "insurance"),
        ("other", "other")
    ]

    currency = [
        ("USD", "USD"),
        ("USDEUR", "EUR"),
        ("USDGBP", "GBP"),
        ("USDCHF", "CHF"),
        ("USDKWD", "KWD"),
        ("USDBHD", "BHD")
    ]
    # TO BE COMPLETED (please delete the word pass above)
    # StringField for description
    description = StringField("description")
    # SelectField for category
    category = SelectField("category", choices=category)
    # DecimalField for cost
    cost = DecimalField("cost")
    # Currency StringField
    currency = SelectField("currency", choices=currency)
    # DateField for date
    date = DateField("date")

def get_total_expenses(category):
    # Access the database adding the cost of all documents of the category passed as input parameter
    # write the appropriate query to retrieve the cost
    cat_query = {'category': category}
    my_expenses = mongo.db.expenses.find(cat_query)
    cat_cost = 0
    for i in my_expenses:
        cat_cost += float(i["cost"])
    return cat_cost

""" ----------- I - JSON DOCUMENTS ----------- """
def save_to_file(data,filename):
    with open(filename,'w') as write_file:
        json.dump(data,write_file,indent=2)

def read_from_file(filename):
    with open(filename,'r') as read_file:
        data = json.load(read_file)
    return data


def currency_converter(cost,currency):
    api_key_dict = read_from_file('JSON_Files/api_key.json')
    key = api_key_dict["key"]
    url="https://api.apilayer.com/currency_data/live?apikey=" + key
    response = requests.get(url).json()
    ### YOUR TASK IS TO COMPLETE THIS FUNCTION
    save_to_file(response, "JSON_Files/currency.json")
    exchange = read_from_file("JSON_Files/currency.json")
    if currency != "USD":
        cost_query = {'cost': cost}
        find_cost = mongo.db.expenses.find(cost_query)
        currencyConvert = exchange["quotes"][currency]
        converted_cost = 0
        for i in find_cost:
            converted_cost = float(i["cost"]) * currencyConvert
            print(converted_cost)
        return converted_cost

    else:
        USD_cost = cost
        print(USD_cost)
    return USD_cost



@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost=0
    for i in my_expenses:
        total_cost += float(i["cost"])
    expensesByCategory = [
        ("rent", get_total_expenses("rent")),
        ("electricity", get_total_expenses("electricity")),
        ("water", get_total_expenses("water")),
        ("restaurants", get_total_expenses("restaurants")),
        ("groceries", get_total_expenses("groceries")),
        ("gas", get_total_expenses("gas")),
        ("fun", get_total_expenses("fun")),
        ("investments", get_total_expenses("investments")),
        ("clothes", get_total_expenses("clothes")),
        ("insurance", get_total_expenses("insurance")),
        ("other", get_total_expenses("other"))
        ]
    # expensesByCategory is a list of tuples
    # each tuple has two elements:
    ## a string containing the category label, for example, insurance
    ## the total cost of this category
    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)

@app.route('/addExpenses',methods=["GET","POST"])
def addExpenses():
    # INCLUDE THE FORM
    expensesForm = Expenses(request.form)
    if request.method == "POST":
        description = request.form['description']
        category = request.form['category']
        cost = request.form['cost']
        currency = request.form['currency']
        date = request.form['date']
        # INSERT ONE DOCUMENT TO THE DATABASE
        # CONTAINING THE DATA LOGGED BY THE USER
        # REMEMBER THAT IT SHOULD BE A PYTHON DICTIONARY
        # expenses = [{'description': 'sushi','category': 'groceries','cost': 3, 'date': "11/14/2022"}]
        # mongo.db.expenses.insert_many(expenses)
        cost = currency_converter(cost,currency)
        mongo.db.expenses.insert_one({'description': description, 'category': category, 'cost': cost, 'currency': currency, 'date': date})
        return render_template("expenseAdded.html")
    return render_template("addExpenses.html",form=expensesForm)
app.run()