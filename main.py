from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from customtkinter import *
import mysql.connector

window_x = 900
window_y = 700

frame_x = 700
frame_y = 800

label_font = ("Arial", 16)

conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="123password",
            database="student_grading"
        )
c = conn.cursor()

class Subject_button():
    def __init__(self, sub_id, sub_name, group_name, group_id, lect_id):
        self.__sub_id = sub_id
        self.__sub_name = sub_name
        self.__group_name = group_name
        self.__group_id = group_id
        self.__lect_id = lect_id

    def create_button(self, x, y):
        button = CTkButton(lecturer.get_name(), text=f"{self.__sub_name}, {self.__group_name}", width=200, command=self.view_subject)
        button.place(x=x, y=y, anchor=CENTER)

    def view_subject(self):
        lecturer.destroy_window(None)
        lecturer_subject = Lecturer_subject(self.__sub_id, self.__lect_id, self.__group_id)
        lecturer_subject.populate_window()

class Window():
    def __init__(self):
        self._x = 0
        self._id = 0

    def set_id(self):
        self._id = int(login.get_id())

    def get_id(self):
        self.set_id()
        return self._id

    def create_window(self, x, y):
        self._name = CTkFrame(root, height=x, width=y)
        self._name.pack(pady=10)

        self._x = x

    def destroy_window(self, log_out):
        self._name.destroy()

        if log_out == "Logout":
            login.populate_window()
        elif log_out == "Lecturer":
            lecturer.populate_window()
        elif log_out == "Admin":
            admin.populate_window()
        else:
            pass

    def get_x(self):
        return self._x

    def get_name(self):
        return self._name

class Student(Window):
    def __init__(self, name):
        self._name = name

    def populate_window(self):
        self.create_window(frame_x, frame_y)

        logout = CTkButton(self._name, text="Log Out", command=lambda: self.destroy_window("Logout"))
        logout.place(x=frame_y/2, y=600, anchor=CENTER)

        c.execute(f"""
        select subject_list.subject, grades.Grade FROM subject_list, subjects, grades, student
        where student.id = grades.Student_id and grades.subject_id = subjects.id 
        and sub_list_id = subject_list.id and student.id = {student.get_id()}""");

        x = frame_y/2
        y = 100
        for i in c.fetchall():
            label = CTkLabel(self._name, text=f"{i[0]} ")
            label.place(x=x, y=y, anchor=E)

            grade = CTkLabel(self._name, text=f" {i[1]}")
            grade.place(x=x, y=y, anchor=W)

            y += 40

class Lecturer(Window):
    def __init__(self, name):
        self._name = name
        self._sub_id = 0
        self._group_id = 0

    def populate_window(self):
        self.create_window(frame_x, frame_y)

        c.execute(f"""SELECT subjects.id, subject_list.subject, student_grading.groups.group, student_grading.groups.id
        FROM subject_list, subjects, teacher, student_grading.groups
        where subject_list.id = subjects.sub_list_id 
        and subjects.groups_id = student_grading.groups.id 
        and subjects.teacher_id = teacher.id and teacher.id = {lecturer.get_id()};
        """)

        x = frame_y/2
        y = 100
        for i in c.fetchall():
            button = Subject_button(i[0], i[1], i[2], i[3], lecturer.get_id())
            button.create_button(x, y)

            y += 40


        logout = CTkButton(self._name, text="Log Out", command=lambda: self.destroy_window("Logout"))
        logout.place(x=frame_y/2, y=600, anchor=CENTER)

