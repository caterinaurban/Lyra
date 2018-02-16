import tkinter as tk

from copy import deepcopy

from lyra.quality_analysis.input_assmp_simplification import CheckerZeroIdentifier
from lyra.quality_analysis.input_checker import ErrorInformation, InputInfo, InputLocation


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

        self.error_frame = tk.Frame(self, width=700, height=100,
                                    highlightthickness=2, highlightbackground="Black")
        self.error_frame.grid(row=0, pady=10)
        self.error_frame.grid_propagate(0)
        values_frame = tk.Frame(self, width=700, height=310)
        values_frame.grid(row=1, column=0)
        values_frame.grid_propagate(0)
        self.old_val_frame = tk.Frame(values_frame, width=300, height=310,
                                      highlightthickness=2, highlightbackground="Black")
        self.old_val_frame.grid(row=0, column=0)
        self.old_val_frame.grid_propagate(0)
        values_new_frame = tk.Frame(values_frame, width=400, height=310)
        values_new_frame.grid(row=0, column=1)
        values_new_frame.grid_propagate(0)
        self.new_val_frame1 = tk.Frame(values_new_frame, width=390, height=150,
                                       highlightthickness=2, highlightbackground="Black")
        self.new_val_frame1.grid(row=0, column=0, padx=(10, 0))
        self.new_val_frame1.grid_propagate(0)
        self.new_val_frame2 = tk.Frame(values_new_frame, width=390, height=150,
                                       highlightthickness=2, highlightbackground="Black")
        self.new_val_frame2.grid(row=1, column=0, padx=(10, 0), pady=(10, 0))
        self.new_val_frame2.grid_propagate(0)

        self.error_frame.grid_rowconfigure(0, weight=1)
        self.error_frame.grid_columnconfigure(0, weight=1)
        self.error_frame.grid_rowconfigure(3, weight=1)
        self.error_frame.grid_columnconfigure(1, weight=1)

        self.old_val_frame.grid_rowconfigure(0, weight=1)
        self.old_val_frame.grid_columnconfigure(0, weight=1)
        self.old_val_frame.grid_rowconfigure(8, weight=1)
        self.old_val_frame.grid_columnconfigure(3, weight=2)

        self.new_val_frame1.grid_rowconfigure(0, weight=1)
        self.new_val_frame1.grid_columnconfigure(0, weight=1)
        self.new_val_frame1.grid_rowconfigure(2, weight=1)
        self.new_val_frame1.grid_columnconfigure(2, weight=1)

        self.new_val_frame2.grid_rowconfigure(0, weight=1)
        self.new_val_frame2.grid_columnconfigure(0, weight=1)
        self.new_val_frame2.grid_rowconfigure(2, weight=1)
        self.new_val_frame2.grid_columnconfigure(2, weight=1)

        self.label_error = tk.Label(self.error_frame, justify=tk.LEFT)
        self.label_error.grid(row=1, column=0, padx=40, sticky=tk.W)

        self.label_progress = tk.Label(self.error_frame, borderwidth=2, relief="raised")
        self.label_progress.grid(row=1, column=1, ipady=3, ipadx=3, padx=40, sticky=tk.E)

        label_old_val = tk.Label(self.old_val_frame, text="Old value:")
        label_old_val.grid(row=0, column=1)

        label_new_val = tk.Label(self.new_val_frame1, text="New value:")
        label_new_val.grid(row=0, column=0)
        self.new_val_var = tk.StringVar()
        self.entry_new_val = tk.Entry(self.new_val_frame1, textvariable=self.new_val_var)
        self.entry_new_val.grid(row=1, column=0)
        self.entry_new_val.bind("<Return>", self.check_new_val)

        self.label_assmp_val = tk.Label(self.new_val_frame1, text="")
        self.label_assmp_val.grid(row=1, column=1)
        self.val1_widgets = [label_old_val]
        self.val1_widgets += [label_new_val, self.entry_new_val, self.label_assmp_val]

        self.label_old_line_before2 = None
        self.new_val_var2 = None
        self.entry_new_val2 = None
        self.label_assmp_val2 = None

        self.old_val_lines = []

        self.start_analysis()

    def show_relation_error_widgets(self):
        """Adds the widgets used for displaying a relational error"""
        label_new_val2 = tk.Label(self.new_val_frame2, text="New value:")
        label_new_val2.grid(row=0, column=0)
        self.new_val_var2 = tk.StringVar()
        self.entry_new_val2 = tk.Entry(self.new_val_frame2, textvariable=self.new_val_var2)
        self.entry_new_val2.grid(row=1, column=0)
        self.entry_new_val2.bind("<Return>", self.check_new_val)

        self.label_assmp_val2 = tk.Label(self.new_val_frame2, text="")
        self.label_assmp_val2.grid(row=1, column=1)

        self.relation_widgets = [label_new_val2, self.entry_new_val2, self.label_assmp_val2]

    def show_error(self):
        """Show information about the current error."""
        if len(self.errors) > 0:
            error = self.errors[self.error_index]
            self.update_error_info(error)
            if error.relation is not None:
                self.update_old_val_lines()
                self.update_relational_error_info(error)
            else:
                self.update_old_val_lines()
                for widget in self.relation_widgets:
                    widget.grid_forget()
                self.entry_new_val.config(state="normal")
                self.entry_new_val.focus()
        else:
            for widget in self.relation_widgets:
                widget.grid_forget()
            for widget in self.val1_widgets:
                widget.grid_forget()
            for widget in self.old_val_lines:
                widget.grid_forget()
            self.label_error.config(text="No errors were found.")
            self.label_progress.config(text="0/0")

    def update_old_val_lines(self):
        """Updates the display of the old values."""
        for widget in self.old_val_lines:
            widget.grid_forget()
        self.old_val_lines = []
        error = self.errors[self.error_index]
        if error.relation is None:
            location_before = deepcopy(error.infos1.location).sub_lines(1)
            location_after = deepcopy(error.infos1.location).add_lines(1)
            self.create_old_val_line(1, location_before, error.infos1.prev_line)
            self.create_old_val_line(2, error.infos1.location, error.infos1.value)
            self.create_old_val_line(3, location_after, error.infos1.next_line)
            return

        if error.infos1.location.user_line < error.infos2.location.user_line:
            val_min = error.infos1
            val_max = error.infos2
        else:
            val_min = error.infos2
            val_max = error.infos1

        max_line = self.calculate_max_location(val_min, val_max)

        for i in range(max_line+2):
            if i == 0:
                location_before1 = deepcopy(val_min.location).sub_lines(1)
                curr_val = (location_before1, val_min.prev_line)
            elif i == 1:
                curr_val = (val_min.location, val_min.value)
            elif i == max_line:
                curr_val = (val_max.location, val_max.value)
            elif i == max_line - 1:
                location_before2 = deepcopy(val_max.location).sub_lines(1)
                curr_val = (location_before2, val_max.prev_line)
            elif i == max_line + 1:
                location_after2 = deepcopy(val_max.location).add_lines(1)
                curr_val = (location_after2, val_max.next_line)
            elif i == 2:
                location_after1 = deepcopy(val_min.location).add_lines(1)
                curr_val = (location_after1, val_min.next_line)
            else:
                continue
            self.create_old_val_line(i+1, curr_val[0], curr_val[1])
        if max_line == 5:
            label_empty_line = tk.Label(self.old_val_frame, text="...")
            label_empty_line.grid(row=4, column=0)
            label_empty_old_val = tk.Label(self.old_val_frame, text="")
            label_empty_old_val.grid(row=4, column=1)
            self.old_val_lines += [label_empty_line, label_empty_old_val]
        if self.entry_new_val2 is not None:
            self.entry_new_val2.grid_forget()
            self.entry_new_val2.grid(row=max_line, column=4)

    def calculate_max_location(self, val_min: InputInfo, val_max: InputInfo):
        """Calculates the row number of the second value depending on how far away the values
        are in the input file.

        :param val_min: information about the first value
        :param val_max: information about the second value
        """
        line_min = val_min.location.file_line
        line_max = val_max.location.file_line
        old_val_line_max = 5
        diff_min_max = line_max - line_min
        if diff_min_max < 5:
            old_val_line_max = diff_min_max + 1
        return old_val_line_max

    def create_old_val_line(self, row: int, location: InputLocation, value: str):
        """Creates a label for the line number and the corresponding value.

        :param row: row number in which the label should be displayed
        :param location: location of the input value
        :param value: input value
        """
        label_line = tk.Label(self.old_val_frame, text=f"{location}")
        label_line.grid(row=row, column=0)
        if value is None:
            value = ""
        label_old_val = tk.Label(self.old_val_frame, text=f"{value}")
        label_old_val.grid(row=row, column=2, sticky=tk.E)
        self.old_val_lines += [label_line, label_old_val]

    def update_error_info(self, error: ErrorInformation):
        """Updates information about the current error

        :param error: current error to display
        """
        self.entry_new_val.delete(0, tk.END)
        self.entry_new_val.insert(0, error.infos1.value)
        self.label_assmp_val.config(text=error.create_info_msg(True))
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

            self.label_assmp_val2.config(text=error.create_info_msg(False))

            self.entry_new_val2.delete(0, tk.END)
            self.entry_new_val2.insert(0, error.infos2.value)
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
        curr_error.infos1.value = new_val
        rel_val = None
        if curr_error.relation is not None:
            if not isinstance(curr_error.relation.other_id, CheckerZeroIdentifier):
                rel_val = self.entry_new_val2.get()
                curr_error.infos2.value = rel_val
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
                old_error.infos1.value = new_val
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
        self.errors[self.error_index].infos1.value = new_val
        if self.errors[self.error_index].infos2 is not None:
            self.errors[self.error_index].infos2.value = rel_val
        self.errors = self.controller.check_corrected_input(self.errors[self.error_index])
        self.error_index = 0
        self.show_error()

    def keep_old_value(self):
        """Shows the values that were entered before."""
        self.entry_new_val.delete(0, tk.END)
        self.entry_new_val.insert(0, self.errors[self.error_index].infos1.value)
        self.entry_new_val2.delete(0, tk.END)
        self.entry_new_val2.insert(0, self.errors[self.error_index].info2.value)

    def start_analysis(self):
        """Runs the assumption analysis and shows information about the first error."""
        self.errors = self.controller.start_analysis(self.program_name, self.input_filename)
        self.error_index = 0
        self.show_error()
