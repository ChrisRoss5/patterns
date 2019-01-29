import tkinter as tk
import tkinter.messagebox as msg
import itertools
import time
import webbrowser
import threading
import sqlite3
import smtplib
import os


class ConfigureWindow:

    @staticmethod
    def center_window(window, width, height):
        """Centers the window depending on user's screen resolution."""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        window.geometry('%dx%d+%d+%d' % (width, height, x, y))
        window.resizable(False, False)
        window.attributes("-topmost", True)
        window.bind("<FocusIn>", window.focus_set())


class HyperlinkManager:

    def __init__(self, text):
        """This class is used to add hyperlinks to Text Widgets."""

        self.text = text
        self.text.tag_config("hyper", foreground="red", underline=True)
        self.text.tag_bind("hyper", "<Enter>", self.enter)
        self.text.tag_bind("hyper", "<Leave>", self.leave)
        self.text.tag_bind("hyper", "<Button-1>", self.click)
        self.links = {}

    def add(self, action):
        """Add an action to the manager. Returns tags to use in
        associated text widget."""
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def enter(self, _event_):
        """User's mouse is hovering the link."""
        self.text.config(cursor="hand2")

    def leave(self, _event_):
        """User's mouse is not hovering the link."""
        self.text.config(cursor="")

    def click(self, _event_):
        """Left mouse button has been clicked."""
        for tag in self.text.tag_names(tk.CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()


class LoadingWindow(tk.Toplevel):

    def __init__(self, __master__):
        """This class represents a pop-up window that will load all patterns."""

        # Defining the window
        super().__init__()
        self.master = __master__
        self.iconify()
        self.wm_overrideredirect(True)
        self.deiconify()
        ConfigureWindow.center_window(self, 600, 300)

        # Initializing frames and headline
        self.progress = tk.Canvas(self, height="60", width="600",
                                  highlightthickness=0, bg="#c0d0c0")
        self.progress_info = tk.Canvas(self, height="210", width="600",
                                       highlightthickness=0, bg="white")
        self.progress.create_text(300, 30, text="Loading patterns...",
                                  justify=tk.CENTER,
                                  font=('Roger', '17', 'bold'))

        # Adding text widgets and saving their status id to further change them
        self.progress_status = []
        for i, space in zip(range(4, 10), range(15, 500, 35)):
            self.progress_info.create_text(150, space,
                text="Patterns of length " + str(i) + "...")
            status = self.progress_info.create_text(450, space,
                text="...Pending", fill="red")
            self.progress_status.append(status)
        self.progress_status = iter(self.progress_status)

        # Applying widgets
        self.progress.pack()
        self.progress_info.pack()

        # Perform calculations and update text as each computation is finished
        # Timer is used to get total computation time
        self.timer = time.time()
        self.calculator(4, 10)

    def calculator(self, x, y):
        """Creates all necessary patterns for unlocking an android phone

        All combinations are generated using permutations from itertools module
        and then further filtered by another static method.

        :param x: Min. pattern length
        :param y: Max. (stopping) pattern length
        :return: Calls a main class's method with calculated arguments
        """

        # Storing number of combinations for each pattern length
        combinations = {4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
        # Storing all valid android patterns
        all_patterns = []

        for dots_connected in range(4, 5):  # x, y
            for pattern in list(
                    itertools.permutations("123456789", dots_connected)):
                if self.check_if_pattern_is_valid(pattern):
                    combinations[dots_connected] += 1
                    all_patterns.append(pattern)

            # Updating screen status for current pattern length
            self.progress_info.itemconfig(next(self.progress_status),
                text="Loaded!", fill="green")

        self.master.config(cursor="")
        self.after(300, lambda: LoadingWindow.destroy(self))
        total_time = time.time() - self.timer

        # This class is now finished and won't
        # appear again until user restarts the program
        PatternsUI.patterns_loaded(self.master, all_patterns, combinations,
                                   total_time)

    @staticmethod
    def check_if_pattern_is_valid(permutation) -> bool:
        """Checks if a pattern (permutation) is a valid
        pattern based on pattern rules for android."""
        visited_dots = [permutation[0]]
        for prev, last in enumerate(permutation[1:]):
            prev = permutation[prev]

            # Checking for diagonal, vertical and horizontal jumps
            for a, b, c in zip("379179139137", "111333777999", "245256458568"):
                if last == a and prev == b and c not in visited_dots:
                    return False

            # Checking for horizontal and vertical jumps over middle dot
            for d, e in zip("2846", "8264"):
                if last == d and prev == e and "5" not in visited_dots:
                    return False

            visited_dots.append(last)

        # If pattern satisfies all rules, it's positive
        return True


class Contact(tk.Toplevel):

    def __init__(self, __master__):
        """This class represents a pop-up window that
        will enable user to contact the developer."""

        # Defining the window
        super().__init__()
        self.title("Contact")
        self.configure(background="light gray")
        ConfigureWindow.center_window(self, 500, 300)

        # Adding title and contact email on canvas
        self.canvas = tk.Canvas(self, width=500, height=90,
                                background="light gray", highlightthickness=0)
        self.contact_mail = tk.Canvas(self, width=500, height=100,
                                      background="light gray",
                                      highlightthickness=0)
        self.canvas.create_text(240, 42,
            text="Got any ideas or run into a problem?"
                 "\nEnter your message below.", font=('Roger', '18', 'bold'))
        self.contact_mail.create_text(120, 23, text="Or contact manually:",
            font=('Roger', '10'))
        self.contact_mail.create_text(280, 23, text="kristijan.ros@gmail.com",
            font=('Roger', '10', 'bold', 'italic'))

        # Creating a text field and a button to send
        self.user_msg = None
        self.text_box = tk.Text(self, height=7, width=200)
        self.bind("<FocusIn>", self.text_box.focus_set())
        self.button = tk.Button(self, height=1, width=15, font=("Roger", 16),
                                text="Send message",
                                activebackground="light blue",
                                command=lambda: self.retrieve_input())

        # Adding a copy to clipboard button for mail
        self.copy = tk.Button(self, width=7, font=("Roger", 9), text="Copy",
                              activebackground="light blue",
                              command=self.copy_to_clipboard)

        # Applying widgets
        self.canvas.pack(anchor=tk.N)
        self.text_box.pack()
        self.button.pack()
        self.contact_mail.pack(anchor=tk.N)
        self.copy.place(relx=.75, rely=.86)

    def retrieve_input(self):
        """Picks up what user has entered and sends it if valid."""
        self.attributes("-topmost", False)
        self.user_msg = self.text_box.get("1.0", "end-1c")
        if len(self.user_msg) - self.user_msg.count(" ") < 30:
            msg.showwarning("Message too short",
                            "Your message must contain at least 30 characters.")
            self.attributes("-topmost", True)
            self.bind("<FocusIn>", self.text_box.focus_set())
        else:
            # Use threading to immediately close the window and start sending data
            threading.Thread(target=self.send_data,
                             args=(self.user_msg,)).start()
            self.destroy()

    @staticmethod
    def send_data(message):
        """Sends user's message to developer's e-mail."""
        sender = "ross.data.sender@gmail.com"
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, "sendata587")
            message = 'Subject: {}\n\n{}'.format(
                "Android Unlock Patterns message", message)
            server.sendmail(sender, "kristijan.ros@gmail.com", message)
            msg.showinfo("Message sent",
                         "Your message has been sent successfully.")
            server.quit()
        except smtplib.SMTPException:
            msg.showerror("No connection",
                          "Please check your internet connection and try again.")

    def copy_to_clipboard(self):
        self.attributes("-topmost", False)
        root = self.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append("kristijan.ros@gmail.com")
        msg.showinfo("Copied Successfully", "Text copied to clipboard")
        self.attributes("-topmost", True)


class Usage(tk.Toplevel):

    def __init__(self, __master__):
        """This class represents a pop-up window that
        shows program usage (bindings)"""

        # Defining the window
        super().__init__()
        self.title("Usage")
        ConfigureWindow.center_window(self, 500, 300)

        # Adding widgets
        self.text = tk.Text(self, bg="white", bd=0, relief=tk.SUNKEN,
                            highlightthickness=0, height=16)
        self.button = tk.Button(self, width=90, font=("Roger", 17),
                                text="Got it", activebackground="light green",
                                command=lambda: self.destroy())
        self.text.tag_configure("title", font=('Verdana', 20, 'bold'))
        self.text.tag_configure("binding", font=('Roger', 11, 'bold'))
        self.text.tag_configure("text", font=('Roger', 10))

        # Inserting text to Text widget
        self.text.insert(tk.END, " " * 20 + "Bindings", "title")
        self.text.insert(tk.END, "\n\n\tMouse wheel > ", "binding")
        self.text.insert(tk.END, "Changes animation speed.\n\n", "text")
        self.text.insert(tk.END, "\tUp arrow > ", "binding")
        self.text.insert(tk.END,
                         "Speeds up animation speed by default speed.\n\n",
                         "text")
        self.text.insert(tk.END, "\tDown arrow > ", "binding")
        self.text.insert(tk.END,
                         "Slows down animation speed by default speed.\n\n",
                         "text")
        self.text.insert(tk.END, "\tLeft arrow > ", "binding")
        self.text.insert(tk.END, "\tPauses and skips to next frame.\n\n",
                         "text")
        self.text.insert(tk.END, "\tRight arrow > ", "binding")
        self.text.insert(tk.END, "Pauses and skips to previous frame.\n\n",
                         "text")
        self.text.insert(tk.END, "\tSpace > ", "binding")
        self.text.insert(tk.END, "Pauses/resumes the animation.", "text")
        self.text.configure(state=tk.DISABLED)

        # Applying widgets
        self.text.pack(anchor=tk.CENTER)
        self.button.pack()


class Instructions(tk.Toplevel):

    def __init__(self, __master__):
        """This class represents a pop-up window that
        shows program instructions and recommendations."""

        # Defining the window
        super().__init__()
        self.title("Instructions")
        ConfigureWindow.center_window(self, 500, 300)

        # Creating full-screen canvas with text
        self.canvas = tk.Canvas(self, width=500, height=300,
                                highlightthickness=0, bg="white")
        self.canvas.create_text(250, 35,
            text="This program works best\nwith windows 10.",
            font=("Roger", 17, "bold", "underline"), justify=tk.CENTER)
        self.canvas.create_text(230, 160,
            text="If you are on another OS,\nprogram may not respond "
                 "as intended.\n\n> If you're on older windows version, "
                 "\nconsider upgrading to windows 10.\n> Pay attention "
                 "to your processing power,\nthis program may use lots "
                 "of CPU power.\n> Slow down animation speed if program "
                 "begins lagging,\nyou might cause it to stop working.",
            fill="black", font=("Roger", 13))

        # Adding buttons on canvas
        self.button1 = tk.Button(self, width=20, font=("Roger", 16),
                                 text="Fair enough", activebackground="green",
                                 command=lambda: self.destroy())
        self.button2 = tk.Button(self, width=21, font=("Roger", 16),
                                 text="I disagree", activebackground="red",
                                 cursor="pirate", command=lambda: self.quit())
        self.canvas.create_window(375, 280, window=self.button1)
        self.canvas.create_window(120, 280, window=self.button2)
        self.canvas.pack()


class AboutAuthor(tk.Toplevel):

    def __init__(self, __master__):
        """This class represents a pop-up window that shows author's word."""

        # Defining the window
        super().__init__()
        self.title("Author")
        ConfigureWindow.center_window(self, 500, 300)

        # Adding widgets
        self.text = tk.Text(self, bg="white", bd=0, highlightthickness=0,
                            font=("Roger", 14, "italic"), height=11)
        self.scroll = tk.Scrollbar(self, command=self.text.yview)
        self.button = tk.Button(self, width=60, font=("Roger", 17),
                                text="Close", activebackground="light green",
                                command=lambda: self.destroy())
        self.text.tag_configure("title", font=('Verdana', 22, 'bold'))
        self.text.tag_configure("text", font=('Roger', 16, 'italic'))
        self.hyperlink = HyperlinkManager(self.text)

        # Inserting text to Text widget
        self.text.insert(tk.END, " " * 14 + "Hello user!\n\n", 'title')
        self.text.insert(tk.END,
                         "   It's KristijanRoss.\n   I developed this program."
                         "\n\n   If you have any questions or ideas on how"
                         "\n   to improve it, send them here: Help > ", 'text')
        self.text.insert(tk.INSERT, "Contact.",
                         self.hyperlink.add(self.contact_shortcut))
        self.text.insert(tk.END,
                         "\n\n   This program will remain free to use as\n"
                         "   long as you are subscribed to Pewdiepie.\n"
                         "   Subscribe to Pewdiepie ", 'text')
        self.text.insert(tk.INSERT, "here.",
                         self.hyperlink.add(self.sub_to_pewds))
        self.text.insert(tk.END, "\n   (if you haven't already).\n", 'text')
        self.text.configure(yscrollcommand=self.scroll.set, state=tk.NORMAL)

        # Applying widgets
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(anchor=tk.CENTER)
        self.button.pack()

    def contact_shortcut(self):
        """Replaces current window with new Contact window."""
        self.destroy()
        Contact(self)

    def sub_to_pewds(self):
        """Replaces current window with new browser tab."""
        self.destroy()
        webbrowser.open_new(
            "https://www.youtube.com/subscription_center?add_user=PewDiePie")


class AboutProgram(tk.Toplevel):

    def __init__(self, __master__):
        """This class represents a pop-up window that shows program features."""

        # Defining the window
        super().__init__()
        self.title("About")
        ConfigureWindow.center_window(self, 600, 348)

        # Adding widgets
        self.text = tk.Text(self, bg="light gray", bd=9, highlightthickness=0,
                            font=("Roger", 16, "italic"), height=12)
        self.scroll = tk.Scrollbar(self, command=self.text.yview)
        self.button = tk.Button(self, width=90, font=("Roger", 15),
                                text="Close", activebackground="light blue",
                                command=lambda: self.destroy())
        self.text.tag_configure("title", font=('Verdana', 19, 'bold'))
        self.text.tag_configure("text", font=('Roger', 14))
        self.hyperlink = HyperlinkManager(self.text)

        # Inserting text to Text widget
        self.text.insert(tk.END, "Patterns\n", "title")
        for dots, combinations in enumerate(__master__.combinations.values(),
                                            start=1):
            self.text.insert(tk.END, "> Combinations with " + str(
                dots) + " dots connected: " + str(combinations) + "\n", "text")
        self.text.insert(tk.END, " " * 33 + "Total combinations: " + str(
            sum(__master__.combinations.values())) + "\n\nIt took " + str(
            round(__master__.total_time,
                  5)) + " seconds for your computer to calculate them.\n"
                        "Highest recorded frame rate on your pc: " + str(
            Settings.run_query(receive=True)[3][0]) + "\n\n", "text")
        self.text.insert(tk.END, "Source code\n", "title")
        self.text.insert(tk.END, "> This program was written in Python 3.6.6.\n"
                                 "> It has over 1000 lines of code.\n"
                                 "> However, it's clean, user friendly and "
                                 "well documented.\n> Only standard python "
                                 "packages were used.\n\n", "text")
        self.text.insert(tk.END, "Usage\n", "title")
        self.text.insert(tk.END, "> Learning permutations on data items.\n"
                                 "> Practicing with Tkinter module and testing "
                                 "its limits.\n"
                                 "> Testing the power of CPU and its usage.\n\n",
                         'text')
        self.text.insert(tk.END, "Idea\n", "title")
        self.text.insert(tk.END, "Randomly saw ", 'text')
        self.text.insert(tk.INSERT, "this video",
                         self.hyperlink.add(self.yt_video))
        self.text.insert(tk.END, " on youtube. \n", 'text')
        self.text.configure(yscrollcommand=self.scroll.set, state=tk.DISABLED)

        # Applying widgets
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(anchor=tk.CENTER)
        self.button.pack()

    def yt_video(self):
        """Replaces current window with new browser tab."""
        self.destroy()
        webbrowser.open_new(
            "https://www.youtube.com/watch?v=D9dXrKUCfO0&t=154s")


class AddPattern(tk.Toplevel):

    def __init__(self, __master__):
        """This class represents a pop-up window in which user will
        enter a pattern that will be added to a collection MyPatterns."""

        # Defining the window
        super().__init__()
        self.title("Add a pattern")
        ConfigureWindow.center_window(self, 300, 32)

        # Adding text box with a save button
        self.user_msg = tk.StringVar()
        self.text_box = tk.Entry(self, width=15, textvariable=self.user_msg,
                                 font=("Verdana", 17))
        self.bind("<FocusIn>", self.text_box.focus_set())
        self.save_button = tk.Button(self, width=10, text="Save",
                                     state=tk.DISABLED, font=("Verdana", 12),
                                     activebackground="light green",
                                     relief=tk.SUNKEN,
                                     command=self.save_pattern)
        self.message = tk.Canvas(self, width=300, height=25,
                                 highlightthickness=0, bg="white")
        self.existing = [x[0] for x in Settings.run_query(receive=True)[2]]
        self.user_msg.trace("w", self.check_input)

        # Applying widgets
        self.save_button.pack(side=tk.RIGHT, anchor=tk.N)
        self.text_box.pack(side=tk.LEFT, anchor=tk.N)

    def check_input(self, *_events_):
        """Checks user's input in real time and shows appropriate message."""
        user_input = self.user_msg.get()
        no_letters = all(
            [x if x.isdigit() else False for x in self.user_msg.get()])
        no_duplicates = len(set(user_input)) == len(user_input)

        def show_message(message):
            self.message.create_text(145, 14, text=message,
                font=("Verdana", 9, "italic"), fill="red", justify=tk.CENTER)

        if 3 < len(
                user_input) < 10 and no_letters and no_duplicates and "0" not in user_input and user_input not in self.existing:
            self.message.place_forget()
            self.save_button.configure(state=tk.NORMAL, relief=tk.RAISED)
            self.geometry("300x32")
        else:
            self.message.delete("all")
            self.save_button.configure(state=tk.DISABLED, relief=tk.SUNKEN)
            self.geometry("300x55")
            user_input = [x for x in self.user_msg.get() if
                          x.isdigit() and x != "0"]
            if "".join(user_input) in self.existing:
                show_message("Already saved pattern.")
            elif 3 < len(user_input) < 10 and len(set(user_input)) == len(
                    user_input):
                user_input = "-".join(user_input)
                show_message(f"Did you mean {user_input}?")
            elif not no_duplicates and no_letters:
                show_message("Numbers are repeating.")
            else:
                show_message("Enter 4 to 9 different digits except 0.")
            self.message.place(relx=0.0, rely=0.5)

    def save_pattern(self):
        """Saves a valid pattern."""
        Settings.run_query(save=self.user_msg.get(), table="my_patterns")
        self.destroy()


class MyPatterns(tk.Toplevel):

    def __init__(self, __master__):
        """This class represents a pop-up window that shows all saved patterns."""

        # Defining the window
        super().__init__()
        self.title("My patterns")
        self.master = __master__
        self.configure(background="white")
        ConfigureWindow.center_window(self, 500, 300)

        # Adding widgets to further fill them
        self.paths = None
        self.all_selected = tk.IntVar()
        self.all_buttons = {}
        self.selected_buttons = []
        self.canvas = self.vbar = self.select_all = None
        self.close = self.delete = self.add = self.show = None
        self.show_saved_patterns()

    def show_saved_patterns(self):
        """This method is called whenever something is modified."""

        # https://stackoverflow.com/questions/7727804/tkinter-using-scrollbars-on-a-canvas
        self.paths = Settings.run_query(receive=True)[2]
        self.frame = tk.Frame(self, width=300, height=225)
        self.canvas = tk.Canvas(self.frame, bg='#FFFFFF', width=300, height=10,
                                scrollregion=(0, 0, 0, len(self.paths) * 38))
        self.vbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(width=475, height=225)
        self.canvas.config(yscrollcommand=self.vbar.set)

        self.canvas.create_text(240, 30, text="My patterns (auto-saved)",
                                font=('Roger', '20', 'bold'))

        if not self.paths:
            self.canvas.create_text(240, 125, text="Empty", fill="light gray",
                                    font=('Roger', '40', 'bold'))
        else:
            self.select_all = tk.Checkbutton(self.canvas,
                variable=self.all_selected, selectcolor='light blue',
                bg="white", bd=8, command=self.select_all_buttons)
            self.canvas.create_window(35, 30, window=self.select_all)

        self.close = tk.Button(self, width=9, height=1, font=("Verdana", 16),
                               activebackground="light blue", text="Close",
                               command=lambda: self.destroy())
        self.delete = tk.Button(self, width=9, height=1, font=("Verdana", 16),
                                activebackground="red", text="Delete",
                                command=lambda: self.delete_pattern())
        self.add = tk.Button(self, width=9, height=1, font=("Verdana", 16),
                             activebackground="green", text="Add",
                             command=lambda: self.add_pattern())
        self.show = tk.Button(self, width=9, height=1, font=("Verdana", 16),
                              activebackground="light green", text="Show",
                              command=lambda: self.show_selected_patterns())
        for pattern, space in zip(self.paths,
                range(75, 76 + len(self.paths) * 32, 32)):
            pattern = " - ".join(pattern[0])
            button = tk.Button(self, width=47, height=1, font=("Verdana", 12),
                               text=f"{pattern}", activebackground="purple",
                               command=lambda p=pattern: self.select_button(p))
            self.all_buttons[pattern] = button
            self.canvas.create_window(237, space, window=button)

        self.frame.pack()
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT)
        self.close.pack(side=tk.LEFT, anchor=tk.S)
        self.delete.pack(side=tk.LEFT, anchor=tk.S)
        self.add.pack(side=tk.LEFT, anchor=tk.S)
        self.show.pack(side=tk.LEFT, anchor=tk.S)

    def select_all_buttons(self):
        """Selects or deselects all buttons."""
        self.selected_buttons = []
        if self.all_selected.get():
            for button in self.all_buttons.keys():
                self.selected_buttons.append(button)
                self.all_buttons[button].configure(relief=tk.SUNKEN,
                                                   background="light blue")
        else:
            for button in self.all_buttons.values():
                button.configure(relief=tk.RAISED,
                                 background="SystemButtonFace")

    def select_button(self, pattern):
        """Shows which buttons are selected/unselected."""
        if pattern in self.selected_buttons:
            self.selected_buttons.remove(pattern)
            self.all_buttons[pattern].configure(relief=tk.RAISED,
                background="SystemButtonFace")
        else:
            self.selected_buttons.append(pattern)
            self.all_buttons[pattern].configure(relief=tk.SUNKEN,
                background="light blue")

    def refresh(self):
        """Refreshes the screen after changes were made."""

        def all_children(window) -> list:
            children = window.winfo_children()
            for w in children:
                if w.winfo_children():
                    children.extend(w.winfo_children())
            return children

        [item.pack_forget() for item in all_children(self)]
        self.all_buttons = {}
        self.selected_buttons = []
        # When everything is deleted and reset, create it again
        self.show_saved_patterns()

    def add_pattern(self):
        """Waits until user adds a new pattern and then refreshes."""
        self.wait_window(AddPattern(self))
        self.refresh()

    def delete_pattern(self):
        """Deletes selected patterns."""
        if not self.selected_buttons:
            return self.nothing_selected()
        for pattern in self.selected_buttons:
            Settings.run_query(
                save="".join([x for x in pattern if x.isdigit()]),
                table="delete")
        self.refresh()

    def show_selected_patterns(self):
        """Displays selected patterns."""
        if not self.selected_buttons:
            return self.nothing_selected()
        combinations = [[y for y in x if y.isdigit()] for x in
                        self.selected_buttons]
        PatternsUI.start_animation(self.master, start_all=False,
            show_saved=combinations)

    def nothing_selected(self):
        """Displays an error message."""
        self.attributes("-topmost", False)
        msg.showerror("Error", "You haven't selected anything.")
        self.attributes("-topmost", True)


