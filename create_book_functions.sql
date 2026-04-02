USE booksdb;

DROP PROCEDURE IF EXISTS register_user;
DELIMITER //
CREATE PROCEDURE register_user(IN in_username VARCHAR(128), IN in_password VARCHAR(128), IN in_display_name VARCHAR(128))
BEGIN
    INSERT INTO application_user(username, user_password, display_name) 
    VALUES(in_username, in_password, in_display_name);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS add_publisher;
DELIMITER //
CREATE PROCEDURE add_publisher(IN in_name VARCHAR(128))
BEGIN
    INSERT INTO publisher(name, date_established, num_employees) 
    VALUES(in_name, NULL, NULL);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS add_book;
DELIMITER //
CREATE PROCEDURE add_book(IN in_isbn VARCHAR(16), IN in_title VARCHAR(128), IN in_page_count INT, IN in_publisher_name VARCHAR(64))
BEGIN
	IF NOT EXISTS(SELECT * FROM publisher WHERE name = in_publisher_name)
    THEN CALL add_publisher(in_publisher_name);
    END IF;

    INSERT INTO book(isbn, title, average_rating, page_count, initial_pub_date, publisher_name) 
    VALUES(in_isbn, in_title, NULL, in_page_count, NULL, in_publisher_name);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_book;
DELIMITER //
CREATE PROCEDURE delete_book(IN in_isbn VARCHAR(16))
BEGIN
	IF NOT EXISTS (SELECT * FROM book WHERE isbn = in_isbn)
    THEN SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "No books exist with this isbn!";
    END IF;
    DELETE FROM book WHERE isbn = in_isbn;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_author;
DELIMITER //
CREATE PROCEDURE delete_author(IN in_author_id INT)
BEGIN
	IF NOT EXISTS (SELECT * FROM author WHERE author_id = in_author_id)
    THEN SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "No authors exist with this id!";
    END IF;
    DELETE FROM author WHERE author_id = in_author_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS delete_review;
DELIMITER //
CREATE PROCEDURE delete_review(IN in_review_id INT, IN in_username VARCHAR(128))
BEGIN
	IF NOT EXISTS (SELECT * FROM review NATURAL JOIN book_reviews WHERE review_id = in_review_id AND username = in_username)
    THEN SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "No reviews exist with this id by this user!";
    END IF;
    DELETE FROM review WHERE review_id = in_review_id;
END //
DELIMITER ;

#CALL delete_review(2, "sam");

DROP PROCEDURE IF EXISTS author_books;
DELIMITER //
CREATE PROCEDURE author_books(IN in_author_id INT)
BEGIN
	IF NOT EXISTS (SELECT * FROM author WHERE author_id = in_author_id)
    THEN SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "No authors exist with this id!";
    END IF;
    
    SELECT author.first_name, author.last_name, book.* FROM book NATURAL JOIN
    book_authors NATURAL JOIN
    author WHERE author_id = in_author_id;
    
END //
DELIMITER ;

#CALL add_author("john", "author", 42, "english");
#CALL add_authorship("101", 1);
#CALL author_books(1);

# EXAMPLES
#CALL add_book ("102", "testbook", 200, "testpub2");
#CALL delete_book ("10231359184");
#CALL add_publisher("testpub");

DROP PROCEDURE IF EXISTS leave_review;
DELIMITER //
CREATE PROCEDURE leave_review(IN in_rating FLOAT, IN in_description VARCHAR(1024), IN in_username VARCHAR(128), IN in_isbn VARCHAR(16))
BEGIN
	IF (in_rating < 0 OR in_rating > 5)
    THEN SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "Review must be between 0 and 5 stars!";
    END IF;

    INSERT INTO review(rating, description, username) 
    VALUES(in_rating, in_description, in_username);
    INSERT INTO book_reviews(isbn, review_id)
    VALUES(in_isbn, LAST_INSERT_ID());
END //
DELIMITER ;

#CALL leave_review(3, "it was ok", "sam", "201");

DROP PROCEDURE IF EXISTS update_review;
DELIMITER //
CREATE PROCEDURE update_review(IN in_rating FLOAT, IN in_description VARCHAR(1024), IN in_username VARCHAR(128), IN in_isbn VARCHAR(16))
BEGIN
	IF NOT EXISTS (SELECT * FROM review NATURAL JOIN book_reviews 
    WHERE username = in_username AND isbn = in_isbn)
    THEN SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "No reviews found from this user for this book!";
    END IF;
    
	IF (in_rating < 0 OR in_rating > 5)
    THEN SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "Review must be between 0 and 5 stars!";
    END IF;

	UPDATE review
    NATURAL JOIN book_reviews
    SET rating = in_rating, description = in_description
    WHERE username = in_username AND isbn = in_isbn;
END //
DELIMITER ;

#CALL update_review(3, "it wasn't very good", "sam", "101");

DROP PROCEDURE IF EXISTS update_book;
DELIMITER //
CREATE PROCEDURE update_book(IN in_isbn VARCHAR(16), IN in_title VARCHAR(128), IN in_page_count INT, IN in_publisher_name VARCHAR(64))
BEGIN
	
    IF NOT EXISTS(SELECT * FROM publisher WHERE name = in_publisher_name)
    THEN CALL add_publisher(in_publisher_name);
    END IF;
    
	UPDATE book
    SET title = in_title, page_count = in_page_count, publisher_name = in_publisher_name 
    WHERE isbn = in_isbn;
END //
DELIMITER ;

#CALL update_book("500", "how", 5000, "kerblam");

