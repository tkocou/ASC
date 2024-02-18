## Copyright 2023 by Thomas Kocourek, N4FWD

import pandas as pd
import sqlite3
import global_var as gv
from datetime import date
import tkinter as tk
#from tkinter import scrolledtext as st
#from tkinter import messagebox as mb

def get_count(self):
    
    ## This function checks each line of data against the database
    ## either it inserts a new record, or it updates an existing record
    
    db_connection = sqlite3.connect(gv.asc_database_path)
    db_cursor = db_connection.cursor()

    db_cursor.execute("SELECT * FROM settings")
    #setting = db_cursor.fetchone()
    
    website = gv.glaarg_url 
    today = []
    result = []
    update_flag = False
    
    ## windows needs this
    ## works okay in Linux
    try:
        data_frame = pd.read_html(website,flavor='html5lib')
    except Exception as e:
        print("Error on read_html: ",str(e))
        return True
    ## Convert data frame into a list of lists
    try:
        result = data_frame[1].to_numpy().tolist()
        #length_list = len(result)
    except Exception as e:
        print("Error on data_frame: ",str(e))
        return
    ## result is a list of lists
    ## read each record from list of lists
    with open("glarg_dump.txt","w") as du:
        du.write(str(result))
    initial_tag = '0' ## set initial update tag
    for record in result:
        ve_record = []
        call_check = []
        ## we now have a list 'record' with ['ve_num','csign','ve_name','sess_ct','helped','overseen','new_lic','upgrades']
        ## check if callsign exist in current table
        ## Parse the record to just the callsign
        call_record = record[1]
        call_check.append(call_record)
            
        db_cursor.execute("SELECT * FROM glaarg_count WHERE csign = ?",tuple(call_check))
        callsign_check = db_cursor.fetchall()
        
        ## do we have an empty database?
        db_cursor.execute("SELECT COUNT(*) FROM glaarg_count")
        len_rc = db_cursor.fetchall()
        len_db_check = int(len_rc[0][0])
        
        ## 'callsign_check' is a list type set to 'None' if no record was fetched
        ## transfer over the record from the GLAARG <- always contains VE data
        index = 0
        for item in gv.gl_input_list:
            if index > 2:
                ve_record.append(int(record[index]))
            else:
                ve_record.append(record[index])
            index += 1
        
        ## If we are doing an update and call is not in the database
        ## set the tag as an update before inserting into the database
        ## to prevent the auto-purge from removing the entry
        if update_flag: 
            initial_tag = '1'
        ve_record.append(initial_tag) ## set the update tag
        ## if a blank was returned, do an insert
        ## During an initial build of the database, "record_check" will always be set to None
        ## "len_db_check" will be zero for an empty database
            
        ## add a record if the db is empty or if the callsign is not already in the database
        if len_db_check < 1 or callsign_check == []: 
            ## Add new record to DB
            try:
                rec_cols = ', '.join(gv.gl_field_list)
                q_marks = ','.join(list('?'*len(gv.gl_field_list)))
                values = tuple(ve_record)
                sql = "INSERT INTO glaarg_count ("+rec_cols+") VALUES ("+q_marks+")"
                db_cursor.execute(sql,values)
                text = "Adding to database, VE is " + str(ve_record[1])+ '.\n'
                self.result_text.insert(tk.END,text)
                self.result_text.yview(tk.END)
            except Exception: ## catch duplicate in case of a DB check slip-up
                ## the callsign does exist, switching to an update
                update_flag = True
                tag_update = '1'
                values = tuple([int(record[3]),int(record[4]),int(record[5]),int(record[6]),int(record[7]),tag_update,call_check[0]]) ## set
                sql = "UPDATE glaarg_count SET sess_ct = ?, helped = ?, overseen = ?, new_lic = ?, upgrades = ?, tag = ? WHERE csign = ?"
                db_cursor.execute(sql,values)
                text = "Updating database, VE is " + str(call_check[0])+ '.\n'
                self.result_text.insert(tk.END,text)
                self.result_text.yview(tk.END)
            db_connection.commit()
            self.update_idletasks()
            
        else: ## record exists, do an update
            update_flag = True
            tag_update = '1'
            values = tuple([int(record[3]),int(record[4]),int(record[5]),int(record[6]),int(record[7]),tag_update,call_check[0]]) ## set
            sql = "UPDATE glaarg_count SET sess_ct = ?, helped = ?, overseen = ?, new_lic = ?, upgrades = ?, tag = ? WHERE csign = ?"
            db_cursor.execute(sql,values)
            db_connection.commit()
            text = "Updating database, VE is " + str(call_check[0])+ '.\n'
            self.result_text.insert(tk.END,text)
            self.result_text.yview(tk.END)
            self.update_idletasks()
            
    ## Only execute this next code if an update was accomplished
    
    if update_flag: ## Auto-Purge
        
        ## Do we have any records which where not updated?
        values = []
        values.append('0')
        db_cursor.execute("SELECT * FROM glaarg_count WHERE tag = ? ",tuple(values))
        ve_records = db_cursor.fetchall()
        ## Check if we have any and delete them
        if len(ve_records) > 0:
            sql_purge = "DELETE FROM glaarg_count WHERE csign = ? "
            for record in ve_records:
                values = []
                ## glaarg callsign column accounting for row number at column 0
                ## ['ve_num','csign','ve_name','sess_ct','helped','overseen','new_lic','upgrades']
                values.append(record[2])
                db_cursor.execute(sql_purge,tuple(values))
            db_connection.commit()
        ## Reset tags to '0' for next update
        db_cursor.execute("SELECT * FROM glaarg_count")
        ve_records = db_cursor.fetchall()
        sql_update = "UPDATE glaarg_count SET tag = ? WHERE csign = ?"
        for record in ve_records:
            values = []
            values.append('0')
            values.append(record[2])
            db_cursor.execute(sql_update,tuple(values))
        db_connection.commit()
          
    ## update the date of this action in 'settings' table
    today_date = str(date.today())
    today.append(today_date)
    sql = "UPDATE settings SET gl_date = ?"
    db_cursor.execute(sql,tuple(today))
    db_connection.commit()
    db_connection.close()
    return False
            
        