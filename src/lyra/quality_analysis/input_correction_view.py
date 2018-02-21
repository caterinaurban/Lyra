import tkinter as tk

from copy import deepcopy

import re

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

        self.label_error = tk.Text(self.error_frame, height=3, width=70, wrap="none")
        self.label_error.configure(bg=self.error_frame.cget('bg'), relief=tk.FLAT)
        self.label_error.tag_config("normal", font="TkDefaultFont")
        self.label_error.tag_config("line1", font="TkDefaultFont", foreground="blue")
        self.label_error.tag_config("line2", font="TkDefaultFont", foreground="dodger blue")
        self.label_error.grid(row=1, column=0, padx=40, sticky=tk.W)

        self.label_progress = tk.Label(self.error_frame, borderwidth=2, relief="raised")
        self.label_progress.grid(row=1, column=1, ipady=3, ipadx=3, padx=40, sticky=tk.E)

        label_old = tk.Label(self.old_val_frame, text="Old value:")
        label_old.grid(row=0, column=1)

        self.label_new_val = tk.Text(self.new_val_frame1, height=1, width=30, wrap="none")
        self.label_new_val.configure(bg=self.new_val_frame1.cget('bg'), relief=tk.FLAT)
        self.label_new_val.tag_config("normal", font="TkDefaultFont")
        self.label_new_val.tag_config("line", font="TkDefaultFont", foreground="blue")
        self.label_new_val.grid(row=0, column=0)

        on_validate = (self.register(self.validate), '%d', '%P', '%W')
        self.new_val_var = tk.StringVar()
        self.entry_new_val = tk.Entry(self.new_val_frame1, textvariable=self.new_val_var,
                                      validate="key", validatecommand=on_validate)
        self.entry_new_val.grid(row=1, column=0)
        self.entry_new_val.bind("<Return>", self.check_new_val)

        self.label_assmp = tk.Label(self.new_val_frame1, text="")
        self.label_assmp.grid(row=1, column=1)
        self.val1_widgets = [label_old, self.label_new_val, self.entry_new_val, self.label_assmp]

        self.entry_new_val2 = None
        self.label_assmp2 = None
        self.label_new_val2 = None

        self.old_val_lines = []

        self.start_analysis()

    def validate(self, action: str, new_value: str, widget_name: str):
        """Checks if a new value is of the correct type

        :param action: "1" is insert, "0" is delete
        :param new_value: new value to check
        :param widget_name: name of the widget whose content is evaluated
        :return: If the new value has the correct type
        """
        if widget_name == f"{self.entry_new_val}":
            input_info = self.errors[self.error_index].infos1
        else:
            input_info = self.errors[self.error_index].infos2
        return action != "1" or input_info.check_type(new_value)

    def show_relation_error_widgets(self):
        """Adds the widgets used for displaying a relational error"""

        self.label_new_val2 = tk.Text(self.new_val_frame2, height=1, width=30, wrap="none")
        self.label_new_val2.configure(bg=self.new_val_frame1.cget('bg'), relief=tk.FLAT)
        self.label_new_val2.tag_config("normal", font="TkDefaultFont")
        self.label_new_val2.tag_config("line", font="TkDefaultFont", foreground="dodger blue")
        self.label_new_val2.grid(row=0, column=0)

        on_validate = (self.register(self.validate), '%d', '%P', '%W')
        new_val_var2 = tk.StringVar()
        self.entry_new_val2 = tk.Entry(self.new_val_frame2, textvariable=new_val_var2,
                                      validate="key", validatecommand=on_validate)
        self.entry_new_val2.grid(row=1, column=0)
        self.entry_new_val2.bind("<Return>", self.check_new_val)

        self.label_assmp2 = tk.Label(self.new_val_frame2, text="")
        self.label_assmp2.grid(row=1, column=1)

        self.relation_widgets = [self.label_new_val2, self.entry_new_val2, self.label_assmp2]

    def show_error(self):
        """Show information about the current error."""
        if len(self.errors) > 0 and isinstance(self.errors[0], ErrorInformation):
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
            self.old_val_frame.grid_forget()
            self.new_val_frame1.grid_forget()
            self.new_val_frame2.grid_forget()
            self.label_progress.grid_forget()
            self.label_error.config(state="normal", height=20, width=100)
            self.label_error.delete(1.0, tk.END)
            output = self.errors[0] if len(self.errors) > 0 else ""
            self.label_error.insert(tk.END, f"Output of the program:\n\n{output}", "normal")
            self.label_error.config(state="disabled")
            self.error_frame.configure(height=400)
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
            self.create_old_val_line(1, location_before, error.infos1.prev_line, False)
            self.create_old_val_line(2, error.infos1.location, error.infos1.orig_value, True)
            self.create_old_val_line(3, location_after, error.infos1.next_line, False)
            return

        val_min = error.infos1
        val_max = error.infos2

        max_line = self.calculate_max_location(val_min, val_max)

        for i in range(max_line+2):
            if i == 0:
                location_before1 = deepcopy(val_min.location).sub_lines(1)
                curr_val = (location_before1, val_min.prev_line)
            elif i == 1:
                curr_val = (val_min.location, val_min.orig_value)
            elif i == max_line:
                curr_val = (val_max.location, val_max.orig_value)
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
            self.create_old_val_line(i+1, curr_val[0], curr_val[1], i == max_line)
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

    def create_old_val_line(self, row: int, location: InputLocation, value: str, is_other: bool):
        """Creates a label for the line number and the corresponding value.

        :param row: row number in which the label should be displayed
        :param location: location of the input value
        :param value: input value
        :param is_other: if this label is for the second value
        """
        label_line = tk.Label(self.old_val_frame, text=f"{location}")
        if row == 2:
            label_line.config(fg="blue")
        elif is_other:
            label_line.config(fg="dodger blue")
        else:
            label_line.config(fg="grey")
        label_line.grid(row=row, column=0)

        if value is None:
            value = ""
        label_old_val = tk.Label(self.old_val_frame, text=f"{value}")
        if row == 2:
            label_old_val.config(fg="blue")
        elif is_other:
            label_old_val.config(fg="dodger blue")
        else:
            label_old_val.config(fg="grey")
        label_old_val.grid(row=row, column=2, sticky=tk.E)
        self.old_val_lines += [label_line, label_old_val]

    def update_error_info(self, error: ErrorInformation):
        """Updates information about the current error

        :param error: current error to display
        """
        self.label_new_val.config(state="normal")
        self.label_new_val.delete("1.0", tk.END)
        self.label_new_val.insert(tk.INSERT, "New value (", "normal")
        self.label_new_val.insert(tk.INSERT, f"{error.infos1.location}", "line")
        self.label_new_val.insert(tk.INSERT, "):", "normal")
        self.label_new_val.config(state="disabled")

        self.entry_new_val.delete(0, tk.END)
        if error.error_level != ErrorInformation.ErrorLevel.Type:
            self.entry_new_val.insert(0, error.infos1.orig_value)
        self.label_assmp.config(text=error.create_info_msg(True))

        self.label_error.config(state="normal")
        self.label_error.delete("1.0", tk.END)
        self.label_error.insert(tk.END, error.error_message, "normal")
        self.color_locations(error.error_message)
        self.label_error.config(state="disabled")
        self.label_progress.config(text=f"{self.error_index+1}/{len(self.errors)}")

    def color_locations(self, text: str):
        """Adds colors to the input line references in the text of the error message

        :param text: error message text
        """
        chars_first_line = re.search("^.*?\\n", text)
        num_chars_first_line = chars_first_line.end() if chars_first_line is not None else 0
        iters = re.finditer("Line \d+", text)
        lines = [(m.group(), m.span()) for m in iters]
        if len(lines) == 2:
            num_val1 = int(re.search("\d+", lines[0][0]).group())
            num_val2 = int(re.search("\d+", lines[1][0]).group())
            val1 = lines[0][1] if num_val1 < num_val2 else lines[1][1]
            val2 = lines[1][1] if num_val1 < num_val2 else lines[0][1]
            val1 = (val1[0]-num_chars_first_line, val1[1]-num_chars_first_line)
            val2 = (val2[0]-num_chars_first_line, val2[1]-num_chars_first_line)
            self.label_error.tag_add("line1", f"2.{val1[0]}", f"2.{val1[1]}")
            self.label_error.tag_add("line2", f"2.{val2[0]}", f"2.{val2[1]}")
        elif len(lines) == 1:
            val = lines[0][1]
            self.label_error.tag_add("line1", f"1.{val[0]}", f"1.{val[1]}")
        else:
            raise Exception(f"An error message can only mention one or two line numbers: {text}")

    def update_relational_error_info(self, error: ErrorInformation):
        """Updates information about the current relational error

        :param error: current relational error to display
        """
        for widget in self.relation_widgets:
            widget.grid_forget()
        if not isinstance(error.relation.other_id, CheckerZeroIdentifier):
            self.show_relation_error_widgets()

            self.label_assmp2.config(text=error.create_info_msg(False))

            self.label_new_val2.config(state="normal")
            self.label_new_val2.delete("1.0", tk.END)
            self.label_new_val2.insert(tk.INSERT, "New value (", "normal")
            self.label_new_val2.insert(tk.INSERT, f"{error.infos2.location}", "line")
            self.label_new_val2.insert(tk.INSERT, "):", "normal")
            self.label_new_val2.config(state="disabled")

            self.entry_new_val2.delete(0, tk.END)
            if error.error_level != ErrorInformation.ErrorLevel.Type:
                self.entry_new_val2.insert(0, error.infos2.orig_value)
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
        curr_error.infos1.change_orig_value(new_val)
        rel_val = None
        if curr_error.relation is not None:
            if not isinstance(curr_error.relation.other_id, CheckerZeroIdentifier):
                rel_val = self.entry_new_val2.get()
                curr_error.infos2.change_orig_value(rel_val)
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
                old_error.infos1.change_orig_value(new_val)
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
        self.errors[self.error_index].infos1.change_orig_value(new_val)
        if self.errors[self.error_index].infos2 is not None:
            self.errors[self.error_index].infos2.change_orig_value(rel_val)
        self.errors = self.controller.check_corrected_input(self.errors[self.error_index])
        self.error_index = 0
        self.show_error()

    def keep_old_value(self):
        """Shows the values that were entered before."""
        self.entry_new_val.delete(0, tk.END)
        self.entry_new_val.insert(0, self.errors[self.error_index].infos1.orig_value)
        if self.entry_new_val2 is not None:
            self.entry_new_val2.delete(0, tk.END)
            self.entry_new_val2.insert(0, self.errors[self.error_index].info2.orig_value)

    def start_analysis(self):
        """Runs the assumption analysis and shows information about the first error."""
        self.errors = self.controller.start_analysis(self.program_name, self.input_filename)
        self.error_index = 0
        self.show_error()
