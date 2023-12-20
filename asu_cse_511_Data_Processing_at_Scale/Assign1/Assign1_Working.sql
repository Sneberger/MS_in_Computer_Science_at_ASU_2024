--ASSIGNMENT 1 SQL CODE:

CREATE TABLE users(
	user_id INT,
	name CHAR(50),				--should have been VARCHAR so not filled to 50 chars
	PRIMARY KEY (user_id));

CREATE TABLE movies(
	movie_id INT,
	title CHAR(170),			--should have been VARCHAR so not filled to 170 chars
	year_released INT,			--broke this out by replacing _% with _ and ) with nothing
	PRIMARY KEY (movie_id));	--having just "year" by itself resulted in 42601 syntax error
	
CREATE TABLE ratings(
	user_id INT,
	movie_id INT,
	rating NUMERIC(2, 1) CHECK(rating BETWEEN 0.0 AND 5.0),	
	time_stamp BIGINT,			--They say "Seconds since midnight UTC or 01/01/1970"
	FOREIGN KEY (user_id) REFERENCES users,
		ON DELETE CASCADE,
	FOREIGN KEY (movie_id) REFERENCES movies,
		ON DELETE CASCADE);
		
CREATE TABLE tag_info(
	tag_id INT,
	content CHAR(170),			--should have been VARCHAR so not filled to 170 chars
	PRIMARY KEY (tag_id));
	
CREATE TABLE tags(
	user_id INT,
	movie_id INT,
	tag_id INT NOT NULL,
	time_stamp BIGINT,			--They say "Seconds since midnight UTC or 01/01/1970"
	FOREIGN KEY (user_id) REFERENCES users,
		ON DELETE CASCADE,
	FOREIGN KEY (movie_id) REFERENCES movies,
		ON DELETE CASCADE,
	FOREIGN KEY (tag_id) REFERENCES tag_info,
		ON DELETE CASCADE);
	
CREATE TABLE genres(
	genre_id INT,
	name CHAR(50),				--should have been VARCHAR so not filled to 50 chars
	PRIMARY KEY (genre_id));
	
CREATE TABLE has_genre(
	movie_id INT,
	genre_id INT NOT NULL,
	FOREIGN KEY (movie_id) REFERENCES movies,
		ON DELETE CASCADE,
	FOREIGN KEY (genre_id) REFERENCES genres,
		ON DELETE CASCADE);
	

--I COULD NOT GET THE FOLLOWING-TYPE SYNTAX TO WORK UNLESS I MOVED csv INTO PgAdmin Folder
COPY movies(movie_id, title, year_released)
FROM 'C:\Users\msneb\Documents\School\CSE511\movies.csv' DELIMITER '%';
COPY tags(user_id, movie_id, tag_id, time_stamp)
FROM 'C:\Users\msneb\Documents\School\CSE511\tags.csv' DELIMITER '%';

