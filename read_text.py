## Copyright 2023 by Thomas Kocourek, N4FWD

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb

import os
import sqlite3
import global_var as gv

def read_text_file(self):
    callsigns = []
    cs_read = ""
    self.result_text.delete(1.0,tk.END)
    file_list = os.listdir(gv.base_rpt_dir)
    for file_line in file_list:
        cs_list = []
        path_to_file = os.path.join(gv.base_rpt_dir,file_line)
        with open(path_to_file,'r') as fh:
            cs_read = fh.read()
        cs_list = cs_read.split('\n')
        callsigns.extend(cs_list)
    for call in callsigns:
        tmp_list = []
        sql_text = "SELECT * FROM ve_count WHERE call LIKE ?"
        self.lookup_callsign = call
        self.exact_matched = False
        lup_callsign = '%'+self.lookup_callsign.upper()+'%'
        db_connection = sqlite3.connect(gv.asc_database)
        db_cursor = db_connection.cursor()
        
        tmp_list.append(lup_callsign)
        try:
            if len(call) > 0: ## might have an empty element in the list
                ## Do SQL query only if 'call' is not empty
                db_cursor.execute(sql_text,tuple(tmp_list))
                record_check = db_cursor.fetchall()
                self.exact_matched = True
            else:
                record_check = []
        except:
            record_check = None
        
        if len(record_check) > 1:  ## multiple match
            self.exact_matched = False  
            sql_match = 'SELECT * FROM ve_count WHERE id = ?'
            tmp_list = []
            
            for record in record_check:
                exact_match = record[1].split(' ')
                if exact_match[0] == self.lookup_callsign.upper():
                    self.exact_matched = True
                    tmp_list.append(record[0])
                    try:
                        db_cursor.execute(sql_match,tuple(tmp_list))
                        record_check = db_cursor.fetchall()
                    except:
                        record_check = None
                    break
        
        db_connection.close()
        
        if len(call) > 0:
            if record_check == None or self.exact_matched == False or record_check == []:
                text = "\nCallsign {} was not found!\n".format(self.lookup_callsign.upper())+'\n'
                self.result_text.insert(tk.END,text)
            else:    
                for r in record_check:
                    text_line = "Count:{}, Call:{}, County:{}, State:{}, Accredited:{}\n".format(r[4],r[1],r[2],r[5],r[3])
                    self.result_text.insert(tk.END,text_line)
    self.update_idletasks()
    
