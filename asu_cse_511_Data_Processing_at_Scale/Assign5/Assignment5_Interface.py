#!/usr/bin/python2.7
#
# Assignment3 Interface
#

import psycopg2
import os
import sys
import threading

# Do not close the connection inside this file i.e. do not perform openconnection.close()

DATABASE_NAME = 'dds_assignment'
RANGE_TABLE_PREFIX = 'rangeratingspart'
TEMP_TABLE_PREFIX = 'temptable'

def getOpenConnection(user='postgres', password='1234', dbname='MovieLens'):
    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='localhost' password='" + password + "'")

def sort(PartitionName, TempTable, sortColumn, openconnection):
    cur = openconnection.cursor()
#    SQL = "SELECT column_name FROM information_schema.columns WHERE table_name = " + PartitionName
    SQL = "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '" + PartitionName + "'"
    cur.execute(SQL)
    print SQL
    columnCount = cur.fetchone()[0]
    print "number of columns = " + str(columnCount)
    if columnCount == 3:
#        SQL = 'INSERT INTO ' + TempTable + ' (SELECT Movieid, Title, Genre FROM ' + PartitionName + ' ORDER BY ' + sortColumn + ' ASC)'
        SQL = 'INSERT INTO {} (SELECT Movie_id, Title, Genre FROM {} ORDER BY {} ASC)'.format(TempTable, PartitionName, sortColumn)
        cur.execute(SQL)
    if columnCount == 4:
#        SQL = 'INSERT INTO ' + TempTable + ' (SELECT UserID, MovieID, Rating, Timestamp FROM ' + PartitionName + ' ORDER BY ' + sortColumn + ' ASC)'
        SQL = 'INSERT INTO {} (SELECT UserID, Movieid, Rating, Timestamp FROM {} ORDER BY {} ASC)'.format(TempTable, PartitionName, sortColumn)
        cur.execute(SQL)
    openconnection.commit()
    print SQL

class mySortThread (threading.Thread):
    def __init__(self, name, PartitionName, TempTable, sortColumn, openconnection):     #threadID, name, counter):
        threading.Thread.__init__(self)
        self.name = name
        self.PartitionName = PartitionName
        self.TempTable = TempTable
        self.sortColumn = sortColumn
        self.openconnection = openconnection
    def run(self):
        print "Starting " + self.name
        sort(self.PartitionName, self.TempTable, self.sortColumn, self.openconnection)
        print "Exiting " + self.name

# Donot close the connection inside this file i.e. do not perform openconnection.close()
def ParallelSort (InputTable, SortingColumnName, OutputTable, openconnection):
    #divide InputTable into 5 partitions
    rangePartition(InputTable, SortingColumnName, 5, openconnection)
    
    #create output table
    cur = openconnection.cursor()
    SQL = 'CREATE TABLE IF NOT EXISTS ' + OutputTable + ' AS SELECT * FROM ' + InputTable + ' WITH NO DATA'
    cur.execute(SQL)
    openconnection.commit()
    print SQL

    for x in range(0, 5):
        cur = openconnection.cursor()
        SQL = 'CREATE TABLE IF NOT EXISTS TempTable' + str(x) + ' AS SELECT * FROM ' + InputTable + ' WITH NO DATA'
        cur.execute(SQL)
        print SQL
        openconnection.commit()
        threadx = mySortThread('thread' + str(x), RANGE_TABLE_PREFIX + str(x), TEMP_TABLE_PREFIX + str(x), SortingColumnName, openconnection)
        threadx.start()
        
    for x in range(0, 5):
        cur = openconnection.cursor()
        SQL = 'INSERT INTO ' + OutputTable + ' (SELECT userid, movieid, rating FROM ' + TEMP_TABLE_PREFIX + str(x) + ')'
        cur.execute(SQL)
        openconnection.commit()
        print SQL

def rangePartition(ratingstablename, Table1JoinColumn, numberofpartitions, openconnection):
    name = RANGE_TABLE_PREFIX
    try:
        cursor = openconnection.cursor()
        cursor.execute("select * from information_schema.tables where table_name='%s'" % ratingstablename)
        if not bool(cursor.rowcount):
            print "Please Load Ratings Table first!!!"
            return
        cursor.execute("CREATE TABLE IF NOT EXISTS RangeRatingsMetadata(PartitionNum INT, MinRating REAL, MaxRating REAL)")
        SQL = 'SELECT Min(' + Table1JoinColumn + ') FROM ' + ratingstablename
        cursor.execute(SQL)
        MinRating = cursor.fetchone()[0]
        SQL = 'SELECT Max(' + Table1JoinColumn + ') FROM ' + ratingstablename
        cursor.execute(SQL)
        MaxRating = cursor.fetchone()[0]
        step = (MaxRating - MinRating) / (float)(numberofpartitions)
        i = 0;
        while i < numberofpartitions:
            newTableName = name + `i`
            if ratingstablename == 'movies':
                cursor.execute("CREATE TABLE IF NOT EXISTS " + newTableName + "(MovieID INT, Title VARCHAR(100), Genre VARCHAR(100))")
            if ratingstablename == 'ratings':
                cursor.execute("CREATE TABLE IF NOT EXISTS " + newTableName + "(UserID INT, MovieID INT, Rating REAL, Timestamp INT)")
            i += 1;

        i = 0;
        while MinRating < MaxRating:
            lowerLimit = MinRating
            upperLimit = MinRating + step
            if lowerLimit < 0:
                lowerLimit = 0.0

            if lowerLimit == 0.0:
                cursor.execute("SELECT * FROM " + ratingstablename + " WHERE " + Table1JoinColumn + " >= " + str(lowerLimit) + " AND " + Table1JoinColumn + " <= " + str(upperLimit)) #Table1JoinColumn + " <= %f" % (ratingstablename, lowerLimit, upperLimit))
                rows = cursor.fetchall()
                newTableName = name + `i`
                for row in rows:
                    if ratingstablename == 'movies':
                        cursor.execute("INSERT INTO %s(MovieID, Title, Genre) VALUES(%d, '%s', '%s')" % (newTableName, row[0], row[1], row[2]))
                    elif ratingstablename == 'ratings':
                        cursor.execute("INSERT INTO %s(UserID, MovieID, Rating, Timestamp) VALUES(%d, %d, %f, %d)" % (newTableName, row[0], row[1], row[2], row[3]))

            if lowerLimit != 0.0:
                cursor.execute("SELECT * FROM " + ratingstablename + " WHERE " + Table1JoinColumn + " > " + str(lowerLimit) + " AND " + Table1JoinColumn + " <= " + str(upperLimit)) #+ Table1JoinColumn + " > %f AND " + Table1JoinColumn + " <= %f" % (ratingstablename, lowerLimit, upperLimit))
                rows = cursor.fetchall()
                newTableName = name + `i`
                for row in rows:
                    if ratingstablename == 'movies':
                        cursor.execute("INSERT INTO %s(MovieID, Title, Genre) VALUES(%d, '%s', '%s')" % (newTableName, row[0], row[1], row[2]))
                    elif ratingstablename == 'ratings':
                        cursor.execute("INSERT INTO %s(UserID, MovieID, Rating, Timestamp) VALUES(%d, %d, %f, %d)" % (newTableName, row[0], row[1], row[2], row[3]))
            MinRating = upperLimit
            i += 1;

        openconnection.commit()
    except psycopg2.DatabaseError, e:
        if openconnection:
            openconnection.rollback()
        print 'Error %s' % e
        sys.exit(1)
    except IOError, e:
        if openconnection:
            openconnection.rollback()
        print 'Error %s' % e
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()

def join(PartitionName, InputTable1, InputTable2, Table1JoinColumn, Table2JoinColumn, OutputTable, openconnection):
    cur = openconnection.cursor()
    SQL = 'INSERT INTO ' + OutputTable + ' (SELECT ' + Table1JoinColumn + ' , ' + Table2JoinColumn + ' FROM ' + PartitionName + ' INNER JOIN ' + InputTable2 + ' ON ' + Table1JoinColumn + ' = ' + Table2JoinColumn + ')'
    print SQL
    cur.execute(SQL)
    openconnection.commit()
    
    if cur:
        cur.close()
        
class myJoinThread (threading.Thread):
    def __init__(self, name, PartitionName, InputTable1, InputTable2, Table1JoinColumn, Table2JoinColumn, OutputTable, openconnection):     #threadID, name, counter):
        threading.Thread.__init__(self)
        self.name = name
        self.PartitionName = PartitionName
        self.InputTable1 = InputTable1
        self.InputTable2 = InputTable2
        self.Table1JoinColumn = Table1JoinColumn
        self.Table2JoinColumn = Table2JoinColumn
        self.OutputTable = OutputTable
        self.openconnection = openconnection
    def run(self):
        print "Starting " + self.name
        join(self.PartitionName, self.InputTable1, self.InputTable2, self.Table1JoinColumn, self.Table2JoinColumn, self.OutputTable, self.openconnection)
        print "Exiting " + self.name
        
def ParallelJoin (InputTable1, InputTable2, Table1JoinColumn, Table2JoinColumn, OutputTable, openconnection):
    #divide InputTable1 into 5 partitions
#    hashPartition(InputTable1, Table1JoinColumn, 5, openconnection)
    rangePartition(InputTable1, Table1JoinColumn, 1, openconnection)
    
    cur = openconnection.cursor()
    SQL = 'CREATE TABLE IF NOT EXISTS ' + OutputTable + ' AS SELECT * FROM ' + InputTable1 + ' INNER JOIN ' + InputTable2 + ' ON ' + InputTable1 + '.' + Table1JoinColumn + ' = ' + InputTable2 + '.' + Table2JoinColumn + ' WITH NO DATA'
#    SQL = 'CREATE TABLE IF NOT EXISTS OutputTable AS SELECT * FROM ' + InputTable1 + ' , ' + InputTable2 + ' WITH NO DATA'
    print SQL
    cur.execute(SQL)
    openconnection.commit()
    
    if cur:
        cur.close()

    for x in range(0, 5):
        threadx = myJoinThread('thread' + str(x), RANGE_TABLE_PREFIX + str(x), InputTable1, InputTable2, Table1JoinColumn, Table2JoinColumn, OutputTable, openconnection)
        threadx.start()
            
#testing
if __name__ == '__main__':
    if len(sys.argv) > 1:
        numberofpartitions = int(sys.argv[1])
    con = getOpenConnection()
    ParallelSort ('movies', 'movie_id', 'Para_Sorted', con)
#    ParallelJoin ('movies', 'ratings', 'movie_id', 'movieid', 'testoutput', con)
    print 'reached end'
    con.close()