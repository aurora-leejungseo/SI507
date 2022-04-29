####################################################
############# MY UNIQUE NAME: jungseo ##############
####################################################


####################################################
# importing packages ###############################
####################################################
import secret
import requests
import sqlite3
from flask import Flask, render_template, Markup
from collections import defaultdict
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from plotly.offline import plot 
from collections import Counter

# Application configurations ############################
app = Flask(__name__)
app.debug = False
app.use_reloader = True


#########################################################
# API ###################################################
#########################################################

# Access API    #########################################
def get_filtered_data(city, category, price):
    '''
    Description:

    Get data with importing API_key and authentification and save this in json
    ----------------------------------------------------------
    Parameters:

    city(str): name of the city from the user input
    category(str): user's preferred category
    price(int): level of the price range from the user input

    ----------------------------------------------------------
    Returns:
    result(json)

    '''
    base_url = "https://api.yelp.com/v3/businesses/search"

    # getting user input

    location = city
    category = category
    price = price
    limit = 50      # returns 50 results

    # parameter setting
    params = {'location': location}
    if category != 'n/a':
        params['categories'] = category
    if price != 'n/a':
        params['price'] = int(price)
    params['limit'] = limit

    # access to API
    API_Key = secret.API_key
    auth = {'Authorization': 'Bearer ' + API_Key}
    response = requests.get(base_url, params=params, headers=auth)

    # get the response in a json format
    result = response.json()

    return  result


def get_all_data(city):
    '''
    Description:

    Get data with importing API_key and authentification and save this in json
    ----------------------------------------------------------
    Parameters:

    city(str): name of the city

    ----------------------------------------------------------
    Returns:
    result(json)

    '''
    base_url = "https://api.yelp.com/v3/businesses/search"

    # getting user input

    location = city
    limit = 50      # returns 50 results

    # parameter setting
    params = {'location': location, 'limit': limit}

    # access to API
    API_Key = secret.API_key
    auth = {'Authorization': 'Bearer ' + API_Key}
    response = requests.get(base_url, params=params, headers=auth)

    # get the response in a json format
    result = response.json()

    return  result


#########################################################
# DB ####################################################
#########################################################

# save data into the database ###########################
def into_db(data):
    '''
    Description:

    Function to save search result into the database named "restaurants"
    ----------------------------------------------------------
    Parameters:

    data(dict): json 

    ----------------------------------------------------------
    Returns:
    None

    '''
    # connection object to interact with SQLite db, this will automatically create a db if it doesn't exist in the folder
    connection = sqlite3.connect("restaurants.db")

    # create tables in the db: state, city, restaurant, review
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE TABLE state (state TEXT, UNIQUE(state))")    # unique: state
        cursor.execute("CREATE TABLE city (city_name TEXT, state TEXT, area_code INTEGER, UNIQUE(area_code))")  # unique: area_code
        cursor.execute("CREATE TABLE restaurant (name TEXT, categories TEXT, rating FLOAT, price INT, city TEXT, state TEXT, address TEXT, phone TEXT, url TEXT, UNIQUE(address))")  # unique: address
        cursor.execute("CREATE TABLE review (review TEXT, rating FLOAT)")
    except:
        pass

    # insert values into the database
    # state:
    for each in data['businesses']:
        location = each['location']
        cursor.execute("INSERT OR IGNORE INTO state VALUES(?)", [location['state']])
        connection.commit()

    # city:
    for each in data['businesses']:
        location = each['location']
        area_code = each['phone'][0:4]
        cursor.execute("INSERT OR IGNORE INTO city VALUES (?, ?, ?)", [location['city'],location['state'], area_code])
        connection.commit()

    # restaurants:
    for each in data['businesses']:
        try:
            name = each['name']
            categories = []
            for category in each['categories']:
                categories.append(category['title'])    # get all the categories
            categories = ', '.join(categories)
            rating = each['rating']
            price = len(each['price'])
            city = each['location']['city']
            state = each['location']['state']
            address = ' '.join(each['location']['display_address'])
            phone = each['phone']
            url = each['url']
            cursor.execute("INSERT OR IGNORE INTO restaurant VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [name, categories, rating, price, city, state, address, phone, url])
            connection.commit()
        except:
            continue

def get_query(city, category, price):
    '''
    Description:

    Function to get data from the database named "restaurants"
    ----------------------------------------------------------
    Parameters:

    city(str): name of the city
    category(str): category of the food
    price(int): level of price range (1-4)
    data_type(str): get which data from the db (all, filtered)
    cursor: access point to the database

    ----------------------------------------------------------
    Returns:
    results

    '''
    city = city
    category = category
    price = price

    if (category == 'n/a') and (category == 'n/a'):
        query = '''SELECT * FROM restaurant WHERE city ="{}"'''.format(city)
    elif (category != 'n/a') and (price != 'n/a'):
        query = '''SELECT * FROM restaurant WHERE city ="{}" AND categories LIKE "%{}%" AND price LIKE {}'''.format(city, category, price)
    elif (category != 'n/a') and (price == 'n/a'):
        query = '''SELECT * FROM restaurant WHERE city ="{}" AND categories LIKE "%{}%"'''.format(city, category)
    elif (category == 'n/a') and (price != 'n/a'):
        query = '''SELECT * FROM restaurant WHERE city ="{}" AND price LIKE {}'''.format(city, price)
    
    return query

def get_data(query):
    connection = sqlite3.connect('restaurants.db')
    cursor = connection.cursor()
    result = cursor.execute(query).fetchall()
    connection.close()
    return result

#########################################################
# Data Preproccessing ###################################
#########################################################

# number of restaurants by price range ##################
def num_res_by_price(json_result):
    '''
    Description:

    Function that counts number of restaurants by price range
    ----------------------------------------------------------
    Parameters:

    json_result(dict): json_result from the API

    ----------------------------------------------------------
    Returns:
    dictionary of {price range: number of restaurants}

    '''
    json_result = json_result['businesses']
    price_num = defaultdict(int)
    for restaurant in json_result:
        try:
            price = restaurant['price']
            price_num[price] += 1
        except:
            continue
    return price_num

# number of restaurants by cateogry #####################
def num_res_by_category(json_result):
    '''
    Description:

    Function that counts number of restaurants by category
    ----------------------------------------------------------
    Parameters:

    json_result(dict): json_result from the API

    ----------------------------------------------------------
    Returns:
    dictionary of {category: number of restaurants}

    '''
    json_result = json_result['businesses']
    category_num = defaultdict(int)
    for restaurant in json_result:
        try:
            categories = restaurant['categories']
            for category in categories:
                category = category['title']
                category_num[category] += 1
        except:
            continue
    category_num = dict(Counter(category_num).most_common(10))
    return category_num

# number of restaurants by rating #####################
def num_res_by_rating(json_result):
    '''
    Description:

    Function that counts number of restaurants by rating
    ----------------------------------------------------------
    Parameters:

    json_result(dict): json_result from the API

    ----------------------------------------------------------
    Returns:
    dictionary of {category: number of restaurants}

    '''
    json_result = json_result['businesses']
    rating_num = defaultdict(int)
    for restaurant in json_result:
        try:
            rating= restaurant['rating']
            rating_num[rating] += 1
        except:
            continue
    return rating_num

# show the word frequencies from the reviews #############



#########################################################
# Flask Graph Design ####################################
#########################################################

# plot figure on the web browser via flask ##############
def plot_chart(x, y, plot_type):
    '''
    Description:

    Function that counts number of restaurants by category
    ----------------------------------------------------------
    Parameters:

    x(list): list of x values
    y(list): list of y values
    plot_name(string): name of the plot
    plot_type(string): plot type (pie, bar, histogram)

    ----------------------------------------------------------
    Returns:
    plotted_chart

    '''
    fig = make_subplots (rows=1, cols=1, specs=[[{'type':plot_type}]])
    if plot_type == 'pie':
        fig.add_trace(go.Pie(labels=x, values=y), row=1, col=1)
        fig.update_traces(opacity=0.8, hoverinfo = "all")
    elif plot_type == 'bar':
        fig.add_trace(go.Bar(x=x, y=y), row=1, col=1)
    plotted_chart = plot(fig, output_type='div')
    return plotted_chart

# pieplot ###############################################
def pie_bar_plot(dictionary, plot_type):
    '''
    Description:

    Plots pie chart for showing distribution of price, category,rating
    ----------------------------------------------------------
    Parameters:

    dictionary (dict): {price/category/rating: number of restaurant}
    plot_type(string): pie, bar

    ----------------------------------------------------------
    Returns:
    plot(labels, values, title, 'pie'/'bar')
    '''
    labels = list(dictionary.keys())
    values = list(dictionary.values())

    if plot_type == 'bar':
        return plot_chart(labels, values, 'bar')
    else:
        return plot_chart(labels, values, 'pie')
#########################################################
# Flask Web Design ######################################
#########################################################

# home route ############################################
@app.route('/')
def home():
    # getting relavant data from db
    return render_template('home.html',city=city)

@app.route('/plot/<city>/<by_what>')
def plotting(city, by_what):
    if by_what == 'price':
        num_res = num_res_by_price(all_result)
        figure = pie_bar_plot(num_res, 'pie')
    elif by_what == 'category':
        num_res = num_res_by_category(all_result)
        figure = pie_bar_plot(num_res, 'pie')
    elif by_what == 'rating':
        num_res = num_res_by_rating(all_result)
        figure = pie_bar_plot(num_res, 'bar')

    return render_template('plot.html', figure=Markup(figure), by_what=by_what, city=city)

@app.route('/recommendations')
def recommendation():
    table = []
    for comp in data:
        row = []
        row.append(comp[0])
        row.append(comp[1])
        row.append(comp[2])
        row.append(comp[3])
        row.append(comp[6])
        row.append(comp[7])
        row.append(comp[8])
        table.append(row)

    return render_template('list.html', data=data, table=table)






#########################################################
# Main Function #########################################
#########################################################
if __name__ == '__main__':
    print('------------------------------------------------------------------------')
    city = input("Type in the name of the the geographical area you want to search for your resraurant recommendations: ")
    category = input("Which food are you craving for? (Optional. If you want to skip this question, just type 'n/a'): ")
    price = input("If you want to filter out the restaurants by price, please indicate the level of pricing in a scale of 1-4 (Optional. If you want to skip this question, just type 'n/a'): ")
    all_result = get_all_data(city)
    filtered_result = get_filtered_data(city, category, price)
    # change city name matching with the name in the database
    city = all_result['businesses'][0]['location']['city']
    #save data into the database
    connection = sqlite3.connect("restaurants.db")
    into_db(all_result)
    into_db(filtered_result)
    #get data from the database
    query = get_query(city, category, price)
    data = get_data(query)
    print('------------------------------------------------------------------------')
    #print(all_result)
    app.run()