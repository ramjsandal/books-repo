import pymysql

def throw_error(error):
    error_code = e.args[0]
    error_message = e.args[1]
    print(f"Error {error_code}: {error_message}")
    print("Please try again!")

def help_message():
    print("Available actions in the book database:")
    print("\nSystem Actions:")
    print("Exit the program: \'quit\'")
    print("See this list of commands again: \'help\'")
    print("\nBook Actions:")
    print("Add a book to the database: \'add_book\'")
    print("Remove a book from the database: \'delete_book\'")
    print("\nReview Actions:")
    print("Leave a review for a book: \'leave_review\'")
    print("See all reviews for a book: \'see_reviews\'")
    print("See your reviews: \'my_reviews\'")
    
connected = False
while (not connected):
    username = input("Enter username for database connection: ")
    password = input("Enter password for database connection: ")
    try:
        cnx = pymysql.connect(host='localhost', user=username, password=password, db='booksdb', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        connected = True
    except:
        print("Incorrect username or password, please try again")

running = True
logged_in = False
print()
print("Welcome to the book database!")
while (running):
    while (not logged_in):
        print("Please type \'login\' to login or \'register\' to register")
        choice = input("")
        cur = cnx.cursor()
    
        match(choice.lower()):
            case "login":
                user = input("Please enter your username: ")
                password = input("Please enter your password: ")
                try:
                    cur.execute("SELECT get_display_name(%s, %s)", (user, password))
                    display_name = next(iter(cur.fetchone().values()))
                    logged_in = True 
                except pymysql.Error as e:
                    throw_error(e)
                    continue
            case "register":
                user = input("Please enter your username: ")
                password = input("Please enter your password: ")
                display_name = input("Please enter a display name: ")
                cur.execute("SELECT user_exists(%s, %s)", (user, display_name))
                already_exists = next(iter(cur.fetchone().values()))
                if (already_exists):
                    print("User already exists with that username or display name, please try a new one!")
                    continue
                cur.callproc('register_user', args=[user, password, display_name])
                cnx.commit()
                logged_in = True 
            case _:
                print("Please enter either \'login\' or \'register\'")
        print("Welcome " + display_name)
        help_message()

    # login block is over
    command = input("Enter command: ")
    match (command.lower()):
        case "add_book":
            isbn = input("Enter ISBN of book: ")
            title = input("Enter title of book: ")
            page_count = int(input("Enter page count of book: "))
            publisher_name = input("Enter publisher name of book: ")
            try:
                cur.callproc("add_book", args=[isbn, title, page_count, publisher_name])
                cnx.commit()
            except pymysql.Error as e:
                throw_error(e)
        case "delete_book":
            isbn = input("Enter ISBN of book: ")
            try:
                cur.callproc("delete_book", args=[isbn])
                cnx.commit()
            except pymysql.Error as e:
                throw_error(e)
        case "leave_review":
            isbn = input("Enter ISBN of book: ")
            rating = float(input("Enter your rating for the book: "))
            description = input("Enter a text review of the book: ")
            try:
                cur.callproc("leave_review", args=[rating, description, user, isbn])
                cnx.commit()
            except pymysql.Error as e:
                throw_error(e)
        case "see_reviews":
            isbn = input("Enter ISBN of book: ")
            try:
                cur.callproc("get_all_reviews_for_book", args=[isbn])
                cnx.commit()
                for review in cur.fetchall():
                    print(f"Review from {review['username']}: ")
                    print(f"Star rating: {review['rating']}")
                    print(f"Text review: {review['description']}\n")
            except pymysql.Error as e:
                throw_error(e)
        case "my_reviews":
            try:
                cur.callproc("get_user_reviews", args=[user])
                cnx.commit()
                for review in cur.fetchall():
                    print(f"Review for \"{review['title']}\" with ISBN {review['isbn']}: ")
                    print(f"Star rating: {review['rating']}")
                    print(f"Text review: {review['description']}\n")
            except pymysql.Error as e:
                throw_error(e)
        case "help":
            help_message()
        case "quit":
            print("See you next time!")
            running = False
        case _:
            print("Invalid command! Type 'help' to get a list of valid commands")


cnx.close()