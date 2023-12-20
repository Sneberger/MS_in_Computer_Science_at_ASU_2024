#Submission for Assignment 3 = Python script that controls PostreSQL
#!/usr/bin/python2.7
#
# Interface for the assignement
#

import psycopg2
import sys

def getOpenConnection(user='postgres', password='1234', dbname='postgres'): #dbname should = 'postgres' turning in and 'MovieLens' for testing
    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "'host='localhost' password='" + password + "'")
    
def loadRatings(ratingstablename, ratingsfilepath, openconnection):
    cur = openconnection.cursor()
    SQL = 'CREATE TABLE IF NOT EXISTS ' + ratingstablename + ' (userid INT, movieid INT, rating NUMERIC)'
    cur.execute(SQL)
    
    file = open(ratingsfilepath, 'r')
    for line in file:
        columns = line.split('::')
        userid = columns[0]
        movieid = columns[1]
        rating = columns[2]
        SQL = 'INSERT INTO '+ ratingstablename +'(userid, movieid, rating) VALUES('+ userid + ', '+ movieid + ', '+ rating +')'
        cur.execute(SQL)
    openconnection.commit()

def rangePartition(ratingstablename, numberofpartitions, openconnection):
    cur = openconnection.cursor()
    cur2 = openconnection.cursor()
    for x in range(0, numberofpartitions):
        SQL = 'CREATE TABLE IF NOT EXISTS range_part' + str(x) +' (userid INT, movieid INT, rating NUMERIC)'
        cur.execute(SQL)

    SQL = 'SELECT * FROM ' + ratingstablename
    cur.execute(SQL)
    row = cur.fetchone()
    while row is not None:
        userid = row[0]
        movieid = row[1]
        rating = row[2]
        if rating == 0:
            SQL = 'INSERT INTO range_part0 VALUES (' + str(userid) + ',' + str(movieid) + ',' + str(rating) +  ')' ## could simplfy because we know 0
            cur2.execute(SQL)
        else: 
            for x in range(0, numberofpartitions):
                if (rating > x * 5.0/numberofpartitions) and rating <= (x + 1) * 5.0/numberofpartitions:
                    SQL = 'INSERT INTO ' + 'range_part' + str(x % numberofpartitions) +' VALUES ('+ str(userid) + ',' + str(movieid) + ',' + str(rating) +  ')'
                    cur2.execute(SQL)
                    break
        row = cur.fetchone()
    
    SQL = 'CREATE TABLE IF NOT EXISTS number_of_partitions (partitions INT)'
    cur.execute(SQL)
    SQL = 'INSERT INTO number_of_partitions VALUES (' + str(numberofpartitions) + ')' 
    cur.execute(SQL)
    openconnection.commit()
    
def roundRobinPartition(ratingstablename, numberofpartitions, openconnection):
    cur = openconnection.cursor()
    cur2 = openconnection.cursor()
    for x in range(0, numberofpartitions):
        SQL = 'CREATE TABLE IF NOT EXISTS ' + 'rrobin_part' + str(x) +' (userid INT, movieid INT, rating NUMERIC)'
        cur.execute(SQL)
    openconnection.commit()
    SQL = 'SELECT * FROM ' + ratingstablename
    cur.execute(SQL)
    row = cur.fetchone()
    x = 0
    while row is not None:
        userid = row[0]
        movieid = row[1]
        rating = row[2]
        SQL = 'INSERT INTO ' + 'rrobin_part' + str(x % numberofpartitions) +' VALUES ('+ str(userid) + ',' + str(movieid) + ',' + str(rating) +  ')'
        cur2.execute(SQL)
        row = cur.fetchone()
        x += 1
            
    SQL = 'CREATE TABLE IF NOT EXISTS number_of_partitions (partitions INT)'
    cur.execute(SQL)
    SQL = 'INSERT INTO number_of_partitions VALUES (' + str(numberofpartitions) + ')' 
    cur.execute(SQL)
    openconnection.commit()

def roundrobininsert(ratingstablename, userid, itemid, rating, openconnection):
    cur = openconnection.cursor()
    
    SQL = 'SELECT partitions FROM number_of_partitions'
    cur.execute(SQL)
    number_of_partitions = cur.fetchone()[0]
    
    SQL = 'INSERT INTO ' + ratingstablename +' VALUES ('+ str(userid) + ', ' + str(itemid) + ', ' + str(rating) + ')'
    cur.execute(SQL)
    
    shortest = 0
    minvalue = 0
    maxvalue = 0
    
    for x in range(0, number_of_partitions):
        SQL = 'SELECT COUNT(*) FROM rrobin_part' + str(x)   ## did not need ratingstable name here
        cur.execute(SQL)
        rows = cur.fetchone()[0]
        if x == 0:
            minvalue = rows
        elif rows < minvalue:
            minvalue = rows
            shortest = x
        if rows > maxvalue:
            maxvalue = rows
    
    if maxvalue > minvalue:
        x = shortest
    else:
        x = 0
        
    SQL = 'INSERT INTO rrobin_part' + str(x) +' VALUES ('+ str(userid) + ',' + str(itemid) + ',' + str(rating) + ')'
    cur.execute(SQL)
    
    openconnection.commit()

def rangeinsert(ratingstablename, userid, itemid, rating, openconnection):
    cur = openconnection.cursor()
    
    SQL = 'SELECT partitions FROM number_of_partitions'
    cur.execute(SQL)
    number_of_partitions = cur.fetchone()[0]
    
    if rating == 0:
        SQL = 'INSERT INTO roundrobin_part0 VALUES ('+ str(userid) + ',' + str(itemid) + ',' + str(rating) +  ')'
        cur.execute(SQL)
    else:
        for x in range(0, number_of_partitions):
            if (rating > x * 5.0/number_of_partitions) and rating <= (x + 1) * 5.0/number_of_partitions:
                SQL = 'INSERT INTO ' + 'range_part' + str(x % number_of_partitions) +' VALUES ('+ str(userid) + ',' + str(itemid) + ',' + str(rating) +  ')'
                cur.execute(SQL)
                break
    openconnection.commit()

def createDB(dbname='dds_assignment'):
    """
    We create a DB by connecting to the default user and database of Postgres
    The function first checks if an existing base exists for a given name, elsecreates it.
    :return:None
    """
    # Connect to the default database    
    con = getOpenConnection(dbname='postgres')
    con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    
    # Check if an existing database with the same name exists
    cur.execute('SELECT COUNT(*) FROM pg_catalog.pg_database WHERE datname=\'%s\'' % (dbname,))
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute('CREATE DATABASE %s' % (dbname,))  # Create the database
    else:
        print 'A database named {0} already exists'.format(dbname)
    
def deletepartitionsandexit(openconnection):
    cur = openconnection.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    l = []
    for row in cur:
        l.append(row[0])
    for tablename in l:
        cur.execute("drop table if exists {0} CASCADE".format(tablename))
        
    cur.close()
    
def deleteTables(ratingstablename, openconnection):
    try:
        cursor = openconnection.cursor()
        if ratingstablename.upper() == 'ALL':
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()
            for table_name in tables:
                cursor.execute('DROP TABLE %s CASCADE' % (table_name[0]))
        else:
            cursor.execute('DROP TABLE %s CASCADE' % (ratingstablename))
        openconnection.commit()
    except psycopg2.DatabaseError, e:
        if openconnection:
            openconnection.rollback()
        print 'Error %s' % e
    except IOError, e:
        if openconnection:
            openconnection.rollback()
        print 'Error %s' % e
    finally:
        if cursor:
            cursor.close()