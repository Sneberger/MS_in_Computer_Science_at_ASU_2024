#!/usr/bin/python2.7
#
# Assignment2 Interface - Actually Assignment 4 in CSE 511 Spring 2021
#

import psycopg2
import os
import sys
# Donot close the connection inside this file i.e. do not perform openconnection.close()

def RangeQuery(ratingsTableName, ratingMinValue, ratingMaxValue, openconnection):
#roundrobin code
    cur = openconnection.cursor()
    SQL = 'SELECT * FROM RoundRobinRatingsMetadata'
    cur.execute(SQL)
    numberOfPartitions = cur.fetchone()[0]
    for x in range(0, numberOfPartitions):
        SQL = "SELECT '" + ratingsTableName + str(x) + "',userID, movieID, rating FROM " + ratingsTableName + str(x) + ' WHERE rating >= ' + str(ratingMinValue) + ' AND rating <= ' + str(ratingMaxValue) str(x) #+ ' WHERE rating > ' + str(ratingMinValue) + ' AND rating <= ' + str(ratingMaxValue)
        cur.execute(SQL)
        rows =  cur.fetchall()
        writeToFile('RangeQueryOut.txt', rows)
            
#range code
    cur = openconnection.cursor()
    SQL = 'SELECT Max(PartitionNum) FROM RangeRatingsMetadata WHERE MinRating <= ' + str(ratingMinValue)
    cur.execute(SQL)
    minPartitionNumber = cur.fetchone()[0]
    SQL = 'SELECT Min(PartitionNum) FROM RangeRatingsMetadata WHERE MaxRating >= ' + str(ratingMaxValue)
    cur.execute(SQL)
    maxPartitionNumber = cur.fetchone()[0]
    for x in range(minPartitionNumber, maxPartitionNumber + 1):
        SQL = "SELECT 'RangeRatingsPart" + str(x) + "',userID, movieID, rating FROM RangeRatingsPart" + str(x) + ' WHERE rating > ' + str(ratingMinValue) + ' AND rating <= ' + str(ratingMaxValue)
        cur.execute(SQL)
        rows = cur.fetchall()
        writeToFile('RangeQueryOut.txt', rows)


def PointQuery(ratingsTableName, ratingValue, openconnection):
#roundrobin code
    cur = openconnection.cursor()
    SQL = 'SELECT * FROM RoundRobinRatingsMetadata'
    cur.execute(SQL)
    numberOfParitions = cur.fetchone()[0]
    for x in range(0, numberOfParitions):
        SQL = "SELECT '" + ratingsTableName + str(x) + "',userID, movieID, rating FROM " + ratingsTableName + str(x) + ' WHERE rating = ' + str(ratingValue)
        cur.execute(SQL)
        rows =  cur.fetchall()
        writeToFile('PointQueryOut.txt', rows)
            
#range code
    cur = openconnection.cursor()
    SQL = 'SELECT Max(PartitionNum) FROM RangeRatingsMetadata WHERE MinRating <= ' + str(ratingValue)
    cur.execute(SQL)
    minPartitionNumber = cur.fetchone()[0]
    SQL = 'SELECT Min(PartitionNum) FROM RangeRatingsMetadata WHERE MaxRating >= ' + str(ratingValue)
    cur.execute(SQL)
    maxPartitionNumber = cur.fetchone()[0]
    for x in range(minPartitionNumber, maxPartitionNumber + 1):
        SQL = "SELECT 'RangeRatingsPart" + str(x) + "',userID, movieID, rating FROM RangeRatingsPart" + str(x) + ' WHERE rating = ' + str(ratingValue)
        cur.execute(SQL)
        rows =  cur.fetchall()
        writeToFile('PointQueryOut.txt', rows)


def writeToFile(filename, rows):
    f = open(filename, 'a')
    for line in rows:
        f.write(','.join(str(s) for s in line))
        f.write('\n')
    f.close()