--ENDED UP NOT NEEDING THIS AS I IMPORTED csv DATA
INSERT INTO ratings (user_id, movie_id, rating, time_stamp) VALUES(user_id, movie_id, rating, EXTRACT(EPOCH FROM NOW())


--ASSIGNMENT 2 SQL CODE:
--PART 1:
CREATE TABLE query1(
	name CHAR(20),
	movie_count INT);

INSERT INTO query1(name, movie_count)	--note you do not use VALUES when using SELECT
(SELECT genres.name, COUNT(*) FROM genres, has_genre WHERE genres.genre_id = has_genre.genre_id
GROUP BY genres.name ORDER by genres.name ASC);

--PART 2
CREATE TABLE query2(
	name CHAR(20),
	rating NUMERIC);


INSERT INTO query2(name, rating)
(SELECT genres.name, ROUND(AVG(ratings.rating), 1) FROM genres, ratings, has_genre
WHERE ratings.movie_id = has_genre.movie_id AND genres.genre_id = has_genre.genre_id
GROUP BY genres.name ORDER by genres.name ASC);

--PART 3
CREATE TABLE query3(
	title VARCHAR(170),
	count_of_ratings INT);

INSERT INTO query3(title, count_of_ratings)
(SELECT movies.title, COUNT(*) FROM ratings, movies --select movie_id and counting all rows subject WHERE in ratings
WHERE ratings.rating is NOT NULL AND ratings.movie_id = movies.movie_id
GROUP BY movies.title
HAVING COUNT(*) >= 10
ORDER by movies.title ASC);

--PART 4
CREATE TABLE query4(
	movie_id INT,
	title VARCHAR(170));

INSERT INTO query4(movie_id, title)	--note you do not use VALUES when using SELECT
(SELECT has_genre.movie_id, movies.title FROM movies, has_genre, genres
WHERE  has_genre.movie_id = movies.movie_id
	AND has_genre.genre_id = genres.genre_id
	AND genres.name = 'Comedy'
ORDER by movies.title ASC);

--PART 5
CREATE TABLE query5(
	title VARCHAR(170),
	average NUMERIC);


INSERT INTO query5(title, average)
(
SELECT movies.title, ROUND(AVG(ratings.rating), 1) FROM movies, ratings
WHERE movies.movie_id = ratings.movie_id --AND genres.genre_id = has_genre.genre_id
GROUP BY movies.title ORDER by movies.title ASC);

--PART 6
CREATE TABLE query6(
	average NUMERIC);

INSERT INTO query6(average)	--note you do not use VALUES when using SELECT
(SELECT ROUND(AVG(ratings.rating), 3) FROM ratings, has_genre, genres
WHERE  has_genre.genre_id = genres.genre_id
	AND ratings.movie_id = has_genre.movie_id
	AND genres.name = 'Comedy');
	
--PART 7
CREATE TABLE query7(
	average NUMERIC);

INSERT INTO query7(average)	--note you do not use VALUES when using SELECT
(SELECT AVG(ratings.rating) FROM has_genre AS has_genre_comedy, has_genre AS has_genre_romance, ratings
WHERE has_genre_comedy.genre_id = 5 AND has_genre_romance.genre_id = 14
	AND has_genre_comedy.movie_id = has_genre_romance.movie_id
	AND has_genre_comedy.movie_id = ratings.movie_id);

--PART 8
CREATE TABLE query8(
	average NUMERIC);

INSERT INTO query8(average)	--note you do not use VALUES when using SELECT
(SELECT AVG(ratings.rating)
FROM has_genre AS has_genre_romance, ratings
WHERE has_genre_romance.genre_id = 14
AND has_genre_romance.movie_id = ratings.movie_id
AND ratings.movie_id NOT IN
	(SELECT has_genre_comedy.movie_id
	FROM has_genre AS has_genre_comedy
	WHERE has_genre_comedy.genre_id = 5));

--PART 9 note this is hard-coded to run user_id = 2 to follow example
CREATE TABLE query9(
	movie_id INT,
	rating NUMERIC);
	
CREATE FUNCTION part9(in integer) RETURNS TABLE(movie_id INT, rating NUMERIC)
	AS $$ SELECT ratings.movie_id, ratings.rating FROM ratings
		WHERE  ratings.user_id = $1
		AND ratings.rating IS NOT NULL $$
		LANGUAGE SQL;

INSERT INTO query9(SELECT * FROM part9(2))

--HERE IS A PYTHON SCRIPT TO ASK THE USER WHAT user_id THEY WANT TO QUERY
import psycopg2

part9_user_id = input('Input the user_id you would like to query: ')
print("You have selected user_id: " + str(part9_user_id))

part9_query = "INSERT INTO query9(SELECT * FROM part9(" + part9_user_id + "))"

password = open('password.txt', 'r').read()	--password could simply be "postgres"
conn = psycopg2.connect('dbname=Movies user=postgres password={0}'.format(password))
cur = conn.cursor()

cur.execute(part9_query)
conn.commit()
cur.close()
conn.close()

--PART 10
--FIRST STEP CREATS similarity TABLE WITH 100,000,000+ ENTRIES SHOWING sim() VALUES
CREATE TABLE similarity(
	movie_id1 INT,		--this should be lowercase L movie already rated by user
	movie_id2 INT,		--this should be i movie not rated by user
	sim NUMERIC(20, 19));--result of simulation function w/value 0 <= sim <= 1

INSERT INTO similarity(movie_id1, movie_id2, sim)
SELECT ratings_I.movie_id, ratings_L.movie_id, (1-ABS(AVG(ratings_I.rating)-AVG(ratings_L.rating))/5)
FROM ratings ratings_I, ratings ratings_L
--WHERE ratings_I.movie_id = I AND ratings_L.movie_id <= 100
GROUP BY ratings_I.movie_id, ratings_L.movie_id
		
--SECOND PART TO CREATE query10 RECOMMENDATION TABLE
CREATE TABLE recommendation(
	title VARCHAR(170));
	
--MISSING NARROWING DOWN TO MOVIES USER HAS NOT SEEN AND INSERTING INTO TABLE

SUNDAY 08-02-2020 discussion with David
1) my try = seemingly correct output but does not make sense why due to > 3.9 issue
SELECT movies.title FROM movies
WHERE (SELECT SUM(s.sim*ratings_L.rating)/SUM(s.sim)
FROM similarity s, ratings ratings_I, ratings ratings_L
WHERE ratings_I.movie_id = movies.movie_id --if remove WHERE get every movie or all - query9
AND s.movie_id1 = ratings_L.movie_id
AND s.movie_id2 = ratings_I.movie_id
AND ratings_L.user_id = 2
AND ratings_I.user_id <> 2) <= 3.9
LIMIT 100
2)
SELECT movies.title
FROM movies
WHERE (
SELECT SUM(s.sim*ratings_L.rating)/SUM(s.sim)
FROM similarity s, ratings ratings_I, ratings ratings_L
WHERE ratings_I.movie_id = movies.movie_id
AND s.movie_id1 = ratings_L.movie_id
AND s.movie_id2 = ratings_I.movie_id
AND ratings_L.user_id = 2
AND ratings_I.user_id <> 2
) > 3.9
3)
SELECT ratings_I.movie_id, SUM(s.sim*ratings_L.rating)/SUM(s.sim)
FROM similarity s, ratings ratings_I, ratings ratings_L
WHERE s.movie_id1 = ratings_L.movie_id
AND s.movie_id2 = ratings_I.movie_id
AND ratings_L.user_id = 2
AND ratings_I.user_id <> 2
GROUP BY ratings_I.movie_id
4)
SELECT movies.title, SUM(s.sim*ratings_L.rating)/SUM(s.sim)
FROM similarity s, ratings ratings_I, ratings ratings_L, movies
WHERE s.movie_id1 = ratings_L.movie_id
AND s.movie_id2 = ratings_I.movie_id
AND ratings_L.user_id = 2
AND ratings_I.user_id <> 2
AND ratings_I.movie_id = movies.movie_id
GROUP BY movies.title
HAVING SUM(s.sim*ratings_L.rating)/SUM(s.sim) > 3.9
LIMIT 100
5)
SELECT ratings_I.movie_id, SUM(s.sim*ratings_L.rating)/SUM(s.sim)
FROM similarity s, ratings ratings_I, ratings ratings_L
WHERE s.movie_id1 = ratings_L.movie_id
AND s.movie_id2 = ratings_I.movie_id
AND ratings_L.user_id = 2
AND ratings_I.user_id <> 2
GROUP BY ratings_I.movie_id
ORDER BY SUM(s.sim*ratings_L.rating)/SUM(s.sim) DESC --removed > 3.9
6) = modification of #4
SELECT movies.title, SUM(s.sim*ratings_L.rating)/SUM(s.sim)
FROM similarity s, ratings ratings_I, ratings ratings_L, movies
WHERE s.movie_id1 = ratings_L.movie_id
AND s.movie_id2 = ratings_I.movie_id
AND ratings_I.movie_id = movies.movie_id
AND ratings_I.movie_id NOT IN ( SELECT DISTINCT movie_id
FROM ratings
WHERE user_id = 2)
AND ratings_L.movie_id IN ( SELECT DISTINCT movie_id
FROM ratings
WHERE user_id = 2)
GROUP BY movies.title
ORDER BY SUM(s.sim*ratings_L.rating)/SUM(s.sim) DESC
6a) David corrected error in above
SELECT ratings_I.movie_id AS I, SUM(s.sim*ratings_L.rating)/SUM(s.sim)
FROM similarity s, ratings ratings_I, ratings ratings_L
WHERE s.movie_id1 = ratings_I.movie_id
AND s.movie_id2 = ratings_L.movie_id
AND ratings_I.movie_id NOT IN ( SELECT DISTINCT movie_id
                                FROM ratings
                                WHERE user_id = 2)
AND ratings_L.user_id = 2	-- this replaces subquery syntax of earlier version
GROUP BY ratings_I.movie_id
ORDER BY SUM(s.sim*ratings_L.rating)/SUM(s.sim) DESC