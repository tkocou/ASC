## Copyright 2023 by Thomas Kocourek, N4FWD

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import sqlite3
import global_var as gv
import os


def detailed_top_data(self):
    
    self.topwin = tk.Toplevel(self)
    self.topwin.title("Detailed Top 100 Reports")
    self.topwin.configure(bg="#b7d7c7")
    
    window_height = gv.top_window_y
    window_width = gv.top_window_x
    if gv.platform_os == "Darwin":
        self.topwin.resizable(True, True)
        self.topwin.minsize(gv.top_window_x,gv.top_window_y)
        self.topwin.maxsize(gv.top_window_x,gv.top_window_y)
        
    screen_width = self.topwin.winfo_screenwidth()
    screen_height = self.topwin.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))+50
    y_cordinate = int((screen_height/2) - (window_height/2))-80
    self.topwin.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    
    self.topwin.columnconfigure(0,weight=1)
    self.topwin.columnconfigure(1,weight=10)
    
    self.topwin.rowconfigure(0,weight=1)
    self.topwin.rowconfigure(1,weight=1)
    self.topwin.rowconfigure(2,weight=1)
    self.topwin.rowconfigure(3,weight=24)
    
    self.settings_setting = []
    self.db_date = ""
    self.my_callsign = ""
    self.my_state = ""
    self.my_count = ""
    self.my_record = ""
    self.selected_detail_list = tk.StringVar()
    self.ve_detailed_list_high = []
    self.ve_detailed_list_equal = []
    self.ve_detailed_list_low = []
    self.ve_detailed_list_high_state = []
    self.ve_detailed_list_equal_state = []
    self.ve_detailed_list_low_state = []
    
    """
    sql_detailed_by_total_higher_count = "SELECT * FROM ve_count WHERE scount > ?"
    sql_detailed_by_total_lower_count = "SELECT * FROM ve_count WHERE scount < ?"
    sql_detailed_by_total_equal_count = "SELECT * FROM ve_count WHERE scount = ?"
    sql_detailed_by_state_higher_count = "SELECT * FROM ve_count WHERE scount > ? AND state LIKE ?"
    sql_detailed_by_state_lower_count = "SELECT * FROM ve_count WHERE scount < ? AND state LIKE ?"
    sql_detailed_by_state_equal_count = "SELECT * FROM ve_count WHERE scount = ? AND state LIKE ?"
    sql_by_call = "SELECT * FROM ve_count WHERE call LIKE ?"
    sql_by_call_cnt = "SELECT COUNT(*) FROM ve_count WHERE call LIKE ?"
    """
    sql_by_defaults = "SELECT * FROM settings"
    
    
    sql_arrl_total = "SELECT * FROM ve_count" ## Grab all entries from ARRL DB
    sql_glaarg_total = "SELECT * FROM glaarg_count" ## grab all entries from GLAARG DB
    
    
    ## open database and fetch info
    db_connection = sqlite3.connect(gv.asc_database_path)
    db_cursor = db_connection.cursor()
    db_cursor.execute(sql_by_defaults)
    self.settings_setting = db_cursor.fetchone()
    ## ['yourcall','date','gl_date','defaultState','autoflag','cronMin','cronHr','cronDom','cronMon','cronDow']
    self.my_callsign = self.settings_setting[1] ## set up callsign
    self.my_state = self.settings_setting[4] ## set up state
    self.db_date = self.settings_setting[2] ## set up date
    
    ##tmp_result = []
    if self.my_callsign == "NOCALL":
        mb.showerror("Error","Callsign has not been set. Use Set Defaults in menu to fix.")
        self.topwin.destroy()
    else:
        
        '''
        tmp_result.append('%'+self.my_callsign+'%')
        db_cursor.execute(sql_by_call_cnt,tuple(tmp_result)) ## Check if your callsign has multiple matches
        result = db_cursor.fetchall() 
        match_count = result[0][0]
    
        db_cursor.execute(sql_by_call,tuple(tmp_result))
        call_list = db_cursor.fetchall()
        
        if match_count > 1:
            sql_match = 'SELECT * FROM ve_count WHERE id = ?'
            tmp_list = []
            self.exact_matched = False
            for record in call_list:
                exact_match = record[1].split(' ')
                if exact_match[0] == self.my_callsign.upper():
                    self.exact_matched = True
                    tmp_list.append(record[0])
                    db_cursor.execute(sql_match,tuple(tmp_list))
                    call_list = db_cursor.fetchall()
                    break
        self.my_record = list(call_list[0]).copy()
        self.my_count = self.my_record[4]  ## scount
        
        
        tmp_result = []
        tmp_result.append(self.my_count)
        db_cursor.execute(sql_detailed_by_total_higher_count,tuple(tmp_result))
        self.ve_detailed_list_high = db_cursor.fetchall()
        
        
        db_cursor.execute(sql_detailed_by_total_equal_count,tuple(tmp_result))
        self.ve_detailed_list_equal = db_cursor.fetchall()
        
        
        db_cursor.execute(sql_detailed_by_total_lower_count,tuple(tmp_result))
        self.ve_detailed_list_low = db_cursor.fetchall()
        
        ## Let's narrow the scope to the state level
        
        tmp_result.append('%'+self.my_state+'%')
        db_cursor.execute(sql_detailed_by_state_higher_count,tuple(tmp_result))
        self.ve_detailed_list_high_state = db_cursor.fetchall()
        
        db_cursor.execute(sql_detailed_by_state_equal_count,tuple(tmp_result))
        self.ve_detailed_list_equal_state = db_cursor.fetchall()
        
        db_cursor.execute(sql_detailed_by_state_lower_count,tuple(tmp_result))
        self.ve_detailed_list_low_state = db_cursor.fetchall()
        '''
        ## Fetch all records from ARRL DB table
        db_cursor.execute(sql_arrl_total)
        self.ve_arrl_listing = db_cursor.fetchall()
        
        ## Again, fetch all records from GLAARG DB table
        db_cursor.execute(sql_glaarg_total)
        self.ve_glaarg_listing = db_cursor.fetchall()
        
        db_connection.close()
        
        ## Let's set up the GUI and populate it
        
        self.cancel_button = tk.Button(self.topwin, text="Cancel Report", command = self.topwin.destroy)
        self.cancel_button.grid(column=1, row=0, sticky='nw', padx=(20,5), pady=(5,5))
        
        self.cancel_button = tk.Button(self.topwin, text="Display Report", command = lambda: display_list(self))
        self.cancel_button.grid(column=0, row=0, sticky='nw', padx=(20,5), pady=(5,5))
        
        
        self.result_text2 = tk.Text(self.topwin)
        self.result_text2.grid(column=1, row=1, pady=4, padx=(20,30), sticky='nes', rowspan=4)
        self.result_text2.configure(background="#d8f8d8", wrap="word", height=34, width=100,fg="#000000")
        self.result_text2.delete(1.0,tk.END)
        self.text_scroll = ttk.Scrollbar(self.topwin, orient=tk.VERTICAL, command=self.result_text2.yview)
        self.text_scroll.grid(column=1, row=1, sticky='nse', rowspan=20, pady=(5,5), padx=(10,10))
        self.result_text2['yscrollcommand'] = self.text_scroll.set
        '''
        
        self.select_detail = ttk.Combobox(self.topwin, width=13, textvariable=self.selected_detail_list)
        self.select_detail.grid(column=0, row=1, sticky='nw', padx=(5,5), pady=(5,5))
        self.select_detail['values'] = tuple(gv.select_report_list)
        self.select_detail['state'] = 'readonly'
        self.select_detail.set(gv.select_report_list_default)
    
        
        ## set up radio buttons for sort
        for fld in gv.rb_cols:
            self.rb = ttk.Radiobutton(self.topwin, text=fld[0], value=fld[1], variable=self.sort_key)
            self.rb.grid(row=3, column=0, sticky='nwe', padx=fld[2])
            
        self.dir_sort_button = tk.Button(self.topwin, text = 'Sort Direction Toggle', bg="#d0ffd0", command = self.toggle_dir)
        self.dir_sort_button.grid(row=2, column=0, sticky='sw',padx=(0,8), pady=0 )
        '''
    
def display_list(self):    
    #list_selection = self.select_detail.get()
    self.result_text2.delete(1.0,tk.END)
    
    ## create a generic text file
    capture_file = os.path.join(gv.base_rpt_dir,'top 100 listing.txt')
    try:
        os.remove(capture_file)
    except Exception:
        pass
    ## open the text file results capture file
    tf = open(capture_file,'w')
    
    '''
    if list_selection == 'State Higher':
        operation = '>'
        self.total_sort = False
        sorted_list = massage_data(self,self.ve_detailed_list_high_state,operation,self.my_count)
    elif list_selection == 'State Equal':
        operation = '='
        self.total_sort = False
        sorted_list = massage_data(self,self.ve_detailed_list_equal_state,operation,self.my_count)
    elif list_selection == 'State Lower':
        operation = '<'
        self.total_sort = False
        sorted_list = massage_data(self,self.ve_detailed_list_low_state,operation,self.my_count)
    elif list_selection == 'Total Higher':
        operation = '>'
        self.total_sort = True
        sorted_list = massage_data(self,self.ve_detailed_list_high,operation,self.my_count)
    elif list_selection == 'Total Equal':
        operation = '='
        self.total_sort = True
        sorted_list = massage_data(self,self.ve_detailed_list_equal,operation,self.my_count)
    elif list_selection == 'Total Lower':
        operation = '<'
        self.total_sort = True
        sorted_list = massage_data(self,self.ve_detailed_list_low,operation,self.my_count)
    '''
    
    self.total_sort = True
    arrl_sorted_list = sort_list_of_tuples(self,self.ve_arrl_listing)
    glaarg_sorted_list = sort_list_of_tuples(self,self.ve_glaarg_listing)
    
    self.result_text2.delete(1.0,tk.END)
    self.update_idletasks()
    text_line = 'ARRL Report\n'
    tf.write(text_line)
    self.result_text2.insert(tk.END,text_line+'\n')
    index = 1
    for line in arrl_sorted_list:
        text_text = "Count:{}, Call:{}, County:{}, State:{}, Accredited:{}\n".format(line[4],line[1],line[2],line[5],line[3])
        if index == 101:
            break
        
        if line[1][:len(self.my_callsign)] == self.my_callsign:
            text_line = str(index)+'>>' + text_text
        else:
            text_line = str(index)+': ' + text_text
        tf.write(text_line)
        self.result_text2.insert(tk.END,text_line)
        index += 1
    text_line = '\n'
    tf.write(text_line)
    self.result_text2.insert(tk.END,text_line+'\n')
    text_line = 'GLAARG Report\n'
    tf.write(text_line)
    self.result_text2.insert(tk.END,text_line+'\n')
    index = 1
    for line in glaarg_sorted_list:
        text_text = "Count:{}, Call:{}, Name:{}, Helped:{}, Overseen:{}, New License:{}, Upgrades:{}\n".format(line[4],line[2],line[3],line[5],line[6],line[7],line[8])
        if index == 101:
            break
        if line[2] == self.my_callsign:
            text_line = str(index)+'>>' + text_text
        else:
            text_line = str(index)+': ' + text_text
        tf.write(text_line)
        self.result_text2.insert(tk.END,text_line)
        index += 1
    text_line = '\n'
    self.result_text2.insert(tk.END,text_line+'\n')
    text_text = "End of report\n"
    tf.write(text_line)
    self.result_text2.insert(tk.END,text_text)
    tf.close()
'''    
def massage_data(self,data,operation,count):
    sorted_data = sort_list_of_tuples(self,data)
    new_list = []
    for record in sorted_data:
        if operation == '>':
            if int(record[4]) > int(count):
                text_line = "Count:{}, Call:{}, County:{}, State:{}, Accredited:{}:".format(record[4],record[1],record[2],record[5],record[3])
                new_list.append(text_line)
        elif operation == '=':
            if int(record[4]) == int(count):
                text_line = "Count:{}, Call:{}, County:{}, State:{}, Accredited:{}".format(record[4],record[1],record[2],record[5],record[3])
                new_list.append(text_line)
        elif operation == '<':
            if int(record[4]) < int(count):
                text_line = "Count:{}, Call:{}, County:{}, State:{}, Accredited:{}".format(record[4],record[1],record[2],record[5],record[3])
                new_list.append(text_line)
    return new_list
''' 
   
def sort_list_of_tuples(self,lt):
    if self.total_sort: ## only do sort by county at the state level of report
        self.sort_key.set('4') ## For total listing reports, force a sort by count
    sort_data_key = int(self.sort_key.get())
    lt.sort(key=lambda tup_var: tup_var[sort_data_key], reverse = self.sort_dir)
    return lt
    
        