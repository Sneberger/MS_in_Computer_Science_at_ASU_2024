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

--USE PYTHON SCRIPT TO TAKE IN user_id FROM USER THEN RUN PSQL
--IMPORT psycopg
import psycopg2

part9_user_id = input('Input the user_id you would like to query: ')

#part9() is a postgres function that returns all movie ratings for user_id
part9_query = "INSERT INTO query9(SELECT * FROM part9(" + part9_user_id + "))"

print("postgres query: " + part9_query)

password = open('password.txt', 'r').read()
conn = psycopg2.connect('dbname=Movies user=postgres password={0}'.format(password))
cur = conn.cursor()

cur.execute(part9_query)

conn.commit()

cur.close()

conn.close()


--PART 10 Recomender
CREATE TABLE recommendation(
	recommend_value NUMERIC,
	name VARCHAR(170));
	
CREATE FUNCTION recommend(in interger) RETURNS TABLE(recommend_value NUMERIC, name VARCHAR(170))
	AS $$ SELECT 
	
	
	

(SELECT movies.title, ROUND(AVG(ratings.rating), 1) FROM movies, ratings
WHERE movies.movie_id = ratings.movie_id --AND genres.genre_id = has_genre.genre_id
GROUP BY movies.title ORDER by movies.title ASC);