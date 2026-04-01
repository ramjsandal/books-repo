import pymysql

connected = False
while (not connected):
    username = input("Enter username for database:")
    password = input("Enter password for database:")
    try:
        cnx = pymysql.connect(host='localhost', user=username, password=password, db='booksdb', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        connected = True
    except:
        print("Incorrect username or password, please try again")

running = True

while (running):

    print("Welcome to the book database!")
    logged_in = False
    while (not logged_in):
        print("Please type login to login or register to register")
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
                    print("Error 4500: No user exists for this login information")
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

    # login block is over
    print("Welcome " + display_name)
    running = False

cnx.close()