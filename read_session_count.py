## Copyright 2023 by Thomas Kocourek, N4FWD

import pandas as pd
import sqlite3
import global_var as gv
from datetime import date
import tkinter as tk
from tkinter import scrolledtext as st

def get_count(self,state):
    
    ## This function checks each line of data against the database
    ## either it inserts a new record, or it updates an existing record
    
    db_connection = sqlite3.connect(gv.asc_database)
    db_cursor = db_connection.cursor()

    db_cursor.execute("SELECT * FROM settings")
    setting = db_cursor.fetchone()
    
    website = gv.arrl_url + state
    today = []
    result = []
    update_flag = False
    
    ## windows needs this
    ## works okay in Linux
    data_frame = pd.read_html(website,flavor='html5lib')
    
    ## Convert data frame into a list of lists
    result = data_frame[0].to_numpy().tolist()
    length_list = len(result)
    ## result is a list of lists
    ## read each record from list of lists
    initial_tag = '0' ## set initial update tag
    for record in result:
        ve_record = []
        call_check = []
        
        ## we now have a list 'record' with [call,county,accreditation date,count]
        ## check if callsign exist in current table
        ## Parse the record to just the callsign
        call_record = record[0]
        call_check.append(call_record)
        
        db_cursor.execute("SELECT * FROM ve_count WHERE call = ?",tuple(call_check))
        record_check = db_cursor.fetchall()
        ## do we have an empty database?
        db_cursor.execute("SELECT COUNT(*) FROM ve_count")
        len_rc = db_cursor.fetchall()
        len_record_check = int(len_rc[0][0])
        
        ## 'record_check' is a list type set to 'None' if no record was fetched
        ## transfer over the record from the ARRL <- always contains VE data
        index = 0
        for item in gv.ve_input_list:
            ve_record.append(record[index])
            index += 1
        ## append the state
        ve_record.append(state)
        ## If we are doing an update and call is not in the database
        ## set the tag as an update before inserting into the database
        ## to prevent the auto-purge from removing the entry
        if update_flag: 
            initial_tag = '1'
        ve_record.append(initial_tag) ## set the update tag
        ## if a blank was returned, do an insert
        ## During an initial build of the database, "record_check" will always be set to None
        ## "len_record_check" will be zero for an empty database
        if record_check == None or len_record_check < 1: 
            index = 0
            ## Check each element in the list for missing data
            for element in ve_record:
                ## ran across an entry where the county was missing (index = 1)
                if type(element)  != str and index == 1:
                    ## substitute 'Not Available' for missing list element
                    ve_record[index] = "N-A"
                index += 1
            
            rec_cols = ', '.join(gv.ve_field_list)
            q_marks = ','.join(list('?'*len(gv.ve_field_list)))
            values = tuple(ve_record)
            sql = "INSERT INTO ve_count ("+rec_cols+") VALUES ("+q_marks+")"
            db_cursor.execute(sql,values)
            db_connection.commit()
            
        else: ## record exists, do an update
            update_flag = True
            tag_update = '1'
            values = tuple([record[3],tag_update,call_check[0]]) ## set
            sql = "UPDATE ve_count SET scount = ?, tag = ? WHERE call = ?"
            db_cursor.execute(sql,values)
            db_connection.commit()
    
    ## Only execute this next code if an update was accomplished
    
    if update_flag: ## Auto-Purge
        
        ## Do we have any records which where not updated?
        values = []
        values.append('0')
        values.append(state)
        db_cursor.execute("SELECT * FROM ve_count WHERE tag = ? and state = ?",tuple(values))
        ve_records = db_cursor.fetchall()
        ## Check if we have any and delete them
        if len(ve_records) > 0:
            sql_purge = "DELETE FROM ve_count WHERE call = ? and state = ?"
            for record in ve_records:
                values = []
                values.append(record[1])
                values.append(state)
                db_cursor.execute(sql_purge,tuple(values))
            db_connection.commit()
        ## Reset tags to '0' for next update
        db_cursor.execute("SELECT * FROM ve_count")
        ve_records = db_cursor.fetchall()
        sql_update = "UPDATE ve_count SET tag = ? WHERE call = ?"
        for record in ve_records:
            values = []
            values.append('0')
            values.append(record[1])
            db_cursor.execute(sql_update,tuple(values))
        db_connection.commit()
          
    ## update the date of this action in 'settings' table
    today_date = str(date.today())
    today.append(today_date)
    sql = "UPDATE settings SET date = ?"
    db_cursor.execute(sql,tuple(today))
    db_connection.commit()
    db_connection.close()
    
            
        