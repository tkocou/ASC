## Copyright 2023 by Thomas Kocourek, N4FWD

import pandas as pd
import sqlite3
import global_var as gv
from datetime import date
import tkinter as tk
import os


def get_count(self):
    
    logging = os.path.join(gv.base_rpt_dir,"a_log.txt")
    ## log_it() is an appending logging function
    ## remove a pre-existing file for a clean output
    if os.path.isfile(logging):
        os.remove(logging)
        
    web_dump = os.path.join(gv.base_rpt_dir,"glarg_dump.txt")
    
    ## This function checks each line of data against the database
    ## either it inserts a new record, or it updates an existing record
    
    db_connection = sqlite3.connect(gv.asc_database_path)
    db_cursor = db_connection.cursor()
    
    website = gv.glaarg_url 
    today = []
    result = []
    update_flag = False
    
    ## windows needs this
    ## works okay in Linux
    try:
        data_frame = pd.read_html(website,flavor='html5lib')
    except Exception as e:
        txt = "Error on read_html: " + str(e)+'\n'
        log_it(txt)
        return True
    ## Convert data frame into a list of lists
    try:
        result = data_frame[1].to_numpy().tolist()
    except Exception as e:
        txt = "Error on data_frame: " + str(e)+'\n'
        log_it(txt)
        return True
    ## result is a list of lists
    ## read each record from list of lists
    ## reading the website was successful
    web_dump = os.path.join(gv.base_rpt_dir,"glarg_dump.txt")
    if  len(result) > 0:
        with open(web_dump,"w") as du:
            du.write(str(result))
    ## website is down, using last record from GLAARG
    else:
        t_result = ""
        try:
            with open(web_dump,"r") as du:
               temp = du.read()
            ## swap a ' for a "
            for char in temp:
                if char == "'":
                    char = '"'
                    t_result += char
                    continue
                elif char == '"':
                    char = "'"
                    t_result += char
                    continue
                t_result += char
                
            ## change list separators from , to |
            s_result = t_result[1:-1].replace('], [',']| [')
            result = s_result.split('|')
            
            ## "result" is now a list of stringified lists 
            temp_list = []
            ## split each element string into a list
            for item in result:
                ## remove the brackets
                t_string = item[1:-1]
                ## break up string into a list
                t_list = t_string.split(',')
                
                ## a side effect of the last split is the name becomes 2 data fields
                ## clean up the data in the record
                t_temp = []
                if t_list[0][0:1] == '[':
                    t_temp.append(t_list[0][2:-1])
                else:
                    t_temp.append(t_list[0][1:-1])
                if t_list[1] == ' nan':
                    t_temp.append('nan')
                else:
                    t_temp.append(t_list[1][2:-1])
                if t_list[3][1:].isdigit():
                    t_temp.append(t_list[2][2:-1])
                    ## append rather than combine elements
                    t_temp.append(t_list[3][1:])
                    for x in range(4,8): ## finish appending numbers
                        t_temp.append(t_list[x][1:])
                else:
                    ## combine elements and append
                    name = t_list[2][2:]+','+t_list[3][:-1]
                    t_temp.append(name)
                    for x in range(4,9): ## finish appending numbers
                        t_temp.append(t_list[x][1:])
                txt = "cleaned up record: "+str(t_temp)+'\n\n'
                log_it(txt)
                
                ## t_list now holds a proper list structure
                t_list = t_temp
                ## build a list of lists
                temp_list.append(t_list)
            
            ## each sub-list is now joined as a list of lists
            result = temp_list
        except Exception as e:
            txt = "Error on reading glaarg_dump: " + str(e)+'\n'
            log_it(txt)
            return True
    initial_tag = '0' ## set initial update tag
    
    txt = "Number of records: "+str(len(result))+'\n'
    log_it(txt)
    
    record_count = 0
    
    for record in result: ## result = list of lists
        
        ve_record = []
        call_check = []
        
        #txt = "record to write to DB: "+str(record)+'\n'
        #log_it(txt)
        #### Good so far ####
        
        ## we now have a list 'record' with ['ve_num','csign','ve_name','sess_ct','helped','overseen','new_lic','upgrades']
        ## check if callsign exist in current table
        ## Parse the record to just the callsign
        
        call_record = record[0]
        call_check.append(call_record)
            
        db_cursor.execute("SELECT * FROM glaarg_count WHERE ve_num = ?",tuple(call_check))
        callsign_check = db_cursor.fetchall()
        #try:
        #    txt = "Doing a callsign_check for: " + call_record + " yields "+ str(callsign_check) + '\n'
        #except Exception:
        #    txt = "Doing a callsign_check for: NAN yields "+ str(callsign_check) + '\n'
        #log_it(txt)
        #### Good so far ####
        
        
        ## do we have an empty database?
        db_cursor.execute("SELECT COUNT(*) FROM glaarg_count")
        len_rc = db_cursor.fetchall()
        len_db_check = int(len_rc[0][0])
        
        ## 'callsign_check' is a list type set to 'None' if no record was fetched
        ## transfer over the record from the GLAARG <- always contains VE data
        ##
        ## Some records from GLAARG are missing data
        ## Normally there are 8 data items
        index = 0
        for item in gv.gl_input_list:
            if index > 2:
                ve_record.append(int(record[index]))
            else:
                if isinstance(record[index],str):
                    ve_record.append(record[index])
                else:
                    tmp_str = "None"
                    ve_record.append(tmp_str)
                
            index += 1
        
        #txt = "check ve_record: "+str(ve_record)+'\n'
        #log_it(txt)
        #### Good so far ####
        
            
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
                
                #txt = "INSERT op: "+str(values)+'\n'
                #log_it(txt)
                #### Good ####
                
                db_cursor.execute(sql,values)
                db_connection.commit()
                
                record_count += 1
                
                #db_cursor.execute("SELECT * FROM glaarg_count WHERE ve_num = ?",tuple(call_check))
                #callsign_check = db_cursor.fetchall()
                
                #txt = "Checking if INSERT was successful: "+ str(callsign_check)+'\n'
                #log_it(txt)
                #### Good ####
                
                text = "Adding to database, VE is " + str(ve_record[1])+ '.\n'
                self.result_text.insert(tk.END,text)
                self.result_text.yview(tk.END)
            except sqlite3.Error as er: ## catch NAN records
                
                
                txt = "SQLite_error:  ".join(er.args)
                log_it(txt)
                
                txt = "Exception class is: "+str(er.__class__)
                log_it(txt)
                
                txt = "exception record: "+str(record)+'\n\n'
                log_it(txt)
                
            db_connection.commit()
            self.update_idletasks()
            
        else: ## record exists, do an update
            update_flag = True
            tag_update = '1'
            
            #txt = "else UPDATE op: "+str(values)+'\n'
            #log_it(txt)
            #### Good ####
            
            values = tuple([int(record[3]),int(record[4]),int(record[5]),int(record[6]),int(record[7]),tag_update,record[0]]) ## set
            sql = "UPDATE glaarg_count SET sess_ct = ?, helped = ?, overseen = ?, new_lic = ?, upgrades = ?, tag = ? WHERE ve_num = ?"
            db_cursor.execute(sql,values)
                
            db_connection.commit()
            
            
            text = "Updating database, VE is " + str(record[1])+ '.\n'
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
            sql_purge = "DELETE FROM glaarg_count WHERE ve_num = ? "
            for record in ve_records:
                values = []
                ## glaarg callsign column accounting for row number at column 0
                ## ['ve_num','csign','ve_name','sess_ct','helped','overseen','new_lic','upgrades']
                values.append(record[1])
                db_cursor.execute(sql_purge,tuple(values))
        ## Reset tags to '0' for next update
        db_cursor.execute("SELECT * FROM glaarg_count")
        ve_records = db_cursor.fetchall()
        sql_update = "UPDATE glaarg_count SET tag = ? WHERE ve_num = ?"
        for record in ve_records:
            values = []
            values.append('0')
            values.append(record[1])
            db_cursor.execute(sql_update,tuple(values))
        db_connection.commit()
    
    txt = "number of records inserted: "+str(record_count)+'\n'
    log_it(txt)
    
    ## update the date of this action in 'settings' table
    today_date = str(date.today())
    today.append(today_date)
    sql = "UPDATE settings SET gl_date = ?"
    db_cursor.execute(sql,tuple(today))
    db_connection.commit()
    db_connection.close()
    return False
            
def log_it(text): ## a quick logging dump
    
    logging = os.path.join(gv.base_rpt_dir,"a_log.txt")
    with open(logging,'a') as li:
        ## make sure we are dealing with a string
        if not text.isalpha():
            text = str(text)
        li.write(text)