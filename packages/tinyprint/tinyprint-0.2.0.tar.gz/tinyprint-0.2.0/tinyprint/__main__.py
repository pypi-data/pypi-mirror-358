"""GUI for tinyprint"""

from dataclasses import dataclass
import os
import logging
from pathlib import Path
import tempfile
from typing import Optional

from tkinter import Tk
from tkinter import ttk
import tkinter as tk

from tkinter.filedialog import (
    askopenfilename,
    askopenfilenames,
    asksaveasfilename,
)

from tinyprint.jobconfig import JobConfig, Resource
from tinyprint.job import Job


def main():
    tempdir = tempfile.TemporaryDirectory(prefix="tinyprint")
    try:
        _main(tempdir.name)
    finally:
        tempdir.cleanup()


def _main(tempdir: str):
    root = Tk()
    root.title("~ tiny print ~")
    frm = ttk.Frame(root, padding=15)
    frm.grid()

    try:  # support macos
        _no_hidden_files(root)
    except Exception:
        pass

    jcm = JobConfigManager(
        JobConfigFields(frm), tempdir, filename_indicator=tk.StringVar(value="")
    )
    jm = JobManager(jcm)

    ymax = 8

    ttk.Button(frm, text="print", command=jm.print).grid(column=0, row=0)
    ttk.Button(frm, text="stop", command=jm.stop).grid(column=1, row=0)

    ttk.Separator(frm).grid(row=1, columnspan=ymax, sticky="ew", pady=10)

    ttk.Label(frm, text="job config: ").grid(column=0, row=2)
    ttk.Label(frm, textvariable=jcm.fields.filename).grid(
        column=1, row=2, columnspan=3, pady=5, sticky="w"
    )

    ttk.Button(frm, text="new", command=jcm.new).grid(column=0, row=3, pady=5, padx=2)
    ttk.Button(frm, text="open", command=jcm.open).grid(column=1, row=3, padx=2)
    ttk.Button(frm, text="save", command=jcm.save).grid(column=2, row=3, padx=2)
    ttk.Button(frm, text="save as ...", command=jcm.save_as).grid(
        column=3, row=3, padx=2
    )
    ttk.Button(frm, text="reload", command=jcm.load).grid(column=4, row=3, padx=2)

    ttk.Separator(frm).grid(row=4, columnspan=ymax, sticky="ew", pady=10)

    ttk.Label(frm, text="resource: ").grid(
        column=0, row=5, columnspan=2, sticky="w", pady=2
    )
    ttk.Button(frm, text="select", command=jcm.select_resource).grid(
        column=2, row=5, sticky="w"
    )
    ttk.Label(frm, textvariable=jcm.fields.resource_list).grid(
        column=4, row=5, columnspan=2, sticky="w"
    )

    ttk.Label(frm, text="printer configuration: ").grid(
        column=0, row=6, columnspan=2, sticky="w", pady=2
    )
    ttk.Button(frm, text="select", command=jcm.select_printer_configuration).grid(
        column=2, row=6, sticky="w"
    )
    ttk.Label(frm, textvariable=jcm.fields.printer_config).grid(
        column=4, row=6, sticky="w"
    )

    ttk.Label(frm, text="cut: ").grid(column=0, row=7, columnspan=2, sticky="w", pady=2)
    jcm.fields.cut.grid(column=2, row=7)
    jcm.fields.cut.bind("<<ComboboxSelected>>", jcm.select_cut)

    ttk.Label(frm, text="sleep time: ").grid(
        column=0, row=8, columnspan=2, sticky="w", pady=2
    )
    ttk.Label(frm, textvariable=jcm.fields.sleep_time).grid(column=2, row=8, sticky="w")
    ttk.Scale(frm, from_=0, to=2, command=jcm.select_sleep_time, length=500).grid(
        column=3, row=8, columnspan=2
    )

    root.mainloop()


# See https://stackoverflow.com/a/54068050
def _no_hidden_files(root):
    # call a dummy dialog with an impossible option to initialize the file
    # dialog without really getting a dialog window; this will throw a
    # TclError, so we need a try...except :
    try:
        root.tk.call("tk_getOpenFile", "-foobarbaz")
    except tk.TclError:
        pass
    # now set the magic variables accordingly
    root.tk.call("set", "::tk::dialog::file::showHiddenBtn", "1")
    root.tk.call("set", "::tk::dialog::file::showHiddenVar", "0")


class JobConfigFields:
    def __init__(self, frm):
        self.filename = tk.StringVar()
        self.resource_list = tk.StringVar()
        self.printer_config = tk.StringVar()
        self.cut = ttk.Combobox(frm, values=["yes", "no"])
        self.sleep_time = tk.DoubleVar()

    def update(self, job_config: JobConfig):
        resource_list = "; ".join(
            [r.path.split(os.sep)[-1] for r in job_config.resource_list]
        )
        if len(resource_list) > 25:
            resource_list = resource_list[:30] + " ..."
        self.resource_list.set(resource_list)
        self.printer_config.set(job_config.printer_config)
        self.cut.set(("no", "yes")[job_config.cut])
        self.sleep_time.set(job_config.sleep_time or 0)


@dataclass
class JobConfigManager:
    fields: JobConfigFields

    tempdir: str
    temp_resource: Optional[str] = None

    job_config: Optional[JobConfig] = None
    filename: Optional[str] = None
    filename_indicator: Optional[tk.StringVar] = None

    def __post_init__(self):
        self.temp_resource = f"{self.tempdir}/tmp-resource.md"
        with open(self.temp_resource, "w") as f:
            f.write("tiny printer test")
        self.new(f"{self.tempdir}/tmp-print-job.json")

    def new(self, *args, **kwargs):
        self.job_config = JobConfig([Resource(self.temp_resource)])
        self.save_as(*args, **kwargs)
        self.updatefields()

    def open(self):
        filetypes = (("print job configuration", "*.json"), ("All files", "*.*"))
        if filename := askopenfilename(
            title="Open a file", initialdir=str(Path.home()), filetypes=filetypes
        ):
            self.set_filename(filename)
            self.load()

    def save(self):
        self.job_config.to_file(self.filename)

    def save_as(self, filename: Optional[str] = None):
        if not filename:
            filetypes = (("print job configuration", "*.json"), ("All files", "*.*"))
            filename = asksaveasfilename(
                title="File path", filetypes=filetypes, initialdir=str(Path.home())
            )
            if not filename:
                return
        if not filename.endswith(".json"):
            filename = f"{filename}.json"
        self.set_filename(filename)
        self.save()

    def load(self):
        if not self.filename:
            return logging.warn("can't load as no file loaded yet")
        logging.info(f"load {self.filename}")
        self.job_config = JobConfig.from_file(self.filename)
        self.updatefields()

    def updatefields(self):
        self.fields.update(self.job_config)

    def set_filename(self, filename: str):
        self.filename = filename
        self.fields.filename.set(self.filename.split(os.sep)[-1])

    def select_resource(self):
        filetypes = (
            ("all files", "*.*"),
            ("pdf file", "*.pdf"),
            ("image file", "*.jpg"),
        )
        file_tuple = askopenfilenames(
            title="Open a file", initialdir=str(Path.home()), filetypes=filetypes
        )
        if not file_tuple:
            return

        resource_list = [Resource(p) for p in file_tuple]

        self.job_config.resource_list = resource_list
        self.updatefields()

    def select_printer_configuration(self):
        filetypes = (
            ("printer configuration", "*.yml"),
            ("all files", "*.*"),
        )
        filename = askopenfilename(
            title="Open a file",
            initialdir=initialdir(self.job_config.printer_config),
            filetypes=filetypes,
        )
        if filename:
            self.job_config.printer_config = filename
            self.updatefields()

    def select_cut(self, *_):
        self.job_config.cut = {"yes": True, "no": False}[self.fields.cut.get()]

    def select_sleep_time(self, value: str):
        if self.job_config:
            v = round(float(value), 2)
            self.job_config.sleep_time = v
            self.fields.sleep_time.set(v)


@dataclass
class JobManager:
    job_config_manager: JobConfigManager
    job: Optional[Job] = None

    def print(self):
        if self.job and self.job.is_printing:
            return logging.warn("job already printing!")

        config = self.job_config_manager.job_config
        if config:
            self.job = Job(config)
            self.job.print()
        else:
            logging.warn("no job config set")

    def stop(self):
        if self.job:
            self.job.stop()
            self.job = None


def initialdir(var):
    return (var and str(Path(var).parent)) or str(Path.home())