class SelectPatterns(tk.Toplevel):

    def __init__(self, __master__):
        """This class represents a pop-up window that enables
         user to choose which patterns will be displayed."""

        # Defining the window
        super().__init__()
        self.title("Selection")
        self.master = __master__
        ConfigureWindow.center_window(self, 500, 300)

        # Creating main canvas
        self.canvas = tk.Canvas(self, width=500, height=300,
                                highlightthickness=0, bg="white")

        # Adding widgets to main canvas
        self.variables = [tk.IntVar() for _ in range(7)]
        self.canvas.create_text(250, 30, text="Select patterns",
                                font=('Roger', '20', 'bold'))
        self.canvas.create_text(240, 80,
                                text="Choose which patterns will be displayed.",
                                font=('Verdana', '12'))
        self.save_button = tk.Button(self, width=38, font=("Verdana", 15),
                                     relief=tk.RAISED, text="Save",
                                     activebackground="green", state=tk.NORMAL,
                                     command=self.save_changes)

        self.check_buttons = []
        for variable, x, n in zip(self.variables, range(60, 700, 72),
                                  range(4, 11)):
            self.check_buttons.append(
                tk.Checkbutton(self.canvas, variable=variable,
                    selectcolor='light blue', bg="white", bd=5))
            if n < 10:
                self.canvas.create_text(x, 150, text=f"{n} dots",
                                        font=('Verdana', '8'))

        self.saved_settings = Settings.run_query(receive=True)[1]
        for x, y in zip(self.saved_settings, self.check_buttons):
            if x:
                y.select()

        # Applying widgets
        self.canvas.create_window(250, 280, window=self.save_button)
        for button, x in zip(self.check_buttons, range(11, 100, 14)):
            if x == 95:
                self.canvas.create_text(217, 209, text="Reverse order: ",
                                        font=('Verdana', '12'))
                button.place(relx=.62, rely=.65)
            else:
                button.place(relx=float(".{}".format(x)), rely=.35)

        self.canvas.pack()
        self.changes = None

    def save_changes(self):
        """Saves changes made after user clicks 'save'."""
        self.changes = [x.get() for x in self.variables]
        if any(self.changes[:-1]):
            self.master.menus[0].entryconfig("Start selected", state=tk.NORMAL)
        else:
            self.master.menus[0].entryconfig("Start selected",
                                             state=tk.DISABLED)
        Settings.run_query(save=self.changes, table="patterns")
        PatternsUI.apply_selected_patterns(self.master, self.changes)
        self.destroy()


class Settings(tk.Toplevel):

    def __init__(self, __master__):
        """This class represents a pop-up window that shows
        program settings which user can change and save anytime."""

        # Defining the window
        super().__init__()
        self.title("Settings")
        self.master = __master__
        ConfigureWindow.center_window(self, 500, 300)

        # Creating main canvas
        self.canvas = tk.Canvas(self, width=500, height=300,
                                highlightthickness=0, bg="white")

        # Adding widgets to main canvas
        self.show_real_fps = tk.IntVar()
        self.ms = tk.IntVar()
        self.delta = tk.IntVar()
        self.canvas.create_text(250, 30, text="Settings",
                                font=('Roger', '20', 'bold'))
        self.canvas.create_text(160, 80, text="Show real time frame rate:",
                                font=('Verdana', '12'))
        self.canvas.create_text(250, 120, text="Choose default speed:",
                                font=('Verdana', '12'))
        self.canvas.create_text(250, 190, text="Choose mousewheel sensitivity:",
                                font=('Verdana', '12'))
        self.cancel_button = tk.Button(self, width=19, font=("Verdana", 15),
                                       text="Done", command=self.destroy)
        self.apply_button = tk.Button(self, width=19, font=("Verdana", 15),
                                      relief=tk.SUNKEN, text="Save",
                                      activebackground="green",
                                      bg="light green", state=tk.DISABLED,
                                      command=self.save_changes)
        self.real_fps = tk.Checkbutton(self.canvas, variable=self.show_real_fps,
            selectcolor='light blue', bg="white", bd=15)
        self.ms_scale = tk.Scale(self.canvas, from_=1000, to=1,
                                 variable=self.ms, width=8, length=399,
                                 repeatdelay=1, repeatinterval=2,
                                 highlightthickness=0, bg="white",
                                 orient=tk.HORIZONTAL, sliderlength=65)
        self.delta_scale = tk.Scale(self.canvas, from_=1, to=300,
                                    variable=self.delta, width=8, length=399,
                                    repeatdelay=1, repeatinterval=6,
                                    highlightthickness=0, bg="white",
                                    orient=tk.HORIZONTAL, sliderlength=65)

        # Applying settings to widgets
        self.saved_settings = self.run_query(receive=True)[0]
        if self.saved_settings[0]:
            self.real_fps.select()
        self.ms_scale.set(self.saved_settings[1])
        self.delta_scale.set(self.saved_settings[2])

        # If changes were made, show button again.
        self.show_real_fps.trace("w", self.show_button)
        self.ms.trace("w", self.show_button)
        self.delta.trace("w", self.show_button)

        # Applying widgets
        self.canvas.create_window(125, 280, window=self.cancel_button)
        self.canvas.create_window(375, 280, window=self.apply_button)
        self.real_fps.place(relx=.8, rely=.18)
        self.ms_scale.place(relx=.1, rely=.44)
        self.delta_scale.place(relx=.1, rely=.67)
        self.canvas.pack()
        self.changes = None

    def show_button(self, *_events_):
        """Shows button 'save' if changes were made."""
        self.changes = (
        self.show_real_fps.get(), self.ms.get(), self.delta.get())
        PatternsUI.apply_settings(self.master, self.changes)

        if self.changes == self.saved_settings:
            self.apply_button.configure(relief=tk.SUNKEN, bg="light green",
                state=tk.DISABLED)
        else:
            self.apply_button.configure(relief=tk.RAISED, bg="SystemButtonFace",
                state=tk.NORMAL)

    def save_changes(self):
        """Saves changes made after user clicks 'save'."""
        self.run_query(save=self.changes, table="settings")
        self.saved_settings = self.run_query(receive=True)[0]
        self.apply_button.configure(relief=tk.SUNKEN, bg="light green",
                                    state=tk.DISABLED)

    @staticmethod
    def run_query(save=None, receive=False, new_db=False, table=None):
        """Saves user's settings."""
        conn = sqlite3.connect("user_settings.db")
        cursor = conn.cursor()

        if new_db:
            with conn:  # Another way to commit changes
                cursor.execute("""CREATE TABLE settings (
                            show_real_fps integer,
                            ms_pause integer,
                            mousewheel_delta integer
                            )""")
                cursor.execute("""CREATE TABLE selected_patterns (
                            len4 integer, len5 integer,
                            len6 integer, len7 integer,
                            len8 integer, len9 integer,
                            reverse integer
                            )""")
                cursor.execute("""CREATE TABLE my_patterns (pattern text)""")
                cursor.execute("""CREATE TABLE highest_fps (fps integer)""")

                """Setting up default settings"""
                cursor.execute("INSERT INTO settings VALUES (0, 500, 150)")
                cursor.execute("INSERT INTO selected_patterns "
                               "VALUES (0, 0, 0, 0, 0, 0, 0)")
                cursor.execute("INSERT INTO highest_fps VALUES (2)")
        elif receive:
            tables = []
            cursor.execute("SELECT * FROM settings")
            tables.append(cursor.fetchall()[0])
            cursor.execute("SELECT * FROM selected_patterns")
            tables.append(cursor.fetchone())
            cursor.execute("SELECT * FROM my_patterns")
            tables.append(cursor.fetchall())
            cursor.execute("SELECT * FROM highest_fps")
            tables.append(cursor.fetchone())
            return tables
        elif table == "settings":
            # Saving with a dictionary
            cursor.execute("""UPDATE settings SET
            show_real_fps = :show_real_fps,
            ms_pause = :ms_pause,
            mousewheel_delta = :mousewheel_delta""",
                           {"show_real_fps": save[0], "ms_pause": save[1],
                               "mousewheel_delta": save[2]})
        elif table == "patterns":
            # Saving with a tuple
            cursor.execute("""UPDATE selected_patterns SET
                        len4 = ?, len5 = ?, len6 = ?,
                        len7 = ?, len8 = ?, len9 = ?,
                        reverse = ?""", (*save,))
        elif table == "delete":
            cursor.execute("DELETE FROM my_patterns WHERE pattern = ?", [save])
        elif table == "set_highest":
            cursor.execute("UPDATE highest_fps SET fps = ?", [save])
        else:
            cursor.execute("INSERT INTO my_patterns VALUES (?)", [save])

        conn.commit()
        conn.close()


class PatternsUI(tk.Tk):

    def __init__(self):
        """This is a main class (window) that is always on user's screen."""

        # Defining the window
        super().__init__()
        self.title("Android Unlock Patterns")
        ConfigureWindow.center_window(self, 900, 550)
        self.attributes("-topmost", False)

        # Adding standard windows menus
        self.menu_bar = tk.Menu(self)
        self.menus = [
            tk.Menu(self.menu_bar, tearoff=0, activebackground="light gray",
                    activeforeground="red") for _menu_ in range(5)]
        self.menu_indices = [0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3]
        self.sub_menu_names = ["Start all", "Start selected", "Settings...",
                               "Select patterns...", "Add a pattern...",
                               "My patterns", "Program", "Instructions",
                               "Author", "Usage", "Contact the developer"]
        self.menu_commands = [(self.start_animation, True),
                              (self.start_animation, False), Settings,
                              SelectPatterns, AddPattern, MyPatterns,
                              AboutProgram, Instructions, AboutAuthor, Usage,
                              Contact]
        for i, (x, y, z) in enumerate(
                zip(self.menu_indices, self.sub_menu_names,
                    self.menu_commands)):
            if i in (1, 5, 8, 10, 12):
                self.menus[x].add_separator()
            if isinstance(z, tuple):
                self.menus[x].add_command(label=y,
                                          command=lambda c=z[0], arg=z[1]: c(
                                              arg))
                continue
            self.menus[x].add_command(label=y, command=lambda c=z: c(self))
        self.menus[4].add_command(label="Exit", command=self.confirm_exit)
        self.menus[0].entryconfig("Start all", state=tk.DISABLED)
        self.menus[0].entryconfig("Start selected", state=tk.DISABLED)
        self.menus[2].entryconfig("Program", state=tk.DISABLED)

        for label, menu in zip(("Start", "Options", "About", "Help", "Exit"),
                               self.menus):
            self.menu_bar.add_cascade(label=label, menu=menu)
        self.config(menu=self.menu_bar)

        # Initializing frames
        self.headline = tk.Canvas(self, height=80, width=900,
                                  highlightthickness=0, bg="#c0c0c0")
        self.patterns_bar = tk.Canvas(self, height=20, width=900,
                                      highlightthickness=0, bg="white")
        self.information = tk.Canvas(self, height=450, width=450,
                                     highlightthickness=0, bg="#c0c0c0")
        self.pattern = tk.Canvas(self, height=450, width=450,
                                 highlightthickness=0)

        # Adding widgets to frames
        self.main_title = "This program shows all possible combinations" \
                          " of unlocking an android phone\nwith a " \
                          "pattern of length between 4 and 9 dots"
        self.information.create_text(220, 220, text="Waiting...", fill="white",
                                     justify=tk.CENTER,
                                     font=('Verdana', '35', 'italic'))
        self.headline.create_text(450, 40, text=self.main_title,
                                  justify=tk.CENTER, font=('Verdana', '15'))
        self.pattern_bg = tk.PhotoImage(data=pattern_background)
        self.pattern.create_image(0, 0, image=self.pattern_bg, anchor='nw')
        self.save_button = tk.Button(self, width=30, font=("Verdana", 15),
                                     bg="#abe5a2", text="Save this pattern",
                                     activebackground="green",
                                     command=self.save_current_pattern)

        # Applying widgets
        self.headline.pack(expand=True, side="top", anchor=tk.N)
        self.patterns_bar.pack(expand=True, side="top", anchor=tk.N)
        self.information.pack(expand=True, side="left", anchor=tk.SW)
        self.pattern.pack(expand=True, side="right", anchor=tk.SE)
        self.save_button.bind("<Enter>", self.hover_on)
        self.save_button.bind("<Leave>", self.hover_off)

        # Adding colors that will be used for arrows
        self.colors = [c + "0000" for c in (
        '#33', '#4c', '#66', '#7f', '#99', '#b2', '#cc', '#e5', '#ff')]

        # X and Y screen points to connect arrows
        self.screen_coords = {1: (68, 50), 2: (224, 50), 3: (380, 50),
                              4: (68, 213), 5: (224, 213), 6: (380, 213),
                              7: (68, 376), 8: (224, 376), 9: (380, 376)}

        # Since Tkinter doesn't have precise timing, average
        # fps will be used on high speeds, below 16 ms pause
        self.average = {1: 250, 2: 220, 3: 210, 4: 175, 5: 140, 6: 130, 7: 115,
                        8: 100, 9: 90, 10: 85, 11: 80, 12: 75, 13: 72, 14: 69,
                        15: 66}

        # Adding buttons to change animation speed
        self.pattern.bind_all('<Up>', self.speed_up_or_slow_down)
        self.pattern.bind_all('<Down>', self.speed_up_or_slow_down)
        self.pattern.bind_all('<Left>', self.previous_or_next_frame)
        self.pattern.bind_all('<Right>', self.previous_or_next_frame)
        self.pattern.bind_all('<space>', self.pause_animation)
        self.pattern.bind_all('<MouseWheel>', self.mouse_wheel)

        # Initializing data structures to further add a collections of data items
        self.all_patterns = None  # all patterns are here
        self.combinations = None  # N of patterns for each pattern length
        self.total_time = None  # total computation time to get all patterns
        self.patterns = None  # Patterns that will be displayed
        self.total_patterns = None  # Depending on chosen patterns
        self.patterns_shown = None  # Depending on chosen patterns

        # These default cache values can be changed by user
        self.saved_settings = Settings.run_query(receive=True)[
            0]  # Load settings
        self.show_real_fps = self.saved_settings[0]  # bool integer
        self.highest_fps = Settings.run_query(receive=True)[3][
            0]  # available in About class
        self.sleep_ms = self.saved_settings[1]  # in milli-seconds
        self.speed_increment = self.saved_settings[2]  # in milli-seconds
        self.chosen_combinations = Settings.run_query(receive=True)[1][
                                   :-1]  # list with selected patterns
        self.reversed = Settings.run_query(receive=True)[1][
            -1]  # play animation in reversed order

        self.paused = False  # paused == True when paused
        self.animating = False  # to allow bindings only when animating
        self.timer = None  # to measure real time frame rate (available in settings)
        self.start_while_waiting = True  # to prevent animation from restarting
        self.current_path = None  # to save pattern when paused
        self.show_saved_pattern = None  # shows saved patterns

        # Start loading all patterns
        self.load_patterns()

    def load_patterns(self):
        """Calls a LoadingWindow class that will be
         shown on top until everything is loaded."""
        self.config(cursor="wait")
        # Use threading to actually see the loading progress
        self.after(250,
                   threading.Thread(target=LoadingWindow, args=(self,)).start())

    def patterns_loaded(self, all_patterns, combinations, total_time):
        """Method to save all previously calculated data."""
        self.all_patterns = all_patterns
        self.combinations = combinations
        self.total_time = total_time
        self.menus[0].entryconfig("Start all", state=tk.NORMAL)
        self.menus[2].entryconfig("Program", state=tk.NORMAL)
        if any(self.chosen_combinations):
            self.menus[0].entryconfig("Start selected", state=tk.NORMAL)

    def save_current_pattern(self):
        self.save_button.configure(state=tk.DISABLED, relief=tk.SUNKEN)
        Settings.run_query(save="".join(self.current_path), table="my_patterns")

    def apply_selected_patterns(self, patterns):
        """Applies patterns which user has selected."""
        self.chosen_combinations = patterns[:-1]
        self.reversed = patterns[-1]

    def apply_settings(self, settings):
        """Applies user settings in real time."""
        self.show_real_fps = settings[0]
        self.sleep_ms = settings[1]
        self.speed_increment = settings[2]

    def confirm_exit(self):
        """Gives user a last chance not to exit the program."""
        if msg.askyesno("Confirm", "Are you sure you want to exit?"):
            self.quit()

    def speed_up_or_slow_down(self, _event_):
        """Speeds up or slows down the animation by 1 ms."""
        if self.animating and not self.paused:
            if _event_.keysym == "Up":
                if self.sleep_ms > 1:
                    self.sleep_ms -= 1
            else:
                self.sleep_ms += 1

    def previous_or_next_frame(self, _event_, first=False):
        """Pauses and shows previous/next frame."""
        if self.animating:
            if _event_.keysym != "Right" and self.patterns_shown > 0:
                self.patterns_shown -= 1
            if self.sleep_ms == 1 and not first:
                self.patterns_shown -= 1
            if self.paused:
                self.paused = False
                self.after(2,
                           lambda: self.previous_or_next_frame(_event_, True))
            else:
                self.paused = True

    def mouse_wheel(self, _event_):
        """Slows/Speeds up the animation by user's configuration."""
        if self.animating and not self.paused:
            if _event_.delta < 0:
                self.sleep_ms += self.speed_increment
            elif self.sleep_ms - self.speed_increment > 1:
                self.sleep_ms -= self.speed_increment
            else:
                self.sleep_ms = 1

    def hover_on(self, _event_):
        """Changes a button when mouse is hovering."""
        self.save_button['background'] = '#57c446'

    def hover_off(self, _event_):
        """Changes a button when mouse is not hovering."""
        self.save_button['background'] = '#abe5a2'

    def start_animation(self, start_all, show_saved=None):
        """Starts all or chosen combinations."""

        self.show_saved_pattern = False
        self.paused = False
        self.patterns_shown = 0
        self.sleep_ms = Settings.run_query(receive=True)[0][1]

        if start_all:
            self.total_patterns = len(self.all_patterns)
            self.patterns = self.all_patterns
        elif show_saved:
            self.show_saved_pattern = True
            self.total_patterns = len(show_saved)
            self.patterns = show_saved
        else:
            # Get chosen combinations by filtering all patterns
            selected_lengths = [n for n, x in
                                enumerate(self.chosen_combinations, start=4) if
                                x]
            selected_patterns = [p for p in self.all_patterns if
                                 len(p) in selected_lengths]
            self.total_patterns = len(selected_patterns)
            self.patterns = selected_patterns
            if self.reversed:
                self.patterns = self.patterns[::-1]

        # User can now use controls
        if self.start_while_waiting:
            self.timer = time.time()
            self.start_while_waiting = False
            self.animating = True
            self.animation()
        else:
            self.animating = False
            self.restart_animation()

    def pause_animation(self, _event_):
        """(un)Pauses the animation."""
        if self.animating:
            if self.paused:
                self.paused = False
            else:
                self.paused = True

    def restart_animation(self):
        """This method is called only while animation is running.
        It interrupts it and starts a new one."""
        self.paused = False
        if not self.animating:
            self.after(10, self.restart_animation)
        else:
            self.timer = time.time()
            self.animation()

    @staticmethod
    def line_maker(screen_points) -> tuple:
        """Creates a line out of given screen points."""
        is_first, x0, y0 = True, 0, 0
        for (x, y) in screen_points:
            if is_first:
                x0, y0, is_first = x, y, False
            else:
                yield x0, y0, x, y
                x0, y0 = x, y

    def find_intersection(self, x1, y1, x2, y2, x3, y3, x4, y4):
        """Checks if lines are intersecting

        :param x1: Starting x point of first line
        :param y1: Starting y point of first line
        :param x2: Ending point x of first line
        :param y2: Ending point y of first line
        :param x3: Starting x point of second line
        :param y3: Starting y point of second line
        :param x4: Ending point x of second line
        :param y4: Ending point y of second line
        :returns: X and Y coordinates of intersection or
        True if lines are overlapping
        :rtype: tuple / bool
        """

        try:
            # Formula from https://en.wikipedia.org/wiki/Line-line_intersection
            px = int(((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (
                        x3 * y4 - y3 * x4)) / (
                                 (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)))
            py = int(((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (
                        x3 * y4 - y3 * x4)) / (
                                 (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)))
        except ZeroDivisionError:
            if ((x4 - x1) ** 2 + (
                    y4 - y1) ** 2) ** 0.5 < 310 and x2 + y2 == x3 + y3:
                # Lines are overlapping
                return True
            return False

        # Check if intersection point is on both lines and ignore
        # points where one line ends, and another continues
        if (px, py) not in self.screen_coords.values() and (
                (x1 < px < x2 or y1 < py < y2) or (
                x1 > px > x2 or y1 > py > y2)) and (
                (x3 < px < x4 or y3 < py < y4) or (
                x3 > px > x4 or y3 > py > y4)):
            return int(px), int(py)
        return False

    def animation(self):
        """Method to show animation."""

        # If another animation has been started, stop this one,
        # and start the new one
        if not self.animating:
            self.animating = True
            return

        # Refresh both pattern and information canvas to add new
        # information and new pattern as well as pattern progress bar
        self.patterns_bar.delete("all")
        self.pattern.delete("all")
        self.information.delete("all")
        self.patterns_shown += 1
        patterns_left = self.total_patterns - self.patterns_shown
        bar_position = (self.patterns_shown / self.total_patterns) * 900
        percentage = int((self.patterns_shown / self.total_patterns) * 100)
        self.patterns_bar.create_rectangle(-1, -1, bar_position, 20,
                                           fill="green", width=0)
        self.patterns_bar.create_text(450, 10, text=f"{percentage}%",
            justify=tk.CENTER)

        # Choose next pattern if available
        try:
            self.current_path = self.patterns[self.patterns_shown - 1]
        except IndexError:
            self.animating = False
            self.start_while_waiting = True
            if not self.show_saved_pattern:
                if msg.askyesno("Finished",
                                "All patterns have been shown. Replay?"):
                    if self.patterns_shown == len(self.all_patterns):
                        self.start_animation(True)
                    else:
                        self.start_animation(False)
            self.patterns_bar.delete("all")
            self.information.create_text(220, 220, text="Waiting...",
                fill="white", justify=tk.CENTER,
                font=('Verdana', '35', 'italic'))
            self.pattern.create_image(0, 0, image=self.pattern_bg, anchor='nw')
            return

        # To find all intersections and lines
        lines = []
        intersections = []
        coords = [self.screen_coords[int(x)] for x in self.current_path]

        # Loop through lines and check if the current line
        # has any intersections with all previous lines
        # x0 and y0 are starting points (coordinates) while
        # x1 and y1 are ending points of one line
        for (x0, y0, x1, y1) in self.line_maker(coords):
            lines.append((x0, y0, x1, y1))
            if len(lines) > 1:
                for line in lines[:-1]:
                    intersections.append(
                        self.find_intersection(*line, *lines[-1]))

        # Number of overlapping intersections
        overlapping = str(intersections.count(True))
        # Remove all overlapping lines and duplicate intersections
        intersections = set([x for x in intersections if type(x) != bool])

        # Set up background for patterns
        self.pattern.create_image(0, 0, image=self.pattern_bg, anchor='nw')
        # Draw lines on screen
        for line, color in zip(lines, self.colors):
            self.pattern.create_line(*line, width=10, fill=color,
                                     activefill="blue", activedash=(4, 4, 4, 4),
                                     activewidth=8, arrow=tk.LAST,
                                     arrowshape=(15, 25, 15))
        # Draw intersecting points
        [self.pattern.create_oval(x - 7, y + 7, x + 7, y - 7, fill="yellow",
                                  width=3) for x, y in intersections]

        if self.sleep_ms < 16:
            # short sleep_ms -> incorrect values -> get defaults
            frame_rate = self.average[self.sleep_ms]
        else:
            frame_rate = round(1 / (self.sleep_ms / 1000), 3)
        time_left = round(patterns_left / frame_rate, 1)

        if self.show_real_fps:
            try:
                frame_rate = round(1 / (time.time() - self.timer), 3)
            except ZeroDivisionError:
                pass
            # Stop time measure
            self.timer = time.time()

        if frame_rate > 400:
            frame_rate = "..."
        if self.show_saved_pattern:
            self.paused = True
            self.sleep_ms = 100
            frame_rate = "..."
            time_left = "..."

        # Apply new highest frame rate
        if isinstance(frame_rate, float):
            if frame_rate > self.highest_fps:
                self.highest_fps = frame_rate
                Settings.run_query(frame_rate, table="set_highest")

        # Collect all calculated data
        info_text = ["Total number of patterns:", " ", "Patterns shown:",
                     "Patterns left to show:", " ", "Current pattern:",
                     "Current pattern length:",
                     "Current pattern intersections:",
                     "Current pattern overlapping patterns:", " ",
                     "Frames per seconds:", "Time until finish (seconds):"]
        info_data = [str(info) for info in (
        self.total_patterns, " ", self.patterns_shown, patterns_left, " ",
        "-".join(self.current_path), len(self.current_path), len(intersections),
        overlapping, " ", frame_rate, time_left)]

        # Applying data to information canvas
        for line, info1, info2, space in zip(range(12), info_text, info_data,
                                             range(30, 500, 30)):
            self.information.create_text(25, space, text=info1, anchor=tk.W,
                font=('Verdana', '11'))
            self.information.create_text(360, space, text=info2,
                font=('Verdana', '11'))
            if line in (1, 4, 9):
                self.information.create_line(25, space, 420, space,
                    fill="light gray", width=3)

        # Enable user to save current pattern only if paused
        if self.paused:
            existing = [x[0] for x in Settings.run_query(receive=True)[2]]
            if "".join(self.current_path) in existing:
                self.save_button.configure(state=tk.DISABLED, relief=tk.SUNKEN)
            else:
                self.save_button.configure(state=tk.NORMAL, relief=tk.RAISED)
            self.information.create_window(225, 410, window=self.save_button)

        # Recursively update the screen, but
        # is more inaccurate with shorter sleep_ms
        self.screen_updater()

    def screen_updater(self):
        """This method changes frames by given frame rate."""
        if not self.paused:
            self.after(self.sleep_ms, self.animation)
        else:
            # Recursively sleep until user un-pauses the animation
            self.after(1, self.screen_updater)


if __name__ == '__main__':

    pattern_background = "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"

    if not os.path.isfile("user_settings.db"):
        Settings.run_query(new_db=True)

    program = PatternsUI()
    program.mainloop()
