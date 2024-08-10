## Copyright 2023 by Thomas Kocourek, N4FWD

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import sqlite3
import global_var as gv
import os
from operator import itemgetter


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
        mb.showerror("Error","Callsign has not been set. Use 'Set Defaults' in menu to fix.")
        self.topwin.destroy()
    else:
        
        ## Fetch all records from ARRL DB table - list of tuples
        db_cursor.execute(sql_arrl_total)
        self.ve_arrl_listing = db_cursor.fetchall()
        
        ## Again, fetch all records from GLAARG DB table - list of tuples
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
        
    
def display_list(self): 
      
    #list_selection = self.select_detail.get()
    self.result_text2.delete(1.0,tk.END)
    
    ## create a capture text file
    capture_file = os.path.join(gv.base_rpt_dir,'top 100 listing.txt')
    try:
        os.remove(capture_file)
    except Exception:
        pass
    ## open and store the results further down
    tf = open(capture_file,'w')
    
    self.total_sort = True

    arrl_sorted_list = sort_list_of_tuples(self,self.ve_arrl_listing)
    
    glaarg_sorted_list = sort_list_of_tuples(self,self.ve_glaarg_listing)
    
    sorted_list = os.path.join(gv.base_rpt_dir,'glaarg_sorted_result.txt')
    
    fd = open(sorted_list,'w')
    
    for item in glaarg_sorted_list:
        text_item = list(item)
        file_text = str(text_item)+'\n'
        fd.write(file_text)
    fd.close()
    
    self.result_text2.delete(1.0,tk.END)
    self.update_idletasks()
    text_line = 'ARRL Report\n'
    tf.write(text_line)
    self.result_text2.insert(tk.END,text_line+'\n')
######################################################### ARRL ##################################
    index = 1    
    for line_tuple in arrl_sorted_list:
        ## only the first 100
        if index > 100:
            break
        
        line = list(line_tuple)
        text_text = "Count:{}, Call:{}, County:{}, State:{}, Accredited:{}\n".format(line[4],line[1],line[2],line[5],line[3])
        
        ## flag a line if it is your callsign
        if line[1][:len(self.my_callsign)] == self.my_callsign:
            text_line = str(index)+'**' + text_text
        else:
            text_line = str(index)+': ' + text_text
        ## columnize the start of the data
        if index < 10:
            t_line = ' '+text_line
        elif index < 100:
            t_line = ' '+text_line
        
        tf.write(t_line)
        self.result_text2.insert(tk.END,text_line)
        index += 1
    text_line = '\n'
    tf.write(text_line)
    self.result_text2.insert(tk.END,text_line+'\n')
    text_line = 'GLAARG Report\n'
    tf.write(text_line)
    self.result_text2.insert(tk.END,text_line+'\n')
    ####################################### GLAARG ##########################
    index = 1
    for line_tuple in glaarg_sorted_list:
        print("type line_tuple: ",line_tuple)
        
        ## Only the first 100
        if index > 100:
            break
        
        line = list(line_tuple)
        text_text = "Count:{}, Call:{}, Name:{}, Helped:{}, Overseen:{}, New License:{}, Upgrades:{}\n".format(line[4],line[2],line[3],line[5],line[6],line[7],line[8])
        
        ## flag a line if it is your callsign
        if line[2] == self.my_callsign:
            text_line = str(index)+'**' + text_text
        else:
            text_line = str(index)+': ' + text_text
        ## columnize the start of the data
        if index < 10:
            text_line = ' '+text_line
        elif index < 100:
            text_line = ' '+text_line
        
        tf.write(text_line)
        self.result_text2.insert(tk.END,text_line)
        index += 1
    text_line = '\n'
    tf.write(text_line)
    self.result_text2.insert(tk.END,text_line+'\n')
    text_text = "\nEnd of report\n"
    tf.write(text_text)
    self.result_text2.insert(tk.END,text_text)
    tf.close()


def sort_list_of_tuples(self,data):
    data.sort(key=itemgetter(4),reverse=True)
    return data
        