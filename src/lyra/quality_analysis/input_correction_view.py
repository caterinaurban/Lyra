import tkinter as tk


class InputCorrection(tk.Tk):

    def __init__(self, controller):
        super().__init__()
        container = tk.Frame(self)
        container.pack()
        self.geometry('%dx%d+%d+%d' % (600, 300, 300, 100))

        input_files_view = InputCorrectionFiles(container, controller)
        input_files_view.grid(row=0, column=0, sticky="nsew")
        input_files_view.tkraise()


class InputCorrectionFiles(tk.Frame):

    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)
        self.controller = controller
        self.container = container
        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=1)

        label_program = tk.Label(self, text="Program")
        label_program.grid(row=0, column=0)
        self.container.entry_program = tk.Entry(self)
        self.container.entry_program.grid(row=0, column=1)
        self.container.entry_program.insert(0, "checker_example")

        label_input = tk.Label(self, text="Input File")
        label_input.grid(row=1, column=0)
        self.container.entry_input = tk.Entry(self)
        self.container.entry_input.grid(row=1, column=1)
        self.container.entry_input.insert(0, "checker_example.in")

        run_button = tk.Button(self, text='Run', command=self.start_anaylis)
        run_button.grid(row=3, column=0)

    def start_anaylis(self):
        program_name = self.container.entry_program.get()
        input_file = self.container.entry_input.get()
        main_page = InputCorrectionMain(self.container, self.controller, program_name, input_file)
        main_page.grid(row=0, column=0, sticky="nsew")
        main_page.tkraise()


class InputCorrectionMain(tk.Frame):

    def __init__(self, parent, controller, program_name, input_filename):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        self.program_name = program_name
        self.input_filename = input_filename
        self.errors = []
        self.error_index = 0

        self.container = parent

        self.label_error = tk.Label(self, text="ERROR", width=80, anchor=tk.W)
        self.label_error.grid(row=0, column=0, columnspan=10, ipady=10, padx=10)

        label_old_val = tk.Label(self, text="Old value:")
        label_old_val.grid(row=1, column=1, columnspan=2)
        self.old_val = tk.Label(self, text="")
        self.old_val.grid(row=2, column=1, columnspan=2, ipady=10)

        label_new_val = tk.Label(self, text="New value:")
        label_new_val.grid(row=1, column=4, columnspan=4)
        self.new_val_var = tk.StringVar()
        self.entry_new_val = tk.Entry(self, textvariable=self.new_val_var)
        self.entry_new_val.grid(row=2, column=4, columnspan=4)
        self.entry_new_val.bind("<KeyRelease>", self.check_new_val)
        self.label_new_val_ok = tk.Label(self, text="BAD")
        self.label_new_val_ok.grid(row=2, column=7, columnspan=2)

        prev_image = tk.PhotoImage(file="icons/prev.png")
        prev_button = tk.Button(self, image=prev_image, command=self.show_prev_error)
        prev_button.image = prev_image
        prev_button.grid(row=3, column=5)

        next_image = tk.PhotoImage(file="icons/next.png")
        next_button = tk.Button(self, image=next_image, command=self.show_next_error)
        next_button.image = next_image
        next_button.grid(row=3, column=6)

        run_button = tk.Button(self, text='Run', command=self.start_anaylis, anchor=tk.W)
        run_button.grid(row=4, column=0, pady=10)

        self.start_anaylis()

    def show_prev_error(self):
        if self.error_index > 0:
            self.error_index -= 1
            self.show_error()

    def show_next_error(self):
        if self.error_index < len(self.errors) - 1:
            self.error_index += 1
            self.show_error()

    def show_error(self):
        error = self.errors[self.error_index]
        self.old_val.config(text=error.old_value)
        self.entry_new_val.delete(0, tk.END)
        self.entry_new_val.insert(0, error.new_value)
        self.label_error.config(text=error.error_message)

    def check_new_val(self):
        new_val = self.entry_new_val.get()
        self.errors[self.error_index].new_value = new_val
        assmp = self.errors[self.error_index].assumption
        location = self.errors[self.error_index].location
        has_error = self.controller.check_new_val(new_val, assmp, location)
        if has_error:
            self.label_new_val_ok.config(text="BAD")
        else:
            self.label_new_val_ok.config(text="GOOD")

    def start_anaylis(self):
        self.errors = self.controller.start_analysis(self.program_name, self.input_filename)
        self.error_index = 0
        self.show_error()
