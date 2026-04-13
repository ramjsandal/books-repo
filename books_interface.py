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
    print("See all users in the database: \'get_users\'")
    print("Update account information \'update_account\'")
    print("Delete account \'delete_account\'")

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

    print("\nPublisher Actions:")
    print("Add a publisher to the database: \'add_publisher\'")
    print("Get all books by a publisher: \'publisher_books\'")
    print("Get all publishers in the database: \'get_publishers\'")
    print("Update a publisher in the database: \'update_publisher\'")
    print("Remove a publisher from the database: \'delete_publisher\'")

    print("\nReview Actions:")
    print("Leave a review for a book: \'leave_review\'")
    print("Update one of your reviews: \'update_review\'")
    print("Delete one of your reviews: \'delete_review\'")
    print("See all reviews for a book: \'see_reviews\'")
    print("See your reviews: \'my_reviews\'")

    print("\nGenre Actions:")
    print("Add a genre to the database: \'add_genre\'")
    print("Get all books with this genre: \'genre_books\'")
    print("Add a genre to a book: \'classify_book\'")
    print("Remove a genre from a book: \'declassify_book\'")
    print("Update a genre in the database: \'update_genre\'")
    print("Remove a genre from the database: \'delete_genre\'")

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

        ######### PUBLISHER ACTIONS ##########
        case "add_publisher":
            name = input("Enter name of publisher: ")
            num_employees = int(input("Enter number of employees of publisher: "))
            run_procedure("add_publisher", [name, num_employees], "Publisher added to database!")
                    
        case "delete_publisher":
            name = input("Enter name of publisher: ")
            run_procedure("delete_publisher", [name], "Publisher deleted from database!")

        case "update_publisher":
            name = input("Enter name of publisher: ")
            num_employees = int(input("Enter new number of employees of publisher: "))
            run_procedure("update_publisher", [name, num_employees], "Publisher updated in database!")

        case "get_publishers":
            try:
                cur.callproc("get_publishers")
                cnx.commit()
                for publisher in cur.fetchall():
                    print(f"Publisher name: {publisher['name']}")
                    print(f"Number of employees: {publisher['num_employees']}\n")
            except pymysql.Error as e:
                throw_error(e)

        case "publisher_books":
            publisher = input("Enter name of publisher: ")
            try:
                cur.callproc("publisher_books", args=[publisher])
                cnx.commit()
                responses = cur.fetchall()
                print(f"Books published by {publisher}:")
                for book in responses:
                    print(f"ISBN: {book['isbn']}: ")
                    print(f"Title: {book['title']}")
                    print(f"Average rating: {book['average_rating']}")
                    print(f"Page count: {book['page_count']}")
                    print(f"Initial publication date: {book['initial_pub_date']}\n")
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
                    print(f"Review for \"{review['title']}\" with ISBN {review['isbn']} and review id {review['review_id']}: ")
                    print(f"Star rating: {review['rating']}")
                    print(f"Text review: {review['description']}\n")
            except pymysql.Error as e:
                throw_error(e)

        ########## GENRE ACTIONS ##########
        case "add_genre":
            name = input("Enter name of genre: ")
            description = input("Enter description of genre: ")
            run_procedure(command_string="add_genre", args=[name, description], success_string="Genre added to database!") 

        case "update_genre":
            name = input("Enter name of genre: ")
            description = input("Enter description of genre: ")
            run_procedure(command_string="update_genre", args=[name, description], success_string="Genre updated in database!") 

        case "delete_genre":
            name = input("Enter name of genre: ")
            run_procedure("delete_genre", [name], "Genre deleted from database!")

        case "genre_books":
            name = input("Enter name of genre: ")
            try:
                cur.callproc("get_books_with_genre", args=[name])
                cnx.commit()
                responses = cur.fetchall()
                print(f"Books with genre {name}:")
                for book in responses:
                    print(f"ISBN: {book['isbn']}: ")
                    print(f"Title: {book['title']}")
                    print(f"Average rating: {book['average_rating']}")
                    print(f"Page count: {book['page_count']}")
                    print(f"Initial publication date: {book['initial_pub_date']}\n")
            except pymysql.Error as e:
                throw_error(e)

        case "classify_book":
            name = input("Enter name of genre: ")
            isbn = input("Enter ISBN of book: ")
            run_procedure(command_string="add_genre_to_book", args=[name, isbn], success_string="Genre added to book in database!") 

        case "declassify_book":
            name = input("Enter name of genre: ")
            isbn = input("Enter ISBN of book: ")
            run_procedure(command_string="remove_genre_from_book", args=[name, isbn], success_string="Genre removed from book in database!") 

        ########## SYSTEM ACTIONS ##########
        case "update_account":
            password = input("Enter a new password: ")
            display_name = input("Enter a new display name: ")
            run_procedure("update_user", [user, password, display_name], "Account updated in database!")

        case "delete_account":
            confirm = input("Are you sure you want to delete your account? Type YES to delete your account: ")
            if (confirm == "YES"):
                run_procedure("delete_user", [user], "Account deleted from database!")
            else:
                print("Not deleting account!")

        case "get_users":
            try:
                cur.callproc("get_users")
                cnx.commit()
                for user in cur.fetchall():
                    print(f"Display name: {user['display_name']}\n")
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