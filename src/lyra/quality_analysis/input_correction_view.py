import tkinter as tk


class InputCorrection(tk.Tk):
    """Container class for the input correction application."""
    def __init__(self, controller):
        super().__init__()
        container = tk.Frame(self)
        container.pack()
        self.geometry('%dx%d+%d+%d' % (600, 300, 300, 100))

        input_files_view = InputCorrectionFiles(container, controller)
        input_files_view.grid(row=0, column=0, sticky="nsew")
        input_files_view.tkraise()


class InputCorrectionFiles(tk.Frame):
    """Screen to input information about the program and input file."""
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)
        self.controller = controller
        self.container = container

        label_program = tk.Label(self, text="Program")
        label_program.grid(row=0, column=0, pady=6)
        self.container.entry_program = tk.Entry(self)
        self.container.entry_program.grid(row=0, column=1)
        self.container.entry_program.insert(0, "checker_example")

        label_input = tk.Label(self, text="Input File")
        label_input.grid(row=1, column=0, pady=6)
        self.container.entry_input = tk.Entry(self)
        self.container.entry_input.grid(row=1, column=1)
        self.container.entry_input.insert(0, "checker_example.in")

        run_button = tk.Button(self, text='Run', command=self.show_main_screen)
        run_button.grid(row=3, column=0, pady=10)

    def show_main_screen(self):
        """Shows the main screen of the application."""
        program_name = self.container.entry_program.get()
        input_file = self.container.entry_input.get()
        main_page = InputCorrectionMain(self.container, self.controller, program_name, input_file)
        main_page.grid(row=0, column=0, sticky="nsew")
        main_page.tkraise()


class InputCorrectionMain(tk.Frame):
    """Main screen of the input correction application. Starts the analysis automaticalliy
    when initialized."""
    def __init__(self, parent, controller, program_name, input_filename):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        self.program_name = program_name
        self.input_filename = input_filename
        self.errors = []
        self.error_index = 0

        self.container = parent

        border_error = tk.Label(self, width=65, borderwidth=2, relief="solid")
        border_error.grid(row=0, column=0, columnspan=10, ipady=15, pady=10, ipadx=30, sticky=tk.W)

        self.label_error = tk.Label(self, text="ERROR", width=70, anchor=tk.W)
        self.label_error.grid(row=0, column=0, columnspan=10)

        self.label_progress = tk.Label(self, text="PROGRESS", borderwidth=2, relief="raised")
        self.label_progress.grid(row=0, column=9, pady=10, ipady=3, ipadx=3)

        border_old_val = tk.Label(self, width=20, height=6, borderwidth=2, relief="solid")
        border_old_val.grid(row=1, column=1, columnspan=2, rowspan=2)

        label_old_val = tk.Label(self, text="Old value:")
        label_old_val.grid(row=1, column=1, columnspan=2)
        self.old_val = tk.Label(self, text="")
        self.old_val.grid(row=2, column=1, columnspan=2, ipady=10)

        border_new_val = tk.Label(self, width=35, height=6, borderwidth=2, relief="solid")
        border_new_val.grid(row=1, column=4, columnspan=4, rowspan=2, padx=3, pady=8, sticky=tk.W)

        label_new_val = tk.Label(self, text="New value:")
        label_new_val.grid(row=1, column=4, columnspan=4)
        self.new_val_var = tk.StringVar()
        self.entry_new_val = tk.Entry(self, textvariable=self.new_val_var)
        self.entry_new_val.grid(row=2, column=4, columnspan=4, padx=5)
        self.entry_new_val.bind("<KeyRelease>", self.check_new_val)
        error_image = tk.PhotoImage(file="icons/error.png")
        self.label_new_val_ok = tk.Label(self, image=error_image)
        self.label_new_val_ok.image = error_image
        self.label_new_val_ok.grid(row=2, column=7)

        prev_image = tk.PhotoImage(file="icons/prev.png")
        prev_button = tk.Button(self, image=prev_image, command=self.show_prev_error)
        prev_button.image = prev_image
        prev_button.grid(row=3, column=5, sticky=tk.E)

        next_image = tk.PhotoImage(file="icons/next.png")
        next_button = tk.Button(self, image=next_image, command=self.show_next_error)
        next_button.image = next_image
        next_button.grid(row=3, column=6, sticky=tk.W, padx=20)

        run_button = tk.Button(self, text="Check", command=self.check_corrected_input, anchor=tk.W)
        run_button.grid(row=4, column=0, pady=10)

        self.start_analysis()

    def show_prev_error(self):
        """Show the previous error in the list."""
        if self.error_index > 0:
            self.error_index -= 1
            self.show_error()

    def show_next_error(self):
        """Show the next error in the list."""
        if self.error_index < len(self.errors) - 1:
            self.error_index += 1
            self.show_error()

    def show_error(self):
        """Show information about the current error."""
        if len(self.errors) > 0:
            error = self.errors[self.error_index]
            self.old_val.config(text=error.old_value)
            self.entry_new_val.delete(0, tk.END)
            self.entry_new_val.insert(0, error.new_value)
            self.label_error.config(text=error.error_message)
            self.label_progress.config(text=f"{self.error_index+1}/{len(self.errors)}")
            self.check_new_val(None)
        else:
            self.old_val.config(text="")
            self.entry_new_val.delete(0, tk.END)
            self.label_error.config(text="No errors were found.")
            self.label_progress.config(text="0/0")
            self.label_new_val_ok.config(text="")

    def check_new_val(self, _):
        """Check if the current new value given by the user fulfils the assumptions."""
        if len(self.errors) == 0:
            return
        new_val = self.entry_new_val.get()
        curr_error = self.errors[self.error_index]
        curr_error.new_value = new_val
        new_error = self.controller.check_new_val(curr_error)
        if new_error is None:
            error_image = tk.PhotoImage(file="icons/checkmark.png")
            self.label_new_val_ok.config(image=error_image)
            self.label_new_val_ok.image = error_image
        else:
            self.errors[self.error_index] = new_error
            self.label_error.config(text=new_error.error_message)
            error_image = tk.PhotoImage(file="icons/error.png")
            self.label_new_val_ok.config(image=error_image)
            self.label_new_val_ok.image = error_image

    def start_analysis(self):
        """Runs the assumption analysis and shows information about the first error."""
        self.errors = self.controller.start_analysis(self.program_name, self.input_filename)
        self.error_index = 0
        self.show_error()

    def check_corrected_input(self):
        """Writes the new values back to the input file and runs the input checker."""
        self.errors = self.controller.check_corrected_input(self.errors)
        self.error_index = 0
        self.show_error()
