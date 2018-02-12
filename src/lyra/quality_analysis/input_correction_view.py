import tkinter as tk

from copy import deepcopy

from lyra.quality_analysis.input_assmp_simplification import CheckerZeroIdentifier


class InputCorrection(tk.Tk):
    """Container class for the input correction application."""
    def __init__(self, controller):
        super().__init__()
        container = tk.Frame(self)
        container.pack()
        self.geometry('%dx%d+%d+%d' % (800, 500, 300, 100))

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

row_error = 0
row_label_val = 1
row_val = 2
row_label_val2 = 3
row_val2 = 4
row_prev_next = 5
row_check = 6
error_width = 80


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
        self.relation_widgets = []

        self.container = parent

        border_error = tk.Label(self, width=error_width+10, borderwidth=2, relief="solid")
        border_error.grid(row=row_error, column=0, columnspan=10, ipady=30, pady=10, ipadx=30)

        self.label_error = tk.Label(self, text="ERROR", width=error_width, anchor=tk.W)
        self.label_error.grid(row=row_error, column=0, columnspan=10)

        self.label_progress = tk.Label(self, text="PROGRESS", borderwidth=2, relief="raised")
        self.label_progress.grid(row=row_error, column=9, pady=10, ipady=3, ipadx=3)

        border_old_val = tk.Label(self, width=20, height=6, borderwidth=2, relief="solid")
        border_old_val.grid(row=row_label_val, column=1, columnspan=2, rowspan=2)

        label_old_val = tk.Label(self, text="Old value:")
        label_old_val.grid(row=row_label_val, column=1, columnspan=2)
        self.old_val = tk.Label(self, text="")
        self.old_val.grid(row=row_val, column=1, columnspan=2, ipady=10)

        border_new_val = tk.Label(self, width=35, height=6, borderwidth=2, relief="solid")
        border_new_val.grid(row=row_label_val, column=4, columnspan=4, rowspan=2, padx=3, pady=8)

        label_new_val = tk.Label(self, text="New value:")
        label_new_val.grid(row=row_label_val, column=4, columnspan=4)
        self.new_val_var = tk.StringVar()
        self.entry_new_val = tk.Entry(self, textvariable=self.new_val_var)
        self.entry_new_val.grid(row=row_val, column=4, columnspan=4, padx=5)
        self.entry_new_val.bind("<Return>", self.check_new_val)

        self.old_val2 = None
        self.new_val_var2 = None
        self.entry_new_val2 = None

        self.entry_locked = False

        self.start_analysis()

    def show_relation_error_widgets(self):
        """Adds the widgets used for displaying a relational error"""
        border_old_val2 = tk.Label(self, width=20, height=6, borderwidth=2, relief="solid")
        border_old_val2.grid(row=row_label_val2, column=1, columnspan=2, rowspan=2)

        label_old_val2 = tk.Label(self, text="Old value:")
        label_old_val2.grid(row=row_label_val2, column=1, columnspan=2)
        self.old_val2 = tk.Label(self, text="")
        self.old_val2.grid(row=row_val2, column=1, columnspan=2, ipady=10)

        border_new_val2 = tk.Label(self, width=35, height=6, borderwidth=2, relief="solid")
        border_new_val2.grid(row=row_label_val2, column=4, columnspan=4, rowspan=2, padx=3, pady=8)

        label_new_val2 = tk.Label(self, text="New value:")
        label_new_val2.grid(row=row_label_val2, column=4, columnspan=4)
        self.new_val_var2 = tk.StringVar()
        self.entry_new_val2 = tk.Entry(self, textvariable=self.new_val_var2)
        self.entry_new_val2.grid(row=row_val2, column=4, columnspan=4, padx=5)
        self.entry_new_val2.bind("<Return>", self.check_new_val)

        self.relation_widgets = [border_old_val2, label_old_val2, self.old_val2, border_new_val2]
        self.relation_widgets += [label_new_val2, self.entry_new_val2]

    def show_error(self):
        """Show information about the current error."""
        if len(self.errors) > 0:
            error = self.errors[self.error_index]
            self.old_val.config(text=error.value)
            self.entry_new_val.delete(0, tk.END)
            self.entry_new_val.insert(0, error.value)
            self.label_error.config(text=error.error_message)
            self.label_progress.config(text=f"{self.error_index+1}/{len(self.errors)}")
            if error.relation is not None:
                for widget in self.relation_widgets:
                    widget.grid_forget()
                if not isinstance(error.relation.other_id, CheckerZeroIdentifier):
                    self.show_relation_error_widgets()
                    self.old_val2.config(text=error.rel_val)
                    self.entry_new_val2.delete(0, tk.END)
                    self.entry_new_val2.insert(0, error.rel_val)
                    state = "normal" if error.is_first_val else "readonly"
                    self.entry_new_val.config(state=state)
                    state2 = "readonly" if error.is_first_val else "normal"
                    self.entry_new_val2.config(state=state2)
                else:
                    self.entry_new_val.config(state="normal")
            else:
                for widget in self.relation_widgets:
                    widget.grid_forget()
                self.entry_new_val.config(state="normal")
        else:
            self.old_val.config(text="")
            self.entry_new_val.delete(0, tk.END)
            if self.old_val2 is not None:
                self.old_val2.config(text="")
                self.entry_new_val2.delete(0, tk.END)
            self.label_error.config(text="No errors were found.")
            self.label_progress.config(text="0/0")

    def check_new_val(self, _):
        """Check if the current new value given by the user fulfils the assumptions."""
        if len(self.errors) == 0:
            return
        curr_error = deepcopy(self.errors[self.error_index])
        new_val = self.entry_new_val.get()
        curr_error.value = new_val
        rel_val = None
        if curr_error.relation is not None:
            if not isinstance(curr_error.relation.other_id, CheckerZeroIdentifier):
                rel_val = self.entry_new_val2.get()
                curr_error.rel_val = rel_val
        new_error = self.controller.check_new_val(curr_error)
        old_error = self.errors[self.error_index]

        if old_error.relation is None:
            if new_error is None:
                self.check_corrected_input(new_val, rel_val)
            elif new_error.error_level < self.errors[self.error_index].error_level:
                self.keep_old_value()
            else:
                self.errors[self.error_index] = new_error
                self.show_error()
        elif new_error is not None and new_error.is_first_val:
            self.keep_old_value()
        elif old_error.is_first_val:
            if isinstance(curr_error.relation.other_id, CheckerZeroIdentifier):
                self.check_corrected_input(new_val, rel_val)
                self.show_error()
            else:
                old_error.value = new_val
                old_error.is_first_val = False
                self.show_error()
        elif new_error is None:
            self.check_corrected_input(new_val, rel_val)
            self.show_error()
        elif new_error.is_first_val or new_error.error_level < old_error.error_level:
            self.keep_old_value()
        else:
            if isinstance(new_error.relation.other_id, CheckerZeroIdentifier):
                self.check_corrected_input(new_val, rel_val)
                self.show_error()
            else:
                self.errors[self.error_index] = new_error
                self.show_error()

    def check_corrected_input(self, new_val: str, rel_val: str):
        """Writes the new values to the file and checks the input

        :param new_val: new value of the current error
        :param rel_val: relational value of the current error
        """
        self.errors[self.error_index].value = new_val
        self.errors[self.error_index].rel_val = rel_val
        self.errors = self.controller.check_corrected_input(self.errors[self.error_index])
        self.error_index = 0
        self.show_error()

    def keep_old_value(self):
        """Shows the values that were entered before."""
        self.entry_new_val.delete(0, tk.END)
        self.entry_new_val.insert(0, self.errors[self.error_index].value)
        self.entry_new_val2.delete(0, tk.END)
        self.entry_new_val2.insert(0, self.errors[self.error_index].rel_val)

    def start_analysis(self):
        """Runs the assumption analysis and shows information about the first error."""
        self.errors = self.controller.start_analysis(self.program_name, self.input_filename)
        self.error_index = 0
        self.show_error()
