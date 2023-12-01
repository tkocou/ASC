## Copyright 2023 by Thomas Kocourek, N4FWD

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import sqlite3
import global_var as gv


def session_count_data(self):
    
    self.topwin = tk.Toplevel(self)
    self.topwin.title("Session Count Reports")
    self.topwin.configure(bg="#b7d7c7")
    
    window_height = gv.top_window_y
    window_width = gv.top_window_x
    if gv.platform_os == "Darwin":
        self.topwin.resizable(True, True)
        self.topwin.minsize(gv.top_window_x,gv.top_window_y)
        self.topwin.maxsize(gv.top_window_x,gv.top_window_y)
        
    screen_width = self.topwin.winfo_screenwidth()
    screen_height = self.topwin.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    self.topwin.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    
    self.topwin.columnconfigure(0,weight=1)
    self.topwin.columnconfigure(1,weight=1)
    self.topwin.columnconfigure(2,weight=1)
    self.topwin.columnconfigure(3,weight=1)
    self.topwin.columnconfigure(4,weight=1)
    
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
    self.ve_total_people = ""
    self.ve_total_higher = ""
    self.ve_total_equal = ""
    self.ve_total_lower = ""
    self.ve_state_people = ""
    self.ve_state_higher = ""
    self.ve_state_equal = ""
    self.ve_state_lower = ""
    
    ## open database and fetch info
    db_connection = sqlite3.connect(gv.asc_database_path)
    db_cursor = db_connection.cursor()
    sql_by_defaults = "SELECT * FROM settings"
    db_cursor.execute(sql_by_defaults)
    self.settings_setting = db_cursor.fetchone()
    
    ## ['yourcall','date','gl_date','defaultState','autoflag','cronMin','cronHr','cronDom','cronMon','cronDow']
    self.my_callsign = self.settings_setting[1] ## set up callsign
    self.my_state = self.settings_setting[4] ## set up state
    self.db_date = self.settings_setting[2] ## set up date
    
    if self.my_callsign == "NOCALL":
        mb.showerror("Error","Callsign has not been set. Use Set Defaults in menu to fix.")
        self.topwin.destroy()
    else:
        sql_by_total = "SELECT COUNT(*) FROM ve_count"
        db_cursor.execute(sql_by_total) ## get count of all registered VEs
        result = db_cursor.fetchall()
        self.ve_total_people = result[0][0]
        
        tmp_result = []
        sql_by_state = "SELECT COUNT(*) FROM ve_count WHERE state LIKE ?"
        tmp_result.append('%'+self.my_state+'%')
        db_cursor.execute(sql_by_state,tuple(tmp_result)) ## get count of all VEs in your state
        result = db_cursor.fetchall()
        self.ve_state_people = result[0][0]
        
        tmp_result = []
        sql_by_call_cnt = "SELECT COUNT(*) FROM ve_count WHERE call LIKE ?"
        tmp_result.append('%'+self.my_callsign+'%')
        db_cursor.execute(sql_by_call_cnt,tuple(tmp_result)) ## Check if your callsign has multiple matches
        result = db_cursor.fetchall() ## to be used later
        match_count = result[0][0]
        
        sql_by_call = "SELECT * FROM ve_count WHERE call LIKE ?"
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
        else:
            tmp_result = []
            tmp_result.append('%'+self.my_callsign+'%')
            db_cursor.execute(sql_by_call,tuple(tmp_result))
            self.my_record = db_cursor.fetchone()
            
        self.my_count = self.my_record[4]  ## scount
        
        tmp_result = []
        sql_by_total_higher_count = "SELECT COUNT(*) FROM ve_count WHERE scount > ?"
        tmp_result.append(self.my_count)
        db_cursor.execute(sql_by_total_higher_count,tuple(tmp_result))
        result = db_cursor.fetchall()
        self.ve_total_higher = result[0][0]
        
        sql_by_total_equal_count = "SELECT COUNT(*) FROM ve_count WHERE scount = ?"
        db_cursor.execute(sql_by_total_equal_count,tuple(tmp_result))
        result = db_cursor.fetchall()
        self.ve_total_equal = result[0][0]
        
        sql_by_total_lower_count = "SELECT COUNT(*) FROM ve_count WHERE scount < ?"
        db_cursor.execute(sql_by_total_lower_count,tuple(tmp_result))
        result = db_cursor.fetchall()
        self.ve_total_lower = result[0][0]
        
        ## Let's narrow the scope to the state level
        sql_by_state_higher_count = "SELECT COUNT(*) FROM ve_count WHERE scount > ? AND state LIKE ?"
        tmp_result.append('%'+self.my_state+'%')
        db_cursor.execute(sql_by_state_higher_count,tuple(tmp_result))
        result = db_cursor.fetchall()
        self.ve_state_higher = result[0][0]
        
        sql_by_state_equal_count = "SELECT COUNT(*) FROM ve_count WHERE scount = ? AND state LIKE ?"
        db_cursor.execute(sql_by_state_equal_count,tuple(tmp_result))
        result = db_cursor.fetchall()
        self.ve_state_equal = result[0][0]
        
        sql_by_state_lower_count = "SELECT COUNT(*) FROM ve_count WHERE scount < ? AND state LIKE ?"
        db_cursor.execute(sql_by_state_lower_count,tuple(tmp_result))
        result = db_cursor.fetchall()
        self.ve_state_lower = result[0][0]
        
        db_connection.close()
        
        ## Let's set up the GUI and populate it
        
        self.list_label = tk.Label(self.topwin, text="Results")
        self.list_label.grid(row=0, column=0, sticky='ne', padx=(10,600), pady=(10,10))
        
        self.cancel_button = tk.Button(self.topwin, text="Cancel Report", command = self.topwin.destroy)
        self.cancel_button.grid(column=0, row=0, sticky='nw', padx=(20,5), pady=(5,5))
        
        self.result_text2 = tk.Text(self.topwin)
        self.result_text2.grid(column=0, row=1, pady=4, padx=(20,30), sticky='nes')
        self.result_text2.configure(background="#d8f8d8", wrap="word", height=34, width=160,fg="#000000")
        self.result_text2.delete(1.0,tk.END)
        self.text_scroll = ttk.Scrollbar(self.topwin, orient=tk.VERTICAL, command=self.result_text2.yview)
        self.text_scroll.grid(column=0, row=1, sticky='nse', rowspan=20, pady=4, padx=(10,10))
        self.result_text2['yscrollcommand'] = self.text_scroll.set
        
        ## Make sure text window is blank
        self.result_text2.delete(1.0,tk.END)
        
        ## Report texts
        text_text = "Statistics for ARRL accredited VEs as of {}.\n\n".format(self.db_date)
        self.result_text2.insert(tk.END,text_text)
        
        text_text = "{} overall statistics:\n\n".format(self.my_callsign)
        self.result_text2.insert(tk.END,text_text)
        
        text_text = "\tThere are {} accredited VEs.\n\n".format(self.ve_total_people)
        self.result_text2.insert(tk.END,text_text)
        
        text_text = "\tThere are {} VEs with higher session counts.\n".format(self.ve_total_higher)
        self.result_text2.insert(tk.END,text_text)
        
        text_text = "\tThere are {} VEs with equal session counts.\n".format(self.ve_total_equal)
        self.result_text2.insert(tk.END,text_text)
        
        text_text = "\tThere are {} VEs with lower session counts.\n\n".format(self.ve_total_lower)
        self.result_text2.insert(tk.END,text_text)
        
        
        text_text = "{} state statistics:\n\n".format(self.my_callsign)
        self.result_text2.insert(tk.END,text_text)
        
        text_text = "\tThere are {} accredited VEs in the state of {}.\n\n".format(self.ve_state_people,self.my_state)
        self.result_text2.insert(tk.END,text_text)
        
        text_text = "\tThere are {} VEs with higher session counts.\n".format(self.ve_state_higher)
        self.result_text2.insert(tk.END,text_text)
        
        text_text = "\tThere are {} VEs with equal session counts.\n".format(self.ve_state_equal)
        self.result_text2.insert(tk.END,text_text)
        
        text_text = "\tThere are {} VEs with lower session counts.\n\n".format(self.ve_state_lower)
        self.result_text2.insert(tk.END,text_text)
        
        
        text_text = "End of report\n"
        self.result_text2.insert(tk.END,text_text)