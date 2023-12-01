## Copyright 2023 by Thomas Kocourek, N4FWD

import os
import sqlite3
import sys
import ve_utilities as ut
import global_var as gv
import tkinter as tk
from tkinter import ttk
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
    glaarg_update = False
    
    ## set path to databases
    tmp_dir = os.path.join(basic_dir,gv.asc_dir)
    gv.asc_database_path = os.path.join(tmp_dir,gv.asc_database_name)
    gv.temp_database_path = os.path.join(tmp_dir,gv.temp_database_name)
    gv.temp_fetch_path = os.path.join(tmp_dir,gv.ARRL_fetch_state)
    
    if os.path.exists(gv.asc_database_path): ## Do we have an existing database?
        ## Yes.
        ## do a check if old style or new glaarg style
        ## if the database is old style or corrupted, then reset the database
        ##
        
        ## sqlite_master is the root definition holding the structure of the database
        ##
        ## In the next line, we are referencing the database root asking about a 
        ## particular table structure
        ##
        
        sql = "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'glaarg_count'" 

        db_connection = sqlite3.connect(gv.asc_database_path)
        db_cursor = db_connection.cursor()
        db_cursor.execute(sql)
        tested_value = db_cursor.fetchone()
        if tested_value == None: ## No table labeled as 'glaarg_count'
            ## remove old table and remind user
            os.remove(gv.asc_database_path)
            mb.showinfo("Alert","Database has been flushed.\nExiting the ASC-DB program to rebuild the database.\nRemember to run Set Defaults.\n")
            if os.path.exists(gv.temp_fetch_path):
                os.remove(gv.temp_fetch_path)
            db_result_flag = False
            return db_result_flag
        
    else:
        ## no existing database
        try:
            ## create a new database
            ##
            with open(gv.asc_database_path,mode="w"):pass
            
            db_connection = sqlite3.connect(gv.asc_database_path)
            db_cursor = db_connection.cursor()
            
            ## will be populated by data from websites
            sql = """
                    CREATE TABLE IF NOT EXISTS ve_count (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    call TEXT NOT NULL UNIQUE, county TEXT NOT NULL, accredit TEXT NOT NULL, scount INTEGER NOT NULL, state TEXT NOT NULL, tag TEXT);
                """
            sql_result = db_cursor.execute(sql)
            
            sql = """
                    CREATE TABLE IF NOT EXISTS glaarg_count (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ve_num TEXT NOT NULL UNIQUE, csign TEXT NOT NULL, ve_name TEXT NOT NULL, sess_ct INTEGER NOT NULL, helped INTEGER NOT NULL, overseen INTEGER NOT NULL,
                    new_lic INTEGER NOT NULL, upgrades INTEGER NOT NULL, tag TEXT);
                """
            sql_result = db_cursor.execute(sql)
            
            ## 'date' is for recording the last date the database was updated
            ## ditto for glaarg via 'gl_date'
            
            ##
            ## Add in entry for glaarg initial/update 'date'
            ##
            sql = """
                    CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY AUTOINCREMENT, yourcall TEXT ,
                    date TEXT , gl_date TEXT, defaultState TEXT, autoflag TEXT , cronMin TEXT , cronHr TEXT , cronDom TEXT , cronMon TEXT , 
                    cronDow TEXT);
                """
            sql_result = db_cursor.execute(sql)
            
            ## commit both sql statements and create tables
            db_connection.commit() 
            
            ## Inserting default values into the 'settings' table
            rec_cols = ', '.join(gv.settings_field_list_glaarg)
            q_marks = ','.join(list('?'*len(gv.settings_field_list_glaarg)))
            values = tuple(gv.settings_default_values_glaarg)
            sql = "INSERT INTO settings ("+rec_cols+") VALUES ("+q_marks+")"
            sql_result = db_cursor.execute(sql,values)
            ## commit insert
            db_connection.commit()
               
            db_cursor.execute("SELECT * FROM settings;")
            sql_records = db_cursor.fetchall()
            
        except sqlite3.Error as er: ## in case of a SQL error, let's get more info
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
            db_result_flag = False
    ## And close the new database
    db_connection.close()
    
    ## whether we were successful or not, return a flag
    return db_result_flag

