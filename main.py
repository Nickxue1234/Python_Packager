import pkg_resources
import subprocess
import threading
from tkinter import *
from tkinter import font, messagebox
import queue

result_queue = queue.Queue()

class Root(Tk):
    def __init__(self, func):
        super().__init__()
        self.fontstyle = font.Font(family="华文行楷")
        self.is_onefile = IntVar()
        self.is_console = IntVar()
        self.func = func

        self.label1 = Label(self, text="Python文件打包器", font=self.fontstyle)
        self.label2 = Label(self, text="打包文件路径", font=self.fontstyle)
        self.file_path = Entry(self)
        self.label3 = Label(self, text="输出路径", font=self.fontstyle)
        self.output_path = Entry(self)
        self.label4 = Label(self, text="图标路径", font=self.fontstyle)
        self.icon_path = Entry(self)
        self.onefile = Checkbutton(self, text="是否输出单个文件", font=self.fontstyle, variable=self.is_onefile)
        self.console = Checkbutton(self, text="是否需要命令行", font=self.fontstyle, variable=self.is_console)
        self.package = Button(self, text="打包", command=lambda: self.func(self.file_path.get(), self.output_path.get(), self.is_onefile.get(), self.is_console.get(), self.icon_path.get()))

        self.label1.grid(row=1, column=1, columnspan=4)
        self.label2.grid(row=2, column=1)
        self.file_path.grid(row=2, column=2)
        self.label3.grid(row=3, column=1)
        self.output_path.grid(row=3, column=2)
        self.label4.grid(row=4, column=1)
        self.icon_path.grid(row=4, column=2)
        self.onefile.grid(row=5, column=1)
        self.console.grid(row=6, column=1)
        self.package.grid(row=7, column=1)

        self.title("Python文件打包器")
        self.check_queue()

    def check_queue(self):
        try:
            result = result_queue.get_nowait()
            if result == "success":
                messagebox.showinfo("提示", "打包成功")
            elif result == "failure":
                messagebox.showinfo("提示", "打包失败")
        except queue.Empty:
            pass
        self.after(100, self.check_queue)  # 每100毫秒检查一次队列

    def run(self):
        self.mainloop()


class Start_to_package(threading.Thread):
    def __init__(self, script_path, output_dir, onefile, no_console, icon):
        super().__init__()
        self.script_path = script_path
        self.output_dir = output_dir
        self.onefile = onefile
        self.no_console = no_console
        self.icon = icon

    def run(self):
        packager(self.script_path, self.output_dir, self.onefile, self.no_console, self.icon)


def install_pyinstaller():
    try:
        pkg_resources.get_distribution("pyinstaller")
    except pkg_resources.DistributionNotFound:
        subprocess.check_call(["pip", "install", "pyinstaller"])


def packager(script_path, output_dir=None, onefile=True, no_console=True, icon=None):
    command = ["pyinstaller", ]
    if onefile:
        command.append("--onefile")
    if no_console:
        command.append("--noconsole")
    if icon:
        command.extend(["--icon", icon])
    if output_dir:
        command.extend(["--distpath", output_dir])
    command.append(script_path)
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result_queue.put("success")
    except subprocess.CalledProcessError:
        result_queue.put("failure")


def run_thread(script_path, output_dir, onefile, no_console, icon):
    thread = Start_to_package(script_path, output_dir, onefile, no_console, icon)
    thread.start()


if __name__ == "__main__":
    install_pyinstaller()
    root = Root(run_thread)
    root.run()
