import tkinter as tk

from copy import deepcopy

from lyra.quality_analysis.input_assmp_simplification import CheckerZeroIdentifier
from lyra.quality_analysis.input_checker import ErrorInformation


class InputCorrection(tk.Tk):
    """Container class for the input correction application."""
    def __init__(self, controller):
        super().__init__()
        container = tk.Frame(self)
        container.pack()
        self.geometry('%dx%d+%d+%d' % (800, 600, 300, 100))

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
row_label_val = row_error + 1
row_val_before = row_label_val + 1
row_val = row_val_before + 1
row_val_after = row_val + 1
row_label_val2 = row_val_after + 2
row_val_before2 = row_label_val2 + 1
row_val2 = row_val_before2 + 1
row_val_after2 = row_val2 + 1
row_prev_next = row_val_after2 + 1
row_check = row_prev_next + 1
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
        border_error.grid(row=row_error, column=0, columnspan=10, ipady=40, pady=10, ipadx=30)

        self.label_error = tk.Label(self, text="ERROR", width=error_width, anchor=tk.W)
        self.label_error.grid(row=row_error, column=0, columnspan=10)

        self.label_progress = tk.Label(self, text="PROGRESS", borderwidth=2, relief="raised")
        self.label_progress.grid(row=row_error, column=9, pady=10, ipady=3, ipadx=3)

        border_old_val = tk.Label(self, width=20, borderwidth=2, relief="solid")
        border_old_val.grid(row=row_label_val, column=1, columnspan=2, rowspan=row_val_after, ipady=40)

        label_old_val = tk.Label(self, text="Old value:")
        label_old_val.grid(row=row_label_val, column=1, columnspan=2)

        self.label_old_line_before = tk.Label(self, text="Line:")
        self.label_old_line_before.grid(row=row_val_before, column=0)
        self.old_val_before = tk.Label(self, text="")
        self.old_val_before.grid(row=row_val_before, column=1, columnspan=2)

        self.label_old_line = tk.Label(self, text="Line:")
        self.label_old_line.grid(row=row_val, column=0)
        self.old_val = tk.Label(self, text="")
        self.old_val.grid(row=row_val, column=1, columnspan=2)

        self.label_old_line_after = tk.Label(self, text="Line:")
        self.label_old_line_after.grid(row=row_val_after, column=0)
        self.old_val_after = tk.Label(self, text="")
        self.old_val_after.grid(row=row_val_after, column=1, columnspan=2)

        label_empty = tk.Label(self, text=" ")
        label_empty.grid(row=row_val_after+1, column=1, columnspan=2)

        border_new_val = tk.Label(self, width=35, borderwidth=2, relief="solid")
        border_new_val.grid(row=row_label_val, column=4, columnspan=4, rowspan=row_val_after, ipady=40)

        label_new_val = tk.Label(self, text="New value:")
        label_new_val.grid(row=row_label_val, column=4, columnspan=4)
        self.new_val_var = tk.StringVar()
        self.entry_new_val = tk.Entry(self, textvariable=self.new_val_var)
        self.entry_new_val.grid(row=row_val, column=4, columnspan=4, padx=5)
        self.entry_new_val.bind("<Return>", self.check_new_val)

        self.val1_widgets = [border_old_val, label_old_val, self.old_val, border_new_val]
        self.val1_widgets += [label_new_val, self.entry_new_val]
        self.val1_widgets += [self.label_old_line_before, self.label_old_line]
        self.val1_widgets += [self.label_old_line_after, self.old_val_before, self.old_val_after]

        self.label_old_line_before2 = None
        self.old_val_before2 = None
        self.label_old_line2 = None
        self.old_val2 = None
        self.label_old_line_after2 = None
        self.old_val_after2 = None
        self.new_val_var2 = None
        self.entry_new_val2 = None

        self.entry_locked = False

        self.start_analysis()

    def show_relation_error_widgets(self):
        """Adds the widgets used for displaying a relational error"""
        border_old_val2 = tk.Label(self, width=20, borderwidth=2, relief="solid")
        border_old_val2.grid(row=row_label_val2, column=1, columnspan=2, rowspan=row_val_after, ipady=40)

        label_old_val2 = tk.Label(self, text="Old value:")
        label_old_val2.grid(row=row_label_val2, column=1, columnspan=2)

        self.label_old_line_before2 = tk.Label(self, text="Line:")
        self.label_old_line_before2.grid(row=row_val_before2, column=0)
        self.old_val_before2 = tk.Label(self, text="")
        self.old_val_before2.grid(row=row_val_before2, column=1, columnspan=2)

        self.label_old_line2 = tk.Label(self, text="Line:")
        self.label_old_line2.grid(row=row_val2, column=0)
        self.old_val2 = tk.Label(self, text="")
        self.old_val2.grid(row=row_val2, column=1, columnspan=2)

        self.label_old_line_after2 = tk.Label(self, text="Line:")
        self.label_old_line_after2.grid(row=row_val_after2, column=0)
        self.old_val_after2 = tk.Label(self, text="")
        self.old_val_after2.grid(row=row_val_after2, column=1, columnspan=2)

        border_new_val2 = tk.Label(self, width=35, borderwidth=2, relief="solid")
        border_new_val2.grid(row=row_label_val2, column=4, columnspan=4, rowspan=row_val_after, ipady=40)

        label_new_val2 = tk.Label(self, text="New value:")
        label_new_val2.grid(row=row_label_val2, column=4, columnspan=4)
        self.new_val_var2 = tk.StringVar()
        self.entry_new_val2 = tk.Entry(self, textvariable=self.new_val_var2)
        self.entry_new_val2.grid(row=row_val2, column=4, columnspan=4, padx=5)
        self.entry_new_val2.bind("<Return>", self.check_new_val)

        self.relation_widgets = [border_old_val2, label_old_val2, self.old_val2, border_new_val2]
        self.relation_widgets += [label_new_val2, self.entry_new_val2, self.old_val_after2]
        self.relation_widgets += [self.label_old_line_before2, self.label_old_line2]
        self.relation_widgets += [self.label_old_line_after2, self.old_val_before2]

    def show_error(self):
        """Show information about the current error."""
        if len(self.errors) > 0:
            error = self.errors[self.error_index]
            self.update_error_info(error)
            if error.relation is not None:
                self.update_relational_error_info(error)
            else:
                for widget in self.relation_widgets:
                    widget.grid_forget()
                self.entry_new_val.config(state="normal")
                self.entry_new_val.focus()
        else:
            for widget in self.relation_widgets:
                widget.grid_forget()
            for widget in self.val1_widgets:
                widget.grid_forget()
            self.label_error.config(text="No errors were found.")
            self.label_progress.config(text="0/0")

    def update_error_info(self, error: ErrorInformation):
        """Updates information about the current error

        :param error: current error to display
        """
        self.label_old_line_before.config(text=f"Line {error.location}:")
        self.old_val_before.config(text=error.prev_line)
        self.label_old_line.config(text=f"Line {error.location+1}:")
        self.old_val.config(text=error.value)
        self.label_old_line_after.config(text=f"Line {error.location+2}:")
        self.old_val_after.config(text=error.next_line)

        self.entry_new_val.delete(0, tk.END)
        self.entry_new_val.insert(0, error.value)
        self.label_error.config(text=error.error_message)
        self.label_progress.config(text=f"{self.error_index+1}/{len(self.errors)}")

    def update_relational_error_info(self, error: ErrorInformation):
        """Updates information about the current relational error

        :param error: current relational error to display
        """
        for widget in self.relation_widgets:
            widget.grid_forget()
        if not isinstance(error.relation.other_id, CheckerZeroIdentifier):
            self.show_relation_error_widgets()

            self.label_old_line_before2.config(text=f"Line {error.rel_location}:")
            self.old_val_before2.config(text=error.rel_prev_line)
            self.label_old_line2.config(text=f"Line {error.rel_location+1}:")
            self.old_val2.config(text=error.rel_val)
            self.label_old_line_after2.config(text=f"Line {error.rel_location+2}:")
            self.old_val_after2.config(text=error.rel_next_line)

            self.entry_new_val2.delete(0, tk.END)
            self.entry_new_val2.insert(0, error.rel_val)
            if error.is_first_val:
                state = "normal"
                state2 = "readonly"
                self.entry_new_val.focus()
            else:
                state = "readonly"
                state2 = "normal"
                self.entry_new_val2.focus()
            self.entry_new_val.config(state=state)
            self.entry_new_val2.config(state=state2)
        else:
            self.entry_new_val.focus()
            self.entry_new_val.config(state="normal")

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
