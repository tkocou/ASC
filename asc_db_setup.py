## Copyright 2023 by Thomas Kocourek, N4FWD

import os
import sqlite3
import sys
import ve_utilities as ut
import global_var as gv
import tkinter as tk
from tkinter import messagebox as mb

def setup():
    ## get the correct path for working directory
    ## get_environment() only sets up the path
    ## and returns it
    basic_dir = ut.set_environment()
    
    ## Change to correct directory
    os.chdir(basic_dir)
    ## set the flag
    db_result_flag = True
    
    ## set global path to database
    tmp_dir = os.path.join(basic_dir,gv.asc_dir)
    gv.asc_database = os.path.join(tmp_dir,"asc.db")
    
    if os.path.exists(gv.asc_database):
        ## do not erase an existing database
        ## reset the auto_update function
        db_connection = sqlite3.connect(gv.asc_database)
        db_cursor = db_connection.cursor()
        ## Inserting default auto_update values into the 'settings' table
        tmp_sql = ""
        for item in gv.settings_field_update_list:
            tmp_sql += item+'= ?, '
        tmp_sql = tmp_sql[:-2]
        values = tuple(gv.settings_default_update_values)
        sql = "UPDATE settings SET "+tmp_sql
        db_cursor.execute(sql,values)
        ## commit insert
        db_connection.commit()
    else:
        try:
            # else create a new database
            with open(gv.asc_database,mode="w"):pass

            ## build database ONLY if database did not exist
            
            db_connection = sqlite3.connect(gv.asc_database)
            db_cursor = db_connection.cursor()
            
            ## will be populated by data from website
            sql = """
                    CREATE TABLE IF NOT EXISTS ve_count (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    call TEXT NOT NULL UNIQUE, county TEXT NOT NULL, accredit TEXT NOT NULL, scount TEXT NOT NULL, state TEXT NOT NULL, tag TEXT);
                """
            sql_result = db_cursor.execute(sql)
            
            ## 'date' is for recording the last date the database was updated
            sql = """
                    CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY AUTOINCREMENT, yourcall TEXT ,
                    date TEXT , defaultState TEXT, autoflag TEXT , cronMin TEXT , cronHr TEXT , cronDom TEXT , cronMon TEXT , 
                    cronDow TEXT);
                """
            sql_result = db_cursor.execute(sql)
            
            ## commit both sql statements and create tables
            db_connection.commit() 
            
            ## Inserting default values into the 'settings' table
            rec_cols = ', '.join(gv.settings_field_list)
            q_marks = ','.join(list('?'*len(gv.settings_field_list)))
            values = tuple(gv.settings_default_values)
            sql = "INSERT INTO settings ("+rec_cols+") VALUES ("+q_marks+")"
            sql_result = db_cursor.execute(sql,values)
            ## commit insert
            db_connection.commit()
               
            db_cursor.execute("SELECT * FROM settings;")
            sql_records = db_cursor.fetchall()
            
            ## 've_count' table will be empty
            ## 'settings' table will have default values
            ## And close the new database
            #db_connection.close()
        except sqlite3.Error as er: ## in case of a SQL error, let's get more info
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
    ## And close the new database
    db_connection.close()    
    ## whether we were successful or not, return a flag
    return db_result_flag