DROP PROCEDURE IF EXISTS update_author;
DELIMITER //
CREATE PROCEDURE update_author(IN in_author_id INT, IN in_first_name VARCHAR(128), IN in_last_name VARCHAR(128), IN in_age INT, IN in_language VARCHAR(128))
BEGIN
	
    IF NOT EXISTS(SELECT * FROM author WHERE author_id = in_author_id)
		THEN SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "Author does not exist in database";
    END IF;
        
	UPDATE author
    SET first_name = in_first_name, last_name = in_last_name, age = in_age, primary_language = in_language
    WHERE author_id = in_author_id;
END //
DELIMITER ;

#CALL update_author(45, "johnny", "author", 40, "english");

DROP PROCEDURE IF EXISTS get_all_reviews_for_book;
DELIMITER //
CREATE PROCEDURE get_all_reviews_for_book(IN in_isbn VARCHAR(16))
BEGIN
    SELECT review.* FROM review NATURAL JOIN
    book_reviews NATURAL JOIN
    book WHERE isbn = in_isbn;
END //
DELIMITER ;

DROP FUNCTION IF EXISTS has_reviewed;
DELIMITER //
CREATE FUNCTION has_reviewed(in_username VARCHAR(128), in_isbn VARCHAR(16))
RETURNS BOOLEAN
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE review_count INT;
    SELECT COUNT(*) INTO review_count FROM review NATURAL JOIN
    book_reviews NATURAL JOIN
    book WHERE(in_username = review.username AND in_isbn = book.isbn);
    RETURN review_count > 0;
END //
DELIMITER ;

#SELECT has_reviewed("sam", "101");

DROP PROCEDURE IF EXISTS get_user_reviews;
DELIMITER //
CREATE PROCEDURE get_user_reviews(IN in_display_name VARCHAR(128))
BEGIN
    SELECT book.isbn, book.title, review.* FROM review NATURAL JOIN
    application_user NATURAL JOIN
    book_reviews NATURAL JOIN
    book WHERE display_name = in_display_name;
END //
DELIMITER ;

#CALL get_user_reviews("sam");
#CALL get_all_reviews_for_book("101");

DROP PROCEDURE IF EXISTS add_author;
DELIMITER //
CREATE PROCEDURE add_author(
in_first_name VARCHAR(64),
in_last_name VARCHAR(64),
in_age INT,
in_primary_language VARCHAR(64))
BEGIN
    INSERT INTO author(first_name, last_name, age, primary_language) 
    VALUES(in_first_name, in_last_name, in_age, in_primary_language);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS get_authors;
DELIMITER //
CREATE PROCEDURE get_authors()
BEGIN
    SELECT * FROM author;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS get_books;
DELIMITER //
CREATE PROCEDURE get_books()
BEGIN
    SELECT * FROM book;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS add_genre;
DELIMITER //
CREATE PROCEDURE add_genre(
in_name VARCHAR(64),
in_description VARCHAR(128))
BEGIN
    INSERT INTO genre(name, description) 
    VALUES(in_name, in_description);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS add_authorship;
DELIMITER //
CREATE PROCEDURE add_authorship(
in_isbn VARCHAR(16),
in_author_id INT)
BEGIN
    INSERT INTO book_authors(isbn, author_id) 
    VALUES(in_isbn, in_author_id);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS add_genre_to_book;
DELIMITER //
CREATE PROCEDURE add_genre_to_book(
in_isbn VARCHAR(16),
in_genre_name VARCHAR(64))
BEGIN
    INSERT INTO book_genres(isbn, genre_name) 
    VALUES(in_isbn, in_genre_name);
END //
DELIMITER ;

DROP TRIGGER IF EXISTS update_average_rating_inserted;
DELIMITER //
CREATE TRIGGER update_average_rating_inserted AFTER INSERT ON book_reviews
FOR EACH ROW
BEGIN
	UPDATE book
    SET average_rating = (
        SELECT AVG(review.rating) FROM review
        JOIN book_reviews ON review.review_id = book_reviews.review_id
        WHERE book_reviews.isbn = NEW.isbn
    )
    WHERE book.isbn = NEW.isbn;
END //
DELIMITER ;

DROP TRIGGER IF EXISTS update_average_rating_deleted;
DELIMITER //
CREATE TRIGGER update_average_rating_deleted AFTER DELETE ON book_reviews
FOR EACH ROW
BEGIN
	UPDATE book
    SET average_rating = (
        SELECT AVG(review.rating) FROM review
        JOIN book_reviews ON review.review_id = book_reviews.review_id
        WHERE book_reviews.isbn = OLD.isbn
    )
    WHERE book.isbn = OLD.isbn;
END //
DELIMITER ;

DROP FUNCTION IF EXISTS get_display_name;
DELIMITER //

CREATE FUNCTION get_display_name(username_p VARCHAR(128), password_p VARCHAR(128))
RETURNS VARCHAR(128)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE display_name_result VARCHAR(128);
    SELECT display_name INTO display_name_result FROM application_user
    WHERE username = username_p AND user_password = password_p;

    IF display_name_result IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = "Login information does not exist, is there a typo in your username or password?";
    END IF;

    RETURN display_name_result;
END //
DELIMITER ;

#SELECT get_display_name("xdd", "woajdsoa");

DROP FUNCTION IF EXISTS user_exists;
DELIMITER //
CREATE FUNCTION user_exists(in_username VARCHAR(128), in_display_name VARCHAR(128))
RETURNS BOOLEAN
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE user_count INT;
    SELECT COUNT(*) INTO user_count FROM application_user
    WHERE username = in_username OR display_name = in_display_name;
    RETURN user_count > 0;
END //

DELIMITER ;