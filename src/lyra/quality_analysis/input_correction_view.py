import subprocess
import tkinter as tk

from copy import deepcopy

import re
from tkinter import messagebox

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
        values_frame = tk.Frame(self, width=700, height=800)
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

        error_icon = tk.PhotoImage(file="icons/error.png")
        self.error_icon = tk.Label(self.error_frame, image=error_icon)
        self.error_icon.photo = error_icon
        self.error_icon.grid(row=1, column=0, sticky=tk.W, padx=10)

        self.label_error = tk.Text(self.error_frame, height=3, width=70, wrap="none")
        self.label_error.configure(bg=self.error_frame.cget('bg'), relief=tk.FLAT)
        self.label_error.tag_config("normal", font="TkDefaultFont")
        self.label_error.tag_config("color_red", font="TkDefaultFont", foreground="red")
        self.label_error.tag_config("color_blue", font="TkDefaultFont", foreground="blue")
        self.label_error.grid(row=1, column=0, padx=40, sticky=tk.W)

        self.label_progress = tk.Label(self.error_frame, borderwidth=2, relief="raised")
        self.label_progress.grid(row=1, column=1, ipady=3, ipadx=3, padx=40, sticky=tk.E)

        label_old = tk.Label(self.old_val_frame, text="Old value:")
        label_old.grid(row=0, column=1)

        self.label_new_val = tk.Text(self.new_val_frame1, height=1, width=30, wrap="none")
        self.label_new_val.configure(bg=self.new_val_frame1.cget('bg'), relief=tk.FLAT)
        self.label_new_val.tag_config("normal", font="TkDefaultFont")
        self.label_new_val.tag_config("color_blue", font="TkDefaultFont", foreground="blue")
        self.label_new_val.tag_config("color_red", font="TkDefaultFont", foreground="red")
        self.label_new_val.grid(row=0, column=0, sticky=tk.W, padx=(26, 0))

        on_validate = (self.register(self.validate), '%d', '%P', '%W')
        self.new_val_var = tk.StringVar()
        self.entry_new_val = tk.Entry(self.new_val_frame1, textvariable=self.new_val_var,
                                      validate="key", validatecommand=on_validate)
        self.entry_new_val.grid(row=1, column=0, sticky=tk.W, padx=(30, 0))
        self.entry_new_val.bind("<Return>", self.check_new_val)

        self.label_assmp = tk.Label(self.new_val_frame1, text="")
        self.label_assmp.grid(row=1, column=1, sticky=tk.W)

        show_input_button = tk.Button(values_frame, text="Open input file",
                                      command=self.open_input_file)
        show_input_button.grid(row=2, column=0, sticky=tk.W, pady=20)

        self.new_val_var2 = None
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
        if not isinstance(self.errors[self.error_index], ErrorInformation):
            return True
        if widget_name == f"{self.entry_new_val}":
            input_info = self.errors[self.error_index].infos1
        else:
            input_info = self.errors[self.error_index].infos2
        return action != "1" or input_info.check_type(new_value)

    def show_relation_error_widgets(self):
        """Adds the widgets used for displaying a relational error"""

        self.label_new_val2 = tk.Text(self.new_val_frame2, height=1, width=30, wrap="none")
        self.label_new_val2.configure(bg=self.new_val_frame2.cget('bg'), relief=tk.FLAT)
        self.label_new_val2.tag_config("normal", font="TkDefaultFont")
        self.label_new_val2.tag_config("color_blue", font="TkDefaultFont", foreground="blue")
        self.label_new_val2.tag_config("color_red", font="TkDefaultFont", foreground="red")
        self.label_new_val2.grid(row=0, column=0, sticky=tk.W, padx=(26, 0))

        on_validate = (self.register(self.validate), '%d', '%P', '%W')
        self.new_val_var2 = tk.StringVar()
        self.entry_new_val2 = tk.Entry(self.new_val_frame2, textvariable=self.new_val_var2,
                                       validate="key", validatecommand=on_validate)
        self.entry_new_val2.grid(row=1, column=0, sticky=tk.W, padx=(30, 0))
        self.entry_new_val2.bind("<Return>", self.check_new_val)

        self.label_assmp2 = tk.Label(self.new_val_frame2, text="")
        self.label_assmp2.grid(row=1, column=1, sticky=tk.W)

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
            self.error_icon.grid_forget()
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
        location_label = f"{location}" if location.user_line != 0 else ""
        label_line = tk.Label(self.old_val_frame, text=location_label)
        label_line.grid(row=row, column=0)
        value = "" if value is None else value
        label_old_val = tk.Label(self.old_val_frame, text=f"{value}")
        label_old_val.grid(row=row, column=2, sticky=tk.E)
        self.old_val_lines += [label_line, label_old_val]

        first_is_error = self.errors[self.error_index].is_first_val
        if row == 2:
            color = "red" if first_is_error else "blue"
            label_line.config(fg=color)
            label_old_val.config(fg=color)
        elif is_other:
            color = "blue" if first_is_error else "red"
            label_line.config(fg=color)
            label_old_val.config(fg=color)
        else:
            label_line.config(fg="grey")
            label_old_val.config(fg="grey")

    def update_error_info(self, error: ErrorInformation):
        """Updates information about the current error

        :param error: current error to display
        """
        self.label_new_val.config(state="normal")
        self.label_new_val.delete("1.0", tk.END)
        self.label_new_val.insert(tk.INSERT, "New value (", "normal")
        color_config = "color_red" if error.is_first_val else "color_blue"
        self.label_new_val.insert(tk.INSERT, f"{error.infos1.location}", color_config)
        self.label_new_val.insert(tk.INSERT, "):", "normal")
        self.label_new_val.config(state="disabled")

        self.new_val_var.set("")
        if error.error_level != ErrorInformation.ErrorLevel.Type:
            self.new_val_var.set(error.infos1.orig_value)
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
        found_line_words = re.finditer("Line \d+", text)
        lines = [(m.group(), m.span()) for m in found_line_words]
        if len(lines) == 2:
            line_rel1 = lines[0]
            line_rel2 = lines[1]
            line_number1 = int(re.search("\d+", line_rel1[0]).group())
            if self.errors[self.error_index].is_first_val:
                curr_error_loc = self.errors[self.error_index].infos1.location.file_line
            else:
                curr_error_loc = self.errors[self.error_index].infos2.location.file_line

            num_red = line_rel1[1] if curr_error_loc + 1 == line_number1 else line_rel2[1]
            num_blue = line_rel2[1] if curr_error_loc + 1 == line_number1 else line_rel1[1]

            num_red = (num_red[0]-num_chars_first_line, num_red[1]-num_chars_first_line)
            num_blue = (num_blue[0]-num_chars_first_line, num_blue[1]-num_chars_first_line)
            self.label_error.tag_add("color_red", f"2.{num_red[0]}", f"2.{num_red[1]}")
            self.label_error.tag_add("color_blue", f"2.{num_blue[0]}", f"2.{num_blue[1]}")
        elif len(lines) == 1:
            val = lines[0][1]
            self.label_error.tag_add("color_red", f"1.{val[0]}", f"1.{val[1]}")
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
            color_config = "color_red" if not error.is_first_val else "color_blue"
            self.label_new_val2.insert(tk.INSERT, f"{error.infos2.location}", color_config)
            self.label_new_val2.insert(tk.INSERT, "):", "normal")
            self.label_new_val2.config(state="disabled")

            if error.error_level != ErrorInformation.ErrorLevel.Type:
                self.new_val_var2.set(error.infos2.orig_value)
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
        if len(self.errors) == 0 or not isinstance(self.errors[0], ErrorInformation):
            return
        curr_error = deepcopy(self.errors[self.error_index])
        new_val = self.entry_new_val.get()
        curr_error.infos1.change_orig_value(new_val)
        rel_val = None
        if curr_error.relation is not None:
            if not isinstance(curr_error.relation.other_id, CheckerZeroIdentifier):
                rel_val = self.entry_new_val2.get()
                curr_error.infos2.change_orig_value(rel_val)
        old_error = self.errors[self.error_index]
        if not old_error.is_first_val:
            self.check_corrected_input(new_val, rel_val)
        else:
            new_error = self.controller.check_new_val(curr_error)
            if new_error is None:
                self.check_corrected_input(new_val, rel_val)
            elif old_error.relation is None:
                if new_error.error_level < self.errors[self.error_index].error_level:
                    self.keep_old_value()
                else:
                    self.errors[self.error_index] = new_error
                    self.show_error()
            elif new_error is not None and new_error.is_first_val:
                self.keep_old_value()
            elif isinstance(curr_error.relation.other_id, CheckerZeroIdentifier):
                self.check_corrected_input(new_val, rel_val)
                self.show_error()
            else:
                old_error.infos1.change_orig_value(new_val)
                old_error.is_first_val = False
                self.show_error()

    def check_corrected_input(self, new_val: str, rel_val: str):
        """Writes the new values to the file and checks the input

        :param new_val: new value of the current error
        :param rel_val: relational value of the current error
        """
        self.errors[self.error_index].infos1.change_orig_value(new_val)
        if self.errors[self.error_index].infos2 is not None:
            self.errors[self.error_index].infos2.change_orig_value(rel_val)
        new_errors = self.controller.check_corrected_input(self.errors[self.error_index])
        num_new_errors = len(new_errors) - len(self.errors) + 1
        if num_new_errors > 100:
            message = f"This value creates {num_new_errors} new errors.\n" \
                      f"Do you want to proceed?"
            proceed = messagebox.askokcancel("Python", message)
            if not proceed:
                return
        self.errors = new_errors
        self.error_index = 0
        self.new_val_var.set("")
        if self.new_val_var2 is not None:
            self.new_val_var2.set("")
        self.show_error()

    def keep_old_value(self):
        """Shows the values that were entered before."""
        self.new_val_var.set(self.errors[self.error_index].infos1.orig_value)
        if self.new_val_var2 is not None:
            self.new_val_var2.set(self.errors[self.error_index].info2.orig_value)

    def start_analysis(self):
        """Runs the assumption analysis and shows information about the first error."""
        self.errors = self.controller.start_analysis(self.program_name, self.input_filename)
        self.error_index = 0
        self.show_error()

    def open_input_file(self):
        """Opens an input file for editing and rechecks the assumptions when returning"""
        subprocess.call(f"kate example/{self.input_filename}", shell=True)
        self.errors = self.controller.run_checker()
        self.error_index = 0
        self.show_error()
