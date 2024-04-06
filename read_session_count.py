## Copyright 2023 by Thomas Kocourek, N4FWD

#import pandas as pd
import sqlite3
import global_var as gv
from datetime import date
import requests
from bs4 import BeautifulSoup

debug_analyze = False  # Is set to False in production. Is set to True for development.

def get_count(self,state):
    reject = ['Call','input','Location','select','Sort','option']

    ## This function checks each line of data against the database
    ## either it inserts a new record, or it updates an existing record
    
    db_connection = sqlite3.connect(gv.asc_database_path)
    db_cursor = db_connection.cursor()
    
    website = gv.arrl_url + state
    today = []
    result = []
    update_flag = False
    
    if debug_analyze:
        capture_filename = "transaction_dump.txt"
        dt = open(capture_filename,'a')
    
    html_text = requests.get(website).text

    ## Filter data from raw HTML
    soup = BeautifulSoup(html_text, 'html.parser')
    
    find_all = soup.find_all(['td'])
    
    capture_flag = False
    temp_list = []
    t_index = 0
    initial_tag = '0' ## set initial update tag
    ##
    ## a parsing loop to extract the VE info
    ##
    for line in find_all:
        if debug_analyze:
            line_txt = "Line in find_all: "+str(line)+'\n'
            dt.write(line_txt)
        line_txt = str(line) ## reset to line only
        ve_record = []
        call_check = []     
        reject_flag = False
        for check in reject:
            if check in line_txt:
                if debug_analyze:
                    line_check = f"check = {check}: reject_flag = True\n"
                    dt.write(line_check)
                reject_flag = True
        if reject_flag: ## loop back for another line of text
            if debug_analyze:
                dt.write("Reject_flag is set. Loop back.\n")
            continue
        if debug_analyze:
            temp_var = f"t_index = {t_index}\n"
            dt.write(temp_var)
        ## Looking for text containing the callsign and name of VE
        if line_txt[:4] == "<td>" and "</b>" in line_txt and line_txt[len(line_txt)-5:] == "</td>" and t_index == 0:
            output = line_txt[7:-5].replace('</b>','')
            capture_flag = True
            temp_list.append(output)
            if debug_analyze:
                temp_txt = f"capture_flag is True, CS output is {output}.\n"
                dt.write(temp_txt)
                dt.flush()
            t_index += 1
        ## Looking for additional information: county, accreditation and count
        elif line_txt[:4] == "<td>" and line_txt[len(line_txt)-5:] == "</td>" and capture_flag and t_index <3:
            output = line_txt[4:len(line_txt)-5]
            temp_list.append(output)
            if debug_analyze:
                temp_txt = f"Additional information is {output}. Saving.\n"
                dt.write(temp_txt)
            t_index += 1
        ## All data for the VE has been captured, reset some variables
        elif t_index > 2:
            output = line_txt[4:len(line_txt)-5]
            temp_list.append(output)
            capture_flag = False
            t_index = 0
            result.append(temp_list)
            if debug_analyze:
                dt.write("\n\nCapture_flag is False. Finished and saving: "+str(temp_list)+" ....Next data\n\n")
                dt.flush()
            temp_list = []
    ## Now result is a list of lists
    for record in result: 
        ## we now have a list 'record' with [call,county,accreditation date,count]
        ## check if callsign exist in current table
        ## Parse the record to just the callsign
        ##
        ## Make sure the list variable is empty
        call_check = []
        call_check.append(record[0])
        db_cursor.execute("SELECT * FROM ve_count WHERE call = ?",tuple(call_check))
        callsign_check = db_cursor.fetchall()
        ## do we have an empty database?
        db_cursor.execute("SELECT COUNT(*) FROM ve_count")
        len_rc = db_cursor.fetchall()
        len_db_check = int(len_rc[0][0])
        ## 'callsign_check' is a list type set to '[]' if no record was fetched
        ## transfer over the record from the ARRL <- always contains VE data
        index = 0
        ve_record = []
        for item in gv.ve_input_list:
            ## Set up a error trap in case of missing county data
            try:
                if index == 3:
                    ve_record.append(int(record[index]))
                else:
                    ve_record.append(record[index])
                index += 1
            ## correct for missing county data
            except Exception:
                temp_list = []
                temp_list.append(ve_record[0]) # append callsign
                temp_list.append("N/A") # add missing county
                temp_list.append(ve_record[1]) # append accreditation
                temp_list.append(ve_record[2]) # append session count
                ve_record = temp_list
        ## append the state
        ve_record.append(state)
        ## If we are doing an update and call is not in the database
        ## set the tag as an update before inserting into the database
        ## to prevent the auto-purge from removing the entry
        if update_flag: 
            initial_tag = '1'
        ve_record.append(initial_tag) ## set the update tag
        ## if a blank was returned, do an insert
        ## During an initial build of the database, "callsign_check" will always be set to []
        ## "len_db_check" will be zero for an empty database
        
        ## Do we have an empty db or is the callsign not in the db yet?
        if len_db_check < 1 or callsign_check == []:
            try:
                rec_cols = ', '.join(gv.ve_field_list)
                q_marks = ','.join(list('?'*len(gv.ve_field_list)))
                values = tuple(ve_record)
                sql = "INSERT INTO ve_count ("+rec_cols+") VALUES ("+q_marks+")"
                db_cursor.execute(sql,values)
            except Exception: ## catch DB check slip-ups
                ## the callsign does exist, switching to an update
                update_flag = True
                tag_update = '1'
                values = tuple([int(record[3]),tag_update,call_check[0]]) ## set
                sql = "UPDATE ve_count SET scount = ?, tag = ? WHERE call = ?"
                db_cursor.execute(sql,values)
            db_connection.commit()
            
        else: ## record exists, do an update
            update_flag = True
            tag_update = '1'
            values = tuple([int(record[3]),tag_update,call_check[0]]) ## set
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
    if debug_analyze:
        dt.close()
            
        