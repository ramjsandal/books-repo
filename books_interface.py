import pymysql

def throw_error(error):
    error_code = error.args[0]
    error_message = error.args[1]
    print(f"Error {error_code}: {error_message}")
    print("Please try again!")

def help_message():
    print("Available actions in the book database:")

    print("\nSystem Actions:")
    print("Exit the program: \'quit\'")
    print("See this list of commands again: \'help\'")

    print("\nBook Actions:")
    print("Add a book to the database: \'add_book\'")
    print("Get all books by an author: \'author_books\'")
    print("Get all books in the database: \'get_books\'")
    print("Update a book in the database: \'update_book\'")
    print("Remove a book from the database: \'delete_book\'")

    print("\nAuthor Actions:")
    print("Add an author to the database: \'add_author\'")
    print("Remove an author from the database: \'delete_author\'")
    print("Update an author in the database: \'update_author\'")
    print("Get all authors in the database: \'get_authors\'")
    print("Credit an author on a book: \'add_credit\'")

    print("\nReview Actions:")
    print("Leave a review for a book: \'leave_review\'")
    print("Update one of your reviews: \'update_review\'")
    print("Delete one of your reviews: \'delete_review\'")
    print("See all reviews for a book: \'see_reviews\'")
    print("See your reviews: \'my_reviews\'")

def run_procedure(command_string, args, success_string):
    try:
        cur.callproc(command_string, args)
        cnx.commit()
        print(success_string)
    except pymysql.Error as e:
        throw_error(e)


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
                continue
        print("Welcome " + display_name)
        help_message()

    # login block is over
    command = input("\nEnter command: ")
    match (command.lower()):

        ########## BOOK ACTIONS ##########
        case "add_book":
            isbn = input("Enter ISBN of book: ")
            title = input("Enter title of book: ")
            page_count = int(input("Enter page count of book: "))
            publisher_name = input("Enter publisher name of book: ")
            run_procedure(command_string="add_book", args=[isbn, title, page_count, publisher_name], success_string="Book added to database!") 

        case "update_book":
            isbn = input("Enter ISBN of book: ")
            title = input("Enter new title of book: ")
            page_count = int(input("Enter new page count of book: "))
            publisher_name = input("Enter new publisher name of book: ")
            run_procedure(command_string="update_book", args=[isbn, title, page_count, publisher_name], success_string="Book updated in database!") 

        case "delete_book":
            isbn = input("Enter ISBN of book: ")
            run_procedure("delete_book", [isbn], "Book deleted from database!")

        case "author_books":
            id = input("Enter author_id of author: ")
            try:
                cur.callproc("author_books", args=[id])
                cnx.commit()
                responses = cur.fetchall()
                if len(responses) > 0 : print(f"Books by {responses[0]['first_name']} {responses[0]['last_name']}:")
                else: print("No books by this author...")
                for book in responses:
                    print(f"ISBN: {book['isbn']}: ")
                    print(f"Title: {book['title']}")
                    print(f"Average rating: {book['average_rating']}")
                    print(f"Page count: {book['page_count']}")
                    print(f"Initial publication date: {book['initial_pub_date']}\n")
            except pymysql.Error as e:
                throw_error(e)

        case "get_books":
            try:
                cur.callproc("get_books")
                cnx.commit()
                for book in cur.fetchall():
                    print(f"ISBN: {book['isbn']}")
                    print(f"Title: {book['title']}")
                    print(f"Page count: {book['page_count']}")
                    print(f"Initial publication date: {book['initial_pub_date']}\n")
            except pymysql.Error as e:
                throw_error(e)



        ######### AUTHOR ACTIONS ##########
        case "add_author":
            first_name = input("Enter first name of author: ")
            last_name = input("Enter last name of author: ")
            age = int(input("Enter age of author: "))
            language = input("Enter primary language of author: ")
            run_procedure("add_author", [first_name, last_name, age, language], "Author added to database!")
                    
        case "add_credit":
            isbn = input("Enter ISBN of book: ")
            author = int(input("Enter author_id of author: "))
            run_procedure("add_authorship", [isbn, author], "Authorship added to database!")

        case "delete_author":
            id = int(input("Enter author_id of author: "))
            run_procedure("delete_author", [id], "Author deleted from database!")

        case "update_author":
            id = int(input("Enter author_id of author: "))
            first_name = input("Enter new first name of author: ")
            last_name = input("Enter new last name of author: ")
            age = int(input("Enter new age of author: "))
            language = input("Enter new primary language of author: ")
            run_procedure("update_author", [id, first_name, last_name, age, language], "Author updated in database!")

        case "get_authors":
            try:
                cur.callproc("get_authors")
                cnx.commit()
                for author in cur.fetchall():
                    print(f"Author ID: {author['author_id']}")
                    print(f"Name: {author['first_name']} {author['last_name']}")
                    print(f"Age: {author['age']}")
                    print(f"Primary language: {author['primary_language']}\n")
            except pymysql.Error as e:
                throw_error(e)

        ######### REVIEW ACTIONS ##########
        case "leave_review":
            isbn = input("Enter ISBN of book: ")
            try:
                cur.execute("SELECT has_reviewed(%s, %s)", (user, isbn))
                has_review = next(iter(cur.fetchone().values()))
                if has_review:
                    print("You've already reviewed this book, you can update your review with update_review")
                    continue
            except pymysql.Error as e:
                throw_error(e)

            rating = float(input("Enter your rating for the book: "))
            description = input("Enter a text review of the book: ")
            run_procedure("leave_review", [rating, description, user, isbn], "Review successful!")

        case "update_review":
            isbn = input("Enter ISBN of book: ")
            try:
                cur.execute("SELECT has_reviewed(%s, %s)", (user, isbn))
                has_review = next(iter(cur.fetchone().values()))
                if not has_review:
                    print("You've have not reviewed this book, you can leave a review with leave_review")
                    continue
            except pymysql.Error as e:
                throw_error(e)

            rating = float(input("Enter your rating for the book: "))
            description = input("Enter a text review of the book: ")
            run_procedure("update_review", [rating, description, user, isbn], "Review updated!")

        case "delete_review":
            id = int(input("Enter review_id of review: "))
            run_procedure("delete_review", [id, user], "Review deleted from database!")

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

        ########## SYSTEM ACTIONS ##########
        case "help":
            help_message()

        case "quit":
            print("See you next time!")
            running = False

        case _:
            print("Invalid command! Type 'help' to get a list of valid commands")


cnx.close()