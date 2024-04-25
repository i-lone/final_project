import psycopg2
import secrets
import string
import random
import csv
import requests


username_adj_pull = ["Little", "Big", "Sunny", "Top", "Loony", "Sugar", "Ghostly", "Happy", "Sad", "Funky", "Cyber",
                     "Dreamy", "Meek", "Grand", "Green", "Red", "Pink", "Blue", "Neon", "White", "Black", "Gray",
                     "Solemn", "Yellow", "Lavender", "Skycleaving", "Amazing", "Girly", "Manly", "Flying", "IT",
                     "Genius", "Almighty", "Mint", "Gold", "Cooper", "Iron", "Hot", "Bright", "Brave", "Solemn", "Rich",
                     "Poor", "Charming", "Clever", "Calm", "Cool", "Cheerful", "Fiery", "Busy", "Cautious", "Curt",
                     "Fair", "Pretty", "Handsome", "Chubby", "Dear", "Honey", "Cruel", "Nutty", "Wicked", "Tiny",
                     "Small", "Frail", "Fancy", "Naughty"]

cities = ["Kyiv", "Poltava", "Lviv", "Kherson", "Odesa", "Zhytomyr", "Ternopil", "Ivano-Frankivsk"]

USER_URL = ""

BOOK_URL = ""


def database_credentials():
    return psycopg2.connect(database="project_users",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")


def create_tables():
    conn = database_credentials()

    table_users = "users"
    table_books = "books"

    cursor = conn.cursor()

    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_users))
    if not (bool(cursor.rowcount)):
        print(f'No table ${table_users}. Creating table')
        cursor.execute("CREATE TABLE {0} ("
                       "id SERIAL PRIMARY KEY,"
                       "username VARCHAR(45),"
                       "password VARCHAR(25))".format(table_users))

    cursor.execute("select * from information_schema.tables where table_name = '{0}'".format(table_books))
    if not (bool(cursor.rowcount)):
        print(f'No table ${table_books}. Creating table')
        cursor.execute("CREATE TABLE {0} ("
                       "id SERIAL PRIMARY KEY,"
                       "title VARCHAR(250),"
                       "author VARCHAR(150),"
                       "year int,"
                       "publisher VARCHAR(100),"
                       "city VARCHAR(20),"
                       "reserved_by int REFERENCES users(id))".format(table_books))

    conn.commit()
    cursor.close()
    conn.close()


def generate_username(username_noun_pull, len_noun, len_adj):
    number = random.randint(0, 6)
    username = ""
    match number:
        case 0:
            rand_adj = random.randint(0, (len_adj - 1))
            rand_noun = random.randint(0, (len_noun - 1))
            rand_num = random.randint(0, 999999)
            username = (username_adj_pull[rand_adj].capitalize() + username_noun_pull[rand_noun].capitalize() +
                        str(rand_num))
        case 1:
            rand_adj = random.randint(0, (len_adj - 1))
            rand_noun = random.randint(0, (len_noun - 1))
            rand_num = random.randint(0, 999999)
            username = (username_adj_pull[rand_adj].capitalize() + "_" + username_noun_pull[rand_noun].capitalize() +
                        str(rand_num))
        case 2:
            rand_adj = random.randint(0, (len_adj - 1))
            rand_noun = random.randint(0, (len_noun - 1))
            rand_num = random.randint(0, 999999)
            username = (username_adj_pull[rand_adj].capitalize() + "_" + username_noun_pull[rand_noun].capitalize() +
                        "_" + str(rand_num))
        case 3:
            rand_adj = random.randint(0, (len_adj - 1))
            rand_noun = random.randint(0, (len_noun - 1))
            rand_num = random.randint(0, 999999)
            username = (username_adj_pull[rand_adj].capitalize() + username_noun_pull[rand_noun].capitalize() + "_" +
                        str(rand_num))

        case 4:
            rand_adj = random.randint(0, (len_adj - 1))
            rand_noun = random.randint(0, (len_noun - 1))
            rand_num = random.randint(0, 999999)
            username = (username_adj_pull[rand_adj].capitalize() + username_noun_pull[rand_noun].capitalize() + "." +
                        str(rand_num))

        case 5:
            rand_adj = random.randint(0, (len_adj - 1))
            rand_noun = random.randint(0, (len_noun - 1))
            rand_num = random.randint(0, 999999)
            username = (username_adj_pull[rand_adj].capitalize() + "." + username_noun_pull[rand_noun].capitalize() +
                        "." + str(rand_num))

        case 6:
            rand_adj = random.randint(0, (len_adj - 1))
            rand_noun = random.randint(0, (len_noun - 1))
            rand_num = random.randint(0, 999999)
            username = (username_adj_pull[rand_adj].capitalize() + "." + username_noun_pull[rand_noun].capitalize() +
                        str(rand_num))
    return username


def generate_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    return password


def generate_city():
    return cities[random.randint(0, 7)]


def generate_year():
    return random.randint(1985, 2014)


def transform_text(file):
    file_path = file + ".txt"
    new_file_path = file + "_new.txt"
    with open(file_path, 'r', encoding="utf-8") as file:
        data = file.read()
    clean_string = data.translate({ord(c): None for c in '"!@#$?,.-'})
    clean_string = clean_string.replace("\n", " ")
    clean_string = clean_string.lower()
    with open(new_file_path, 'w', encoding="utf-8") as file:
        file.write(clean_string)


def generate_publisher(pub_list, length):
    return pub_list[random.randint(0, length - 1)]


def generate_author(authors_list, length):
    return authors_list[random.randint(0, length - 1)]


def generate_title(word_list, length):
    rand_length = random.randint(1, 10)
    title = ""
    first = True
    for i in range(rand_length):
        rand_word = random.randint(0, length - 1)
        word = word_list[rand_word]
        if first:
            word = str(word).capitalize()
            first = False
        title += str(word) + " "
    return title


def fill_generated_books():
    print("Filling generated books")
    with open("text_new.txt", 'r', encoding="utf-8") as file:
        data = file.read()
    title_list = list(data.split(" "))
    title_list_final = []
    for ele in title_list:
        new_ele = ele.strip()
        if len(new_ele) > 4:
            print(new_ele + " " + str(len(new_ele)))
            title_list_final.append(new_ele)
    title_length = len(title_list_final)
    with open("publishers.txt", 'r', encoding="utf-8") as file:
        publishers = file.readlines()
    publishers_length = len(publishers)
    with open("authors.txt", 'r', encoding="utf-8") as file:
        authors = file.readlines()

    authors_length = len(authors)
    title_set = set()

    for i in range(5000000):
        title = generate_title(title_list_final, title_length).strip()
        title_set.add(title)
        if i % 100000 == 0:
            print(f'{i} row is inserted')

    for title in title_set:
        request_url = BOOK_URL
        headers = {'Content-Type': "application/json", 'Accept': "application/json"}
        body = {"title": title, "author": generate_author(authors, authors_length).strip(), "year": generate_year(),
                "publisher": generate_publisher(publishers, publishers_length).strip()}
        res = requests.post(request_url, json=body, headers=headers)
        if res.status_code is not requests.codes.ok:
            print(f'{title} was not inserted')


def fill_users():
    print("Filling generated users")
    with open("nouns_new.txt", 'r', encoding="utf-8") as file:
        username_noun_pull = file.read()
    noun_list = list(username_noun_pull.split(" "))
    len_noun = len(noun_list)
    len_adj = len(username_adj_pull)
    users_set = set()
    for i in range(5000000):
        username = generate_username(noun_list, len_noun, len_adj)
        users_set.add(username)
        if i % 100000 == 0:
            print(f'{i} row is inserted')
    for user in users_set:
        request_url = USER_URL
        headers = {'Content-Type': "application/json", 'Accept': "application/json"}
        body = {"username": user, "password": generate_password()}
        res = requests.post(request_url, json=body, headers=headers)
        if res.status_code is not requests.codes.ok:
            print(f'{user} was not inserted')


def fill_books():
    conn = database_credentials()
    cursor = conn.cursor()
    with open('books.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row['title'], row['author'], row['year'], row['publisher'])
            cursor.execute(f'INSERT INTO books (title, author, year, publisher, city) '
                           f'VALUES (%s, %s, %s, %s, %s)',
                           (row['title'], row['author'], row['year'], row['publisher'], generate_city()))
    conn.commit()
    cursor.close()
    conn.close()


def fill_reserved_books():
    number = random.randint(100000, 200000)
    conn = database_credentials()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT (*) FROM books")
    book_count = cursor.fetchall()[0][0]
    cursor.execute("SELECT COUNT (*) FROM users")
    user_count = cursor.fetchall()[0][0]

    for i in range(number):
        if i % 10000 == 0:
            print(str(i) + "/" + str(number))
        random_book = random.randint(1, book_count)
        cursor.execute("SELECT * FROM books WHERE id = {0}".format(random_book))
        if cursor.rowcount:
            book = cursor.fetchall()[0]
            if book[6] is None:
                random_user = random.randint(1, user_count)
                cursor.execute(
                    'UPDATE books SET reserved_by = %s WHERE id = %s',
                    (random_user, random_book))
    conn.commit()
    cursor.close()
    conn.close()


def add_book(isbn, title, author, year, publisher, image_s, image_m, image_l):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO books (isbn, title, author, year, publisher, image_s, image_m, image_l) '
                   f'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                   (isbn, title, author, year, publisher, image_s, image_m, image_l))
    conn.commit()
    cursor.close()
    conn.close()


def register_user(username, password):
    conn = database_credentials()

    cursor = conn.cursor()
    cursor.execute("SELECT * from users WHERE username = '{0}'".format(username))
    if not cursor.rowcount:
        cursor.execute(f'INSERT INTO users (username, password) VALUES (%s, %s)',
                       (username, password))
    else:
        print("User with the same name already registered!")
    conn.commit()
    cursor.close()
    conn.close()


def reserve_book(user, book_id): # TO DO title to id
    conn = database_credentials()
    cursor = conn.cursor()

    cursor.execute("SELECT * from users WHERE username = '{0}'".format(user))
    rows = cursor.fetchall()
    user_id = rows[0][0]
    cursor.execute(
        'UPDATE books SET reserved_by = %s WHERE id = %s',
        (user_id, book_id))

    conn.commit()
    cursor.close()
    conn.close()


def main():
    create_tables()
    transform_text("text")
    transform_text("nouns")
    fill_users()
    fill_generated_books()


main()