class Lecturer_subject(Window):
    def __init__(self, sub_id, lect_id, group_id):
        self._lect_id = lect_id
        self._sub_id = sub_id
        self._group_id = group_id

    def populate_window(self):
        self.create_window(frame_x, frame_y)

        self._table = ttk.Treeview(self._name, height=20)

        self._table['columns'] = ('Id', 'Name', "Surname", "Grade")

        self._table.heading("#0", text="")
        self._table.heading("Id", text="")
        self._table.heading("Name", text="Name", anchor=W)
        self._table.heading("Surname", text="Surname", anchor=W)
        self._table.heading("Grade", text="Grade", anchor=CENTER)

        self._table.column("#0", width=0, stretch=NO)
        self._table.column("Id", width=0, stretch=NO)
        self._table.column("Name", width=120, minwidth=120, anchor=W)
        self._table.column("Surname", width=200, minwidth=200, anchor=W)
        self._table.column("Grade", width=50, minwidth=50, anchor=CENTER)

        self._table.place(x=frame_y/2, y=20, anchor=N)

        grade_label = CTkLabel(self._name, text="Grade: ")
        grade_label.place(x=frame_y/2, y=430, anchor=E)

        self._grade_entry = CTkComboBox(self._name, values=["None", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"], width=70)
        self._grade_entry.place(x=frame_y/2, y=430, anchor=W)

        self.__update_btn = CTkButton(self._name, text="Set", command=self.update_record, width=60, state=DISABLED)
        self.__update_btn.place(x=frame_y/2, y=470, anchor=CENTER)

        logout = CTkButton(self._name, text="Back", command=lambda: self.destroy_window("Lecturer"))
        logout.place(x=frame_y/2, y=600, anchor=CENTER)

        c.execute(f"""
        SELECT student.id, student.name, student.surname FROM student_grading.student, student_grading.groups, subjects
        WHERE student.groups_id = student_grading.groups.id and student_grading.groups.id = subjects.groups_id 
        AND subjects.id = {self._sub_id} AND student_grading.groups.id = {self._group_id}
        """)

        self._table.bind("<ButtonRelease-1>", self.select_record)

        for i in c.fetchall():
            self._table.insert(parent='', index='end', iid=i[0], values=(i[0], i[1], i[2], None))

            c.execute(f"""
            SELECT Grade FROM student_grading.grades
            WHERE Subject_id = {self._sub_id} AND Student_id = {i[0]};
            """)

            for j in c.fetchall():
                for k in j:
                    self._table.item(i[0], text="", values=(i[0], i[1], i[2], k))

    def select_record(self, e):
        self.__selected = self._table.focus()
        self.__grade = self._table.item(self.__selected, 'values')

        if self.__selected != "":
            self._grade_entry.set(str(self.__grade[3]))
            self.__update_btn.configure(state=NORMAL)

    def update_record(self):
        self._table.item(self.__selected, text="", values=(self.__grade[0], self.__grade[1], self.__grade[2], self._grade_entry.get()))

        if self._grade_entry.get() != "None":
            c.execute(f"""
            UPDATE student_grading.grades SET grades.Grade = {int(self._grade_entry.get())} WHERE grades.Student_id = {int(self.__grade[0])} and grades.Subject_id = {int(self._sub_id)};
            """)
        else:
            c.execute(f"""
            UPDATE student_grading.grades SET grades.Grade = NULL WHERE grades.Student_id = {int(self.__grade[0])} and grades.Subject_id = {int(self._sub_id)};
            """)

        conn.commit()

class Admin(Window):
    def __init__(self, name):
        self._name = name

    def populate_window(self):
        self.create_window(frame_x, frame_y)

        new_teacher_btn = CTkButton(self._name, text="View all Lecturers", command=self.view_teacher)
        new_teacher_btn.place(x=frame_y/2, y=100, anchor=CENTER)

        new_group_btn = CTkButton(self._name, text="View all Groups", command=self.view_group)
        new_group_btn.place(x=frame_y/2, y=150, anchor=CENTER)

        new_subject_btn = CTkButton(self._name, text="View all Subjects", command=self.view_subject)
        new_subject_btn.place(x=frame_y/2, y=200, anchor=CENTER)

        new_student_btn = CTkButton(self._name, text="View all Students", command=self.view_student)
        new_student_btn.place(x=frame_y/2, y=250, anchor=CENTER)


        logout = CTkButton(self._name, text="Log Out", command=lambda: self.destroy_window("Logout"))
        logout.place(x=frame_y/2, y=600, anchor=CENTER)

    def view_teacher(self):
        self._name.destroy()

        self.create_window(frame_x, frame_y)
        self._name.pack(pady=10)

        self._table = ttk.Treeview(self._name, height=20)

        self._table['columns'] = ('Id', 'Name', "Surname", "Username", "Email", "DOB", "Phone", "Address")

        self._table.heading("#0", text="")
        self._table.heading("Id", text="Id", anchor=CENTER)
        self._table.heading("Name", text="Name", anchor=W)
        self._table.heading("Surname", text="Surname", anchor=W)
        self._table.heading("Username", text="Username", anchor=W)
        self._table.heading("Email", text="Email", anchor=W)
        self._table.heading("DOB", text="Date of Birth", anchor=CENTER)
        self._table.heading("Phone", text="Phone", anchor=W)
        self._table.heading("Address", text="Address", anchor=W)

        self._table.column("#0", width=0, stretch=NO)
        self._table.column("Id", width=30, minwidth=30, anchor=CENTER)
        self._table.column("Name", width=60, minwidth=60, anchor=W)
        self._table.column("Surname", width=90, minwidth=90, anchor=W)
        self._table.column("Username", width=70, minwidth=70, anchor=W)
        self._table.column("Email", width=170, minwidth=170, anchor=W)
        self._table.column("DOB", width=90, minwidth=90, anchor=CENTER)
        self._table.column("Phone", width=110, minwidth=110, anchor=W)
        self._table.column("Address", width=150, minwidth=150, anchor=W)

        self._table.place(x=frame_y/2, y=20, anchor=N)

        self.__new_record = CTkButton(self._name, text="New Record", width=110, command=self.new_teacher)
        self.__new_record.place(x=15, y=430, anchor=W)

        self.__update_record = CTkButton(self._name, text="Update Record", width=110, command=self.update_teacher)
        self.__update_record.place(x=135, y=430, anchor=W)
        self.__update_record.configure(state=DISABLED)

        self.__delete_record = CTkButton(self._name, text="Delete Record", width=110, command=self.remove_teacher)
        self.__delete_record.place(x=255, y=430, anchor=W)
        self.__delete_record.configure(state=DISABLED)

        back = CTkButton(self._name, text="Back", command=lambda: self.destroy_window("Admin"))
        back.place(x=frame_y/2, y=600, anchor=CENTER)

        c.execute(f"""
        SELECT * FROM teacher
                """)

        self._table.bind("<ButtonRelease-1>", self.select_record)

        for i in c.fetchall():
            self._table.insert(parent='', index='end', iid=i[0], values=(i[0], i[1], i[2], i[3], i[5], i[6], i[7], i[8]))

    def remove_teacher(self):
        #Sukuria patvirtinimo dialoga
        box = messagebox.askyesno("Warning!", "Are you sure you want to remove this record?", default='no')

        if box:
            self._table.delete(self.__selected)

            c.execute(f"""
            DELETE FROM teacher WHERE (id = {int(self.__selected)});
            """)
            conn.commit()
        else:
            pass

    def update_teacher(self):
        self.__update_teacher = CTk()
        self.__update_teacher.title("Update Lecturer")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_x = int((screen_width / 2) - (400 / 2))
        window_y = int((screen_height / 2) - (600 / 2 + 60))
        self.__update_teacher.geometry(f'400x600+{window_x}+{window_y}')
        self.__update_teacher.resizable(False, False)

        labels = ("Arial", 14)

        name_label = CTkLabel(self.__update_teacher, text="Name:", font=labels)
        name_label.place(x=100, y=55, anchor=W)
        name_entry = CTkEntry(self.__update_teacher, width=200)
        name_entry.place(x=200, y=80, anchor=CENTER)

        surname_label = CTkLabel(self.__update_teacher, text="Surname:", font=labels)
        surname_label.place(x=100, y=125, anchor=W)
        surname_entry = CTkEntry(self.__update_teacher, width=200)
        surname_entry.place(x=200, y=150, anchor=CENTER)

        email_label = CTkLabel(self.__update_teacher, text="Email:", font=labels)
        email_label.place(x=100, y=195, anchor=W)
        email_entry = CTkEntry(self.__update_teacher, width=200)
        email_entry.place(x=200, y=220, anchor=CENTER)

        dob_label = CTkLabel(self.__update_teacher, text="Date of Birth:", font=labels)
        dob_label.place(x=100, y=265, anchor=W)
        dob_entry = CTkEntry(self.__update_teacher, width=200)
        dob_entry.place(x=200, y=290, anchor=CENTER)

        phone_label = CTkLabel(self.__update_teacher, text="Phone:", font=labels)
        phone_label.place(x=100, y=335, anchor=W)
        phone_entry = CTkEntry(self.__update_teacher, width=200)
        phone_entry.place(x=200, y=360, anchor=CENTER)

        address_label = CTkLabel(self.__update_teacher, text="Address:", font=labels)
        address_label.place(x=100, y=405, anchor=W)
        address_entry = CTkEntry(self.__update_teacher, width=200)
        address_entry.place(x=200, y=430, anchor=CENTER)

        submit = CTkButton(self.__update_teacher, text="Submit", command=lambda: self.update_teacher_submit(name_entry.get(),
                                                                                                     surname_entry.get(),
                                                                                                     email_entry.get(),
                                                                                                     dob_entry.get(),
                                                                                                     phone_entry.get(),
                                                                                                     address_entry.get()))
        submit.place(x=200, y=560, anchor=CENTER)

        name_entry.insert(0, self.__selection[1])
        surname_entry.insert(0, self.__selection[2])
        email_entry.insert(0, self.__selection[4])
        dob_entry.insert(0, self.__selection[5])
        phone_entry.insert(0, self.__selection[6])
        address_entry.insert(0, self.__selection[7])

        self.__update_teacher.mainloop()

    def update_teacher_submit(self, name, surname, email, dob, phone, address):
        if name != "" and surname != "" and email != '' and dob != "" and phone != "" and address != "":
            # Gauti ID
            id = self.__selected

            #Gauti naudotojo varda
            username = name[0] + surname

            #Atnaujinti lentele
            self._table.item(self.__selected, text="", values=(int(id), name, surname, username, email, dob, phone, address))

            #Atnaujinti duomenu baze
            c.execute(f"""
            UPDATE student_grading.teacher SET 
            name = '{name}', 
            surname = '{surname}', 
            username = '{username}', 
            password = '{surname}', 
            email = '{email}', 
            dob = CAST('{dob}' as DATE), 
            phone = '{phone}',
            address = "{address}"  
            WHERE (id = {id});
            """)
            conn.commit()

            #Close the new window
            self.__update_teacher.destroy()

        else:
            warning = CTkLabel(self.__update_teacher, text="All fields must be filled!", text_color='red')
            warning.place(x=200, y=530, anchor=CENTER)

    def new_teacher(self):
        self._new_teacher = CTk()
        self._new_teacher.title("Add new Lecturer")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_x = int((screen_width / 2) - (400 / 2))
        window_y = int((screen_height / 2) - (600 / 2 + 60))
        self._new_teacher.geometry(f'400x600+{window_x}+{window_y}')
        self._new_teacher.resizable(False, False)

        labels = ("Arial", 14)

        name_label = CTkLabel(self._new_teacher, text="Name:", font=labels)
        name_label.place(x=100, y=55, anchor=W)
        name_entry = CTkEntry(self._new_teacher, width=200)
        name_entry.place(x=200, y=80, anchor=CENTER)

        surname_label = CTkLabel(self._new_teacher, text="Surname:", font=labels)
        surname_label.place(x=100, y=125, anchor=W)
        surname_entry = CTkEntry(self._new_teacher, width=200)
        surname_entry.place(x=200, y=150, anchor=CENTER)

        email_label = CTkLabel(self._new_teacher, text="Email:", font=labels)
        email_label.place(x=100, y=195, anchor=W)
        email_entry = CTkEntry(self._new_teacher, width=200)
        email_entry.place(x=200, y=220, anchor=CENTER)

        dob_label = CTkLabel(self._new_teacher, text="Date of Birth:", font=labels)
        dob_label.place(x=100, y=265, anchor=W)
        dob_entry = CTkEntry(self._new_teacher, width=200)
        dob_entry.place(x=200, y=290, anchor=CENTER)

        phone_label = CTkLabel(self._new_teacher, text="Phone:", font=labels)
        phone_label.place(x=100, y=335, anchor=W)
        phone_entry = CTkEntry(self._new_teacher, width=200)
        phone_entry.place(x=200, y=360, anchor=CENTER)

        address_label = CTkLabel(self._new_teacher, text="Address:", font=labels)
        address_label.place(x=100, y=405, anchor=W)
        address_entry = CTkEntry(self._new_teacher, width=200)
        address_entry.place(x=200, y=430, anchor=CENTER)

        submit = CTkButton(self._new_teacher, text="Submit", command=lambda:self.new_teacher_submit(name_entry.get(),
                                                                                                    surname_entry.get(),
                                                                                                    email_entry.get(),
                                                                                                    dob_entry.get(),
                                                                                                    phone_entry.get(),
                                                                                                    address_entry.get()))
        submit.place(x=200, y=560, anchor=CENTER)

        self._new_teacher.mainloop()

    def new_teacher_submit(self, name, surname, email, dob, phone, address):
        if name != "" and surname != "" and email != '' and dob != "" and phone != "" and address != "":
            # Gauti nauja ID
            id = 0
            c.execute("SELECT * FROM teacher")
            for i in c.fetchall():
                id = i[0]

            new_id = int(id)+1

            #Gauti naudotojo varda
            username = name[0] + surname

            #Ikelti duomenis i lentele
            self._table.insert(parent='', index='end', iid=new_id, values=(new_id, name, surname, username, email, dob, phone, address))

            #Ikelti duomenis i duomenu baze
            c.execute(f"""
            INSERT INTO teacher (id, name, surname, username, password, email, dob, phone, address)
            VALUES ({int(new_id)}, '{name}', '{surname}', '{username}', '{surname}', '{email}', CAST('{dob}' as DATE), '{phone}', '{address}');
            """)
            conn.commit()

            #Close the new window
            self._new_teacher.destroy()

        else:
            warning = CTkLabel(self._new_teacher, text="All fields must be filled!", text_color='red')
            warning.place(x=200, y=530, anchor=CENTER)

    def view_group(self):
        self._name.destroy()

        self.create_window(frame_x, frame_y)

        self._table = ttk.Treeview(self._name, height=20)

        self._table['columns'] = ('Id', 'Group', 'Empty')

        self._table.heading("#0", text="")
        self._table.heading("Id", text="Id", anchor=CENTER)
        self._table.heading("Group", text="Name", anchor=W)
        self._table.heading("Empty", text="")

        self._table.column("#0", width=0, stretch=NO)
        self._table.column("Id", width=30, minwidth=30, anchor=CENTER)
        self._table.column("Group", width=70, minwidth=70, anchor=W)
        self._table.column("Empty", width=670, stretch=NO)

        self._table.place(x=frame_y/2, y=20, anchor=N)

        self.__new_record = CTkButton(self._name, text="New Record", width=110, command=self.new_group)
        self.__new_record.place(x=15, y=430, anchor=W)

        self.__update_record = CTkButton(self._name, text="Update Record", width=110, command=self.update_group)
        self.__update_record.place(x=135, y=430, anchor=W)
        self.__update_record.configure(state=DISABLED)

        self.__delete_record = CTkButton(self._name, text="Delete Record", width=110, command=self.remove_group)
        self.__delete_record.place(x=255, y=430, anchor=W)
        self.__delete_record.configure(state=DISABLED)

        back = CTkButton(self._name, text="Back", command=lambda: self.destroy_window("Admin"))
        back.place(x=frame_y/2, y=600, anchor=CENTER)

        c.execute(f"""
        SELECT * FROM student_grading.groups
        """)

        for i in c.fetchall():
            self._table.insert(parent='', index='end', iid=i[0], values=(i[0], i[1]))

        self._table.bind("<ButtonRelease-1>", self.select_record)

    def remove_group(self):
        #Sukuria patvirtinimo dialoga
        box = messagebox.askyesno("Warning!", "Are you sure you want to remove this record?")

        if box:
            self._table.delete(self.__selected)

            c.execute(f"""
            DELETE FROM student_grading.groups WHERE (id = {int(self.__selected)});
            """)
            conn.commit()
        else:
            pass

    def update_group(self):
        self.__update_group = CTk()
        self.__update_group.title("Update Group")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_x = int((screen_width / 2) - (400 / 2))
        window_y = int((screen_height / 2) - (600 / 2 + 60))
        self.__update_group.geometry(f'400x300+{window_x}+{window_y}')
        self.__update_group.resizable(False, False)

        labels = ("Arial", 14)

        name_label = CTkLabel(self.__update_group, text="Name:", font=labels)
        name_label.place(x=100, y=55, anchor=W)
        name_entry = CTkEntry(self.__update_group, width=200)
        name_entry.place(x=200, y=80, anchor=CENTER)

        submit = CTkButton(self.__update_group, text="Submit", command=lambda:self.update_group_submit(name_entry.get()))
        submit.place(x=200, y=260, anchor=CENTER)

        name_entry.insert(0, self.__selection[1])

        self.__update_group.mainloop()

    def update_group_submit(self, name):
        if name != "":
            # Gauti ID
            id = self.__selected

            #Atnaujinti lentele
            self._table.item(self.__selected, text="", values=(int(id), name))

            #Atnaujinti duomenu baze
            c.execute(f"""
            UPDATE student_grading.groups SET 
            groups.group = '{name}' 
            WHERE (id = {id});
                        """)
            conn.commit()

            #Uzdaryti nauja langa
            self.__update_group.destroy()

        else:
            warning = CTkLabel(self.__update_group, text="All fields must be filled!", text_color='red')
            warning.place(x=200, y=530, anchor=CENTER)

    def new_group(self):
        self._new_group = CTk()
        self._new_group.title("Add new group")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_x = int((screen_width / 2) - (400 / 2))
        window_y = int((screen_height / 2) - (600 / 2 + 60))
        self._new_group.geometry(f'400x600+{window_x}+{window_y}')
        self._new_group.resizable(False, False)

        labels = ("Arial", 14)

        name_label = CTkLabel(self._new_group, text="Name:", font=labels)
        name_label.place(x=100, y=55, anchor=W)
        name_entry = CTkEntry(self._new_group, width=200)
        name_entry.place(x=200, y=80, anchor=CENTER)

        submit = CTkButton(self._new_group, text="Submit", command=lambda:self.new_group_submit(name_entry.get()))
        submit.place(x=200, y=560, anchor=CENTER)

        self._new_group.mainloop()

    def new_group_submit(self, name):
        if name != "":
            # Gauti nauja ID
            id = 0
            c.execute("SELECT * FROM student_grading.groups")
            for i in c.fetchall():
                id = i[0]

            new_id = int(id)+1

            #Ikelti duomenis i lentele
            self._table.insert(parent='', index='end', iid=new_id, values=(new_id, name))

            #Ikelti duomenis i duomenu baze
            c.execute(f"""
            INSERT INTO student_grading.groups (id, groups.group)
            VALUES ({int(new_id)}, '{name}');""")
            conn.commit()

            #Close the new window
            self._new_group.destroy()

        else:
            warning = CTkLabel(self._new_group, text="All fields must be filled!", text_color='red')
            warning.place(x=frame_y/2, y=530, anchor=CENTER)

    def view_subject(self):
        #self._name.destroy()

        self.create_window(frame_x, frame_y)

        self._table = ttk.Treeview(self._name, height=20)

        self._table['columns'] = ('Id', 'Subject', "Lecturer", "Group", "Empty")

        self._table.heading("#0", text="")
        self._table.heading("Id", text="Id", anchor=CENTER)
        self._table.heading("Subject", text="Subject", anchor=W)
        self._table.heading("Lecturer", text="Lecturer", anchor=W)
        self._table.heading("Group", text="Group", anchor=W)
        self._table.heading("Empty", text="")

        self._table.column("#0", width=0, stretch=NO)
        self._table.column("Id", width=30, minwidth=30, anchor=CENTER)
        self._table.column("Subject", width=160, minwidth=160, anchor=W)
        self._table.column("Lecturer", width=120, minwidth=120, anchor=W)
        self._table.column("Group", width=60, minwidth=60, anchor=W)
        self._table.column("Empty", width=400, stretch=NO)

        self._table.place(x=frame_y / 2, y=20, anchor=N)

        self.__new_record = CTkButton(self._name, text="New Record", width=110, command=self.new_subject)
        self.__new_record.place(x=15, y=430, anchor=W)

        self.__update_record = CTkButton(self._name, text="Update Record", width=110, command=self.update_subject)
        self.__update_record.place(x=135, y=430, anchor=W)
        self.__update_record.configure(state=DISABLED)

        self.__delete_record = CTkButton(self._name, text="Delete Record", width=110, command=self.remove_subject)
        self.__delete_record.place(x=255, y=430, anchor=W)
        self.__delete_record.configure(state=DISABLED)

        back = CTkButton(self._name, text="Back", command=lambda: self.destroy_window("Admin"))
        back.place(x=frame_y / 2, y=600, anchor=CENTER)

        c.execute(f"""
        SELECT subjects.id, teacher.name, teacher.surname, subject_list.subject, student_grading.groups.group FROM student_grading.subjects, teacher, subject_list, student_grading.groups
        WHERE teacher_id = teacher.id and sub_list_id = subject_list.id and groups_id = student_grading.groups.id;
        """)

        self._table.bind("<ButtonRelease-1>", self.select_record)

        for i in c.fetchall():
            lecturer = i[1] + " " + i[2]
            self._table.insert(parent='', index='end', iid=i[0], values=(i[0], i[3], lecturer, i[4]))

        back = CTkButton(self._name, text="Back", command=lambda: self.destroy_window("Admin"))
        back.place(x=frame_y/2, y=600, anchor=CENTER)

    def remove_subject(self):
        # Sukuria patvirtinimo dialoga
        box = messagebox.askyesno("Warning!", "Are you sure you want to remove this record?")

        if box:
            self._table.delete(self.__selected)
            c.execute(f"""
            DELETE FROM student_grading.grades WHERE (Subject_id = {int(self.__selected)});
            """)
            conn.commit()

            c.execute(f"""
            DELETE FROM student_grading.subjects WHERE (id = {int(self.__selected)});
            """)
            conn.commit()
        else:
            pass

    def new_subject(self):
        self._new_subject = CTk()
        self._new_subject.title("Add new subject")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_x = int((screen_width / 2) - (400 / 2))
        window_y = int((screen_height / 2) - (600 / 2 + 60))
        self._new_subject.geometry(f'400x600+{window_x}+{window_y}')
        self._new_subject.resizable(False, False)

        labels = ("Arial", 14)

        # Gauti destitoju vardus
        c.execute("SELECT teacher.name, teacher.surname FROM student_grading.teacher")
        teachers = []
        for i in c.fetchall():
            teachers.append(i[0] + " " + i[1])

        teacher_label = CTkLabel(self._new_subject, text="Lecturer:", font=labels)
        teacher_label.place(x=100, y=55, anchor=W)
        teacher_entry = CTkComboBox(self._new_subject, values=[*teachers], width=200)
        teacher_entry.place(x=100, y=80, anchor=W)

        # Gauti paskaitu pavadinimus
        c.execute("SELECT student_grading.subject_list.subject FROM student_grading.subject_list")
        subjects = []
        for i in c.fetchall():
            for j in i:
                subjects.append(j)

        subject_label = CTkLabel(self._new_subject, text="Subject:", font=labels)
        subject_label.place(x=100, y=125, anchor=W)
        subject_entry = CTkComboBox(self._new_subject, values=[*subjects], width=200)
        subject_entry.place(x=100, y=150, anchor=W)

        # Gauti grupiu pavadinimus
        c.execute("SELECT student_grading.groups.group FROM student_grading.groups")
        groups = []
        for i in c.fetchall():
            for j in i:
                groups.append(j)

        group_label = CTkLabel(self._new_subject, text="Group:", font=labels)
        group_label.place(x=100, y=195, anchor=W)
        group_entry = CTkComboBox(self._new_subject, values=[*groups], width=200)
        group_entry.place(x=100, y=220, anchor=W)

        submit = CTkButton(self._new_subject, text="Submit", command=lambda:self.new_subject_submit(teacher_entry.get(),
                                                                                                    subject_entry.get(),
                                                                                                    group_entry.get()))
        submit.place(x=200, y=560, anchor=CENTER)

        self._new_subject.mainloop()

    def new_subject_submit(self, teacher, subject, group):
        # Gauti nauja ID
        id = 0
        c.execute("SELECT * FROM subjects")
        for i in c.fetchall():
            id = i[0]

        new_id = int(id)+1

        lecturer_split = teacher.split(" ")

        #Gauti paskaitos ID
        c.execute(f"select subject_list.id from subject_list where subject = '{subject}'")
        for i in c.fetchone():
            sub_id = i

        #Gauti destitojo ID
        c.execute(f"select teacher.id from teacher where name = '{lecturer_split[0]}' and surname = '{lecturer_split[1]}'")
        for i in c.fetchone():
            lect_id = i

        #Gauti grupes ID
        c.execute(f"select student_grading.groups.id from student_grading.groups where student_grading.groups.group = '{group}'")
        for i in c.fetchone():
            group_id = i

        #Ikelti duomenis i lentele
        self._table.insert(parent='', index='end', iid=new_id, values=(new_id, subject, teacher, group))

        #Ikelti duomenis i duomenu baze
        c.execute(f"""
        INSERT INTO subjects (id, teacher_id, sub_list_id, groups_id)
        VALUES ({int(new_id)}, {int(lect_id)}, {int(sub_id)}, {int(group_id)});
        """)
        conn.commit()

        # Sukurti duomenis pazimiu lentelei

        # Gauti nauja id
        grade_id = 0
        c.execute("select id from grades")
        for i in c.fetchall():
            for j in i:
                grade_id = j + 1

        print(grade_id)
        c.execute(f"""
        select id from student where groups_id = {group_id}
        """)

        for i in c.fetchall():
            c.execute(f"""
            INSERT INTO grades (id, Subject_id, Student_id)
            VALUES ('{int(grade_id)}', '{int(new_id)}', '{int(i[0])}');
            """)
            conn.commit()

            grade_id += 1

        #Close the new window
        self._new_subject.destroy()

    def update_subject(self):
        self._update_subject = CTk()
        self._update_subject.title("Update subject")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_x = int((screen_width / 2) - (400 / 2))
        window_y = int((screen_height / 2) - (600 / 2 + 60))
        self._update_subject.geometry(f'400x600+{window_x}+{window_y}')
        self._update_subject.resizable(False, False)

        labels = ("Arial", 14)

        # Gauti destitoju vardus
        c.execute("SELECT teacher.name, teacher.surname FROM student_grading.teacher")
        teachers = []
        for i in c.fetchall():
            teachers.append(i[0] + " " + i[1])

        teacher_label = CTkLabel(self._update_subject, text="Lecturer:", font=labels)
        teacher_label.place(x=100, y=55, anchor=W)
        teacher_entry = CTkComboBox(self._update_subject, values=[*teachers], width=200)
        teacher_entry.place(x=100, y=80, anchor=W)

        # Gauti paskaitu pavadinimus
        c.execute("SELECT student_grading.subject_list.subject FROM student_grading.subject_list")
        subjects = []
        for i in c.fetchall():
            for j in i:
                subjects.append(j)

        subject_label = CTkLabel(self._update_subject, text="Subject:", font=labels)
        subject_label.place(x=100, y=125, anchor=W)
        subject_entry = CTkComboBox(self._update_subject, values=[*subjects], width=200)
        subject_entry.place(x=100, y=150, anchor=W)

        # Gauti grupiu pavadinimus
        c.execute("SELECT student_grading.groups.group FROM student_grading.groups")
        groups = []
        for i in c.fetchall():
            for j in i:
                groups.append(j)

        group_label = CTkLabel(self._update_subject, text="Group:", font=labels)
        group_label.place(x=100, y=195, anchor=W)
        group_entry = CTkComboBox(self._update_subject, values=[*groups], width=200)
        group_entry.place(x=100, y=220, anchor=W)

        submit = CTkButton(self._update_subject, text="Submit", command=lambda:self.update_subject_submit(teacher_entry.get(),
                                                                                                       subject_entry.get(),
                                                                                                       group_entry.get()))
        submit.place(x=200, y=560, anchor=CENTER)

        teacher_entry.set(self.__selection[2])
        subject_entry.set(self.__selection[1])
        group_entry.set(self.__selection[3])

        self._update_subject.mainloop()

    def update_subject_submit(self, teacher, subject, group):
        # Gauti ID
        id = self.__selected

        # Gauti paskaitos ID
        c.execute(f"select subject_list.id from subject_list where subject = '{subject}'")
        for i in c.fetchone():
            sub_id = i

        # Gauti destitojo ID
        lecturer_split = teacher.split(" ")
        c.execute(
            f"select teacher.id from teacher where name = '{lecturer_split[0]}' and surname = '{lecturer_split[1]}'")
        for i in c.fetchone():
            lect_id = i

        # Gauti grupes ID
        c.execute(
            f"select student_grading.groups.id from student_grading.groups where student_grading.groups.group = '{group}'")
        for i in c.fetchone():
            group_id = i

        # Atnaujinti lentele
        self._table.item(self.__selected, text="",
                         values=(int(id), subject, teacher, group))

        # Issaugoti duomenu baze
        c.execute(f"""
        UPDATE student_grading.subjects SET 
        teacher_id = '{lect_id}', 
        sub_list_id = '{sub_id}', 
        groups_id = '{group_id}'
        WHERE (id = {int(id)});
        """)
        conn.commit()

        # Uzdaryti langa
        self._update_subject.destroy()

    def view_student(self):
        self._name.destroy()

        self.create_window(frame_x, frame_y)

        self._table = ttk.Treeview(self._name, height=20)

        self._table['columns'] = ('Id', 'Name', "Surname", "Username", "Email", "DOB", "Phone", "Address", "Group")

        self._table.heading("#0", text="")
        self._table.heading("Id", text="Id", anchor=CENTER)
        self._table.heading("Name", text="Name", anchor=W)
        self._table.heading("Surname", text="Surname", anchor=W)
        self._table.heading("Username", text="Username", anchor=W)
        self._table.heading("Email", text="Email", anchor=W)
        self._table.heading("DOB", text="Date of Birth", anchor=CENTER)
        self._table.heading("Phone", text="Phone", anchor=W)
        self._table.heading("Address", text="Address", anchor=W)
        self._table.heading("Group", text="Group", anchor=W)

        self._table.column("#0", width=0, stretch=NO)
        self._table.column("Id", width=30, minwidth=30, anchor=CENTER)
        self._table.column("Name", width=60, minwidth=60, anchor=W)
        self._table.column("Surname", width=90, minwidth=90, anchor=W)
        self._table.column("Username", width=70, minwidth=70, anchor=W)
        self._table.column("Email", width=150, minwidth=150, anchor=W)
        self._table.column("DOB", width=90, minwidth=90, anchor=CENTER)
        self._table.column("Phone", width=105, minwidth=105, anchor=W)
        self._table.column("Address", width=125, minwidth=125, anchor=W)
        self._table.column("Group", width=50, minwidth=50, anchor=W)

        self._table.place(x=frame_y/2, y=20, anchor=N)

        self.__new_record = CTkButton(self._name, text="New Record", width=110, command=self.new_student)
        self.__new_record.place(x=15, y=430, anchor=W)

        self.__update_record = CTkButton(self._name, text="Update Record", width=110, command=self.update_student)
        self.__update_record.place(x=135, y=430, anchor=W)
        self.__update_record.configure(state=DISABLED)

        self.__delete_record = CTkButton(self._name, text="Delete Record", width=110, command=self.remove_student)
        self.__delete_record.place(x=255, y=430, anchor=W)
        self.__delete_record.configure(state=DISABLED)

        back = CTkButton(self._name, text="Back", command=lambda: self.destroy_window("Admin"))
        back.place(x=frame_y/2, y=600, anchor=CENTER)

        c.execute(f"""
        SELECT student.id, name, surname, username, email, dob, phone, address, student_grading.groups.group 
        FROM student_grading.student, student_grading.groups
        where groups_id = student_grading.groups.id;
                """)

        self._table.bind("<ButtonRelease-1>", self.select_record)

        for i in c.fetchall():
            self._table.insert(parent='', index='end', iid=i[0],
                               values=(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]))

    def remove_student(self):
        # Sukuria patvirtinimo dialoga
        box = messagebox.askyesno("Warning!", "Are you sure you want to remove this record?")

        if box:
            self._table.delete(self.__selected)

            c.execute(f"""
            DELETE FROM student WHERE (id = {int(self.__selected)});
            """)
            conn.commit()
        else:
            pass

    def update_student(self):
        self.__update_student = CTk()
        self.__update_student.title("Update student")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_x = int((screen_width / 2) - (400 / 2))
        window_y = int((screen_height / 2) - (600 / 2 + 60))
        self.__update_student.geometry(f'400x650+{window_x}+{window_y-20}')
        self.__update_student.resizable(False, False)

        labels = ("Arial", 14)

        name_label = CTkLabel(self.__update_student, text="Name:", font=labels)
        name_label.place(x=100, y=55, anchor=W)
        name_entry = CTkEntry(self.__update_student, width=200)
        name_entry.place(x=200, y=80, anchor=CENTER)

        surname_label = CTkLabel(self.__update_student, text="Surname:", font=labels)
        surname_label.place(x=100, y=125, anchor=W)
        surname_entry = CTkEntry(self.__update_student, width=200)
        surname_entry.place(x=200, y=150, anchor=CENTER)

        email_label = CTkLabel(self.__update_student, text="Email:", font=labels)
        email_label.place(x=100, y=195, anchor=W)
        email_entry = CTkEntry(self.__update_student, width=200)
        email_entry.place(x=200, y=220, anchor=CENTER)

        dob_label = CTkLabel(self.__update_student, text="Date of Birth:", font=labels)
        dob_label.place(x=100, y=265, anchor=W)
        dob_entry = CTkEntry(self.__update_student, width=200)
        dob_entry.place(x=200, y=290, anchor=CENTER)

        phone_label = CTkLabel(self.__update_student, text="Phone:", font=labels)
        phone_label.place(x=100, y=335, anchor=W)
        phone_entry = CTkEntry(self.__update_student, width=200)
        phone_entry.place(x=200, y=360, anchor=CENTER)

        address_label = CTkLabel(self.__update_student, text="Address:", font=labels)
        address_label.place(x=100, y=405, anchor=W)
        address_entry = CTkEntry(self.__update_student, width=200)
        address_entry.place(x=200, y=430, anchor=CENTER)

        # Gauti visu grupiu pavadinimus
        c.execute("SELECT student_grading.groups.group FROM student_grading.groups")
        groups = []
        for i in c.fetchall():
            for j in i:
                groups.append(j)

        group_label = CTkLabel(self.__update_student, text="Group:", font=labels)
        group_label.place(x=100, y=475, anchor=W)
        group_entry = CTkComboBox(self.__update_student, values=[*groups], width=90)
        group_entry.place(x=100, y=500, anchor=W)

        submit = CTkButton(self.__update_student, text="Submit",
                           command=lambda: self.update_student_submit(name_entry.get(),
                                                                      surname_entry.get(),
                                                                      email_entry.get(),
                                                                      dob_entry.get(),
                                                                      phone_entry.get(),
                                                                      address_entry.get(),
                                                                      group_entry.get()))
        submit.place(x=200, y=610, anchor=CENTER)

        name_entry.insert(0, self.__selection[1])
        surname_entry.insert(0, self.__selection[2])
        email_entry.insert(0, self.__selection[4])
        dob_entry.insert(0, self.__selection[5])
        phone_entry.insert(0, self.__selection[6])
        address_entry.insert(0, self.__selection[7])
        group_entry.set(self.__selection[8])

        self.__update_student.mainloop()

    def update_student_submit(self, name, surname, email, dob, phone, address, group):
        if name != "" and surname != "" and email != '' and dob != "" and phone != "" and address != "" and group != "":
            # Gauti ID
            id = self.__selected

            # Gauti naudotojo varda
            c.execute(f"SELECT student.username FROM student WHERE student.id = {id}")
            for i in c.fetchone():
                username = i

            # Gauti grupes id
            c.execute(f"""SELECT student_grading.groups.id FROM student_grading.groups
            WHERE student_grading.groups.group = '{group}'""")
            for i in c.fetchone():
                group_id = i


            # Atnaujinti lentele
            self._table.item(self.__selected, text="", values=(int(id), name, surname, username, email, dob, phone, address, group))


            # Atnaujinti duomenu baze
            c.execute(f'''
            UPDATE student_grading.student SET
            name = "{name}",
            surname = "{surname}",
            password = "{surname}",
            email = "{email}",
            dob = CAST("{dob}" as DATE),
            phone = "{phone}",
            address = "{address}",
            student.groups_id = {group_id}
            WHERE (id = {id});
            ''')
            conn.commit()

            # Uzdaryti nauja langa
            self.__update_student.destroy()

        else:
            warning = CTkLabel(self.__update_teacher, text="All fields must be filled!", text_color='red')
            warning.place(x=200, y=530, anchor=CENTER)

    def new_student(self):
        self._new_student = CTk()
        self._new_student.title("Add new student")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_x = int((screen_width / 2) - (400 / 2))
        window_y = int((screen_height / 2) - (600 / 2 + 60))
        self._new_student.geometry(f'400x650+{window_x}+{window_y-20}')
        self._new_student.resizable(False, False)

        labels = ("Arial", 14)

        name_label = CTkLabel(self._new_student, text="Name:", font=labels)
        name_label.place(x=100, y=55, anchor=W)
        name_entry = CTkEntry(self._new_student, width=200)
        name_entry.place(x=200, y=80, anchor=CENTER)

        surname_label = CTkLabel(self._new_student, text="Surname:", font=labels)
        surname_label.place(x=100, y=125, anchor=W)
        surname_entry = CTkEntry(self._new_student, width=200)
        surname_entry.place(x=200, y=150, anchor=CENTER)

        email_label = CTkLabel(self._new_student, text="Email:", font=labels)
        email_label.place(x=100, y=195, anchor=W)
        email_entry = CTkEntry(self._new_student, width=200)
        email_entry.place(x=200, y=220, anchor=CENTER)

        dob_label = CTkLabel(self._new_student, text="Date of Birth:", font=labels)
        dob_label.place(x=100, y=265, anchor=W)
        dob_entry = CTkEntry(self._new_student, width=200)
        dob_entry.place(x=200, y=290, anchor=CENTER)

        phone_label = CTkLabel(self._new_student, text="Phone:", font=labels)
        phone_label.place(x=100, y=335, anchor=W)
        phone_entry = CTkEntry(self._new_student, width=200)
        phone_entry.place(x=200, y=360, anchor=CENTER)

        address_label = CTkLabel(self._new_student, text="Address:", font=labels)
        address_label.place(x=100, y=405, anchor=W)
        address_entry = CTkEntry(self._new_student, width=200)
        address_entry.place(x=200, y=430, anchor=CENTER)

        # Gauti grupiu pavadinimus
        c.execute("SELECT student_grading.groups.group FROM student_grading.groups")
        groups = []
        for i in c.fetchall():
            for j in i:
                groups.append(j)

        group_label = CTkLabel(self._new_student, text="Group:", font=labels)
        group_label.place(x=100, y=475, anchor=W)
        group_entry = CTkComboBox(self._new_student, values=[*groups], width=90)
        group_entry.place(x=100, y=500, anchor=W)

        submit = CTkButton(self._new_student, text="Submit", command=lambda: self.new_student_submit(name_entry.get(), surname_entry.get(), email_entry.get(), dob_entry.get(), phone_entry.get(), address_entry.get(), group_entry.get()))
        submit.place(x=200, y=610, anchor=CENTER)

        self._new_student.mainloop()

    def new_student_submit(self, name, surname, email, dob, phone, address, group):
        if name != " " and surname != " " and email != " "  and dob != " " and phone != " " and address != " " and group != " ":
            # Gauti nauja ID
            id = 0
            c.execute("SELECT * FROM student")
            for i in c.fetchall():
                id = i[0]

            new_id = int(id) + 1

            # Gauti grupes id
            c.execute(f"""SELECT student_grading.groups.id FROM student_grading.groups
                        WHERE student_grading.groups.group = '{group}'""")
            for i in c.fetchone():
                group_id = i

            # Gauti naudotojo varda
            c.execute("SELECT student.id FROM student")

            prev_user = ""
            for i in c.fetchall():
                for j in i:
                    prev_user = str(j)

            index = next(i for i, c in enumerate(prev_user) if not c.isalpha())

            alphabetic_part = prev_user[:index]
            numeric_part = int(prev_user[index:]) + 1
            formatted_numeric_part = "{:06d}".format(numeric_part)

            username = alphabetic_part + formatted_numeric_part

            # Ikelti duomenis i lentele
            self._table.insert(parent='', index='end', iid=new_id, values=(new_id, name, surname, username, email, dob, phone, address, group))

            # Ikelti duomenis i duomenu baze
            c.execute(f"""
            INSERT INTO student (id, name, surname, username, password, email, dob, phone, address, student.groups_id)
            VALUES ({int(new_id)}, '{name}', '{surname}', '{username}', '{surname}', '{email}', CAST('{dob}' as DATE), '{phone}', '{address}', {int(group_id)});
            """)
            conn.commit()

            # Sukurti duomenis pazimiu lentelei

            # Gauti nauja id
            id = 0
            c.execute("select id from grades")
            for i in c.fetchall():
                for j in i:
                    id = j + 1

            c.execute(f"""
            select id from subjects where groups_id = {group_id}
            """)

            for i in c.fetchall():
                c.execute(f"""
                INSERT INTO grades (id, Subject_id, Student_id)
                VALUES ({int(id)}, {int(i[0])}, {int(new_id)});
                """)
                conn.commit()

                id += 1

            # Uzdaryti nauja langa
            self._new_student.destroy()

        else:
            warning = CTkLabel(self._new_student, text="All fields must be filled!", text_color='red')
            warning.place(x=200, y=580, anchor=CENTER)

    def select_record(self, e):
        self.__selected = self._table.focus()
        self.__selection = self._table.item(self.__selected, 'values')

        if self.__selected != "":
            self.__update_record.configure(state=NORMAL)
            self.__delete_record.configure(state=NORMAL)

class Login(Window):
    def __init__(self, name):
        self._name = name

    def get_id(self):
        return self._id

    def populate_window(self):
        self.create_window(frame_x, frame_y)

        self.__username_label = CTkLabel(self._name, text="Username:", font=label_font)
        self.__username_label.place(x=frame_y/2-20, y=100, anchor=E)

        self.__username = CTkEntry(self._name, width=200)
        self.__username.place(x=frame_y/2, y=125, anchor=CENTER)

        self.__password_label = CTkLabel(self._name, text="Password:", font=label_font)
        self.__password_label.place(x=frame_y/2-20, y=175, anchor=E)

        self.__password = CTkEntry(self._name, width=200, show="*")
        self.__password.place(x=frame_y/2, y=200, anchor=CENTER)

        submit = CTkButton(self._name, text="Log in", command=self.login_submit)
        submit.place(x=frame_y/2, y=260, anchor=CENTER)

    def login_submit(self):
        user = self.__username.get()
        passw = self.__password.get()
        connected = False

        c.execute("""
        SELECT * FROM admin WHERE BINARY username = %s AND BINARY password = %s 
        """, (user, passw))
        if c.fetchone() is not None:
            c.execute("""
            SELECT id FROM admin WHERE BINARY username = %s AND BINARY password = %s 
            """, (user, passw));

            for i in c.fetchone():
                self._id = i

            connected = True
            self._name.destroy()
            admin.populate_window()

        c.execute("""
        SELECT teacher.id FROM teacher WHERE BINARY username = %s AND BINARY password = %s 
        """, (user, passw))
        if c.fetchone() is not None:
            c.execute("""
            SELECT id FROM teacher WHERE BINARY username = %s AND BINARY password = %s 
            """, (user, passw));

            for i in c.fetchone():
                self._id = i

            connected = True
            self._name.destroy()
            lecturer.populate_window()

        c.execute("""
        SELECT id FROM student WHERE BINARY username = %s AND BINARY password = %s 
        """, (user, passw));
        if c.fetchone() is not None:

            c.execute("""
            SELECT id FROM student WHERE BINARY username = %s AND BINARY password = %s 
            """, (user, passw));

            for i in c.fetchone():
                self._id = i

            connected = True
            self._name.destroy()
            student.populate_window()

        if connected == False:
            wrong = CTkLabel(self._name, text="Username or password is incorrect!", text_color="red")
            wrong.place(x=frame_y/2, y=230, anchor=CENTER)
        else:
            pass


if __name__ == '__main__':

    login = Login("Login")
    student = Student("Student")
    admin = Admin("Admin")
    lecturer = Lecturer("Lecturer")

    # Sukurti pagrindini langa
    root = CTk()
    root.title("Student grading system")

    # Nustatomas lango dydis ir jo pozicija ekrane
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    win_x = int((screen_width / 2) - (window_x /2))
    win_y = int((screen_height / 2) - (window_y / 2 + 60))
    root.geometry(f'{window_x}x{window_y}+{win_x}+{win_y}')
    root.resizable(False, False)

    # Sistemos pavadinimo uzrasas lango virsuje
    welcome = CTkLabel(root, text="Student Grading System", font=("Arial", 24))
    welcome.pack()

    login.populate_window()

    root.mainloop()