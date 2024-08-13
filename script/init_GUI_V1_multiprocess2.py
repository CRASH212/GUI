import sys
import multiprocessing
import threading
#import mttkinter as tkinter
from tkinter import Tk, Button, Entry, Label, Frame, NORMAL  ,END
from tkinter.messagebox import askyesno
from tkinter.scrolledtext import ScrolledText
#from mttkinter.mtTkinter import Tk, Button, Entry, Label, Frame, NORMAL ,END

from FmcwRadar import radar_run
from PPG import PPG_run
from functools import partial
from showplt_V3 import show_plt
from PPG import showPLT
# from queue import Queue
def radar_running(name, duration, result_queue):
    result = radar_run(name, duration)
    # 将结果放入队列
    result_queue.put(result)


def PPG_running(name, duration, result_queue):
    result = PPG_run(name, duration)
    # 将结果放入队列
    result_queue.put(result)

def update_gui():
    init_window.after(100,update_gui)    
class RaspiGui(object):
    def __init__(self, init_window_name):
        self.result_thread1 = None  # 添加result_thread2属性，默认值为None
        self.result_thread2 = None  # 添加result_thread2属性，默认值为None
        self.init_window_name = init_window_name
        self.init_window_name.title("雷达PPG双通道脉搏波采集程序")  # 设置窗口标题
        self.init_window_name.geometry('200x300')  # 设置窗口大小
        """ 点击右上角关闭窗体弹窗事件 """
        self.init_window_name.protocol('WM_DELETE_WINDOW', self.clos_window)
        """ 组件容器创建 """
        self.log_frame = Frame(self.init_window_name)  # 创建存放日志组件的容器
        self.log_frame.grid(padx=0, pady=5, row=0, column=0)
        self.runs_button_frame = Frame(self.init_window_name)  # 创建存放日志组件的容器
        self.runs_button_frame.grid(padx=0, pady=5, row=1, column=0)
        """ 日志框 """
        self.run_log = ScrolledText(self.log_frame, font=('楷体', 10), width=22, height=7)
        self.run_log.grid(padx=19, pady=0, row=0, column=0)
        """ 操作按钮 """
        # 创建提示标签
        self.label = Label(self.runs_button_frame, text="请输入当前病例姓名", font=('行楷', 10), fg="black", bg="#F5B29E", width=17)
        self.label.grid(padx=0, pady=0, row=0, column=0)
        # 创建输入框
        self.entry = Entry(self.runs_button_frame, width=17)
        self.entry.grid(padx=0, pady=0, row=1, column=0)
        self.pre_button = Button(self.runs_button_frame, text='预采集20s', font=('行楷', 10), fg="white", bg="#1E90FF",
                                 width=15, command=lambda: self.thread_it(partial(self.collect_data, 20)))
        self.pre_button.grid(padx=0, pady=7, row=2, column=0)
        self.collect_button = Button(self.runs_button_frame, text='一键采集60s', font=('行楷', 10), fg="white", bg="#1E90FF", width=15, command=lambda: self.thread_it(partial(self.collect_data, 60)))
        self.collect_button.grid(padx=0, pady=7, row=3, column=0)  #, row=1, column=1
        self.collect_button = Button(self.runs_button_frame, text='一键采集120s', font=('行楷', 10), fg="white", bg="#1E90FF", width=15, command=lambda: self.thread_it(partial(self.collect_data, 120)))
        self.collect_button.grid(padx=0, pady=7, row=4, column=0)  #, row=1, column=1
    def thread_it(self, func, *args):
        """ 将函数打包进线程 """
        self.myThread = threading.Thread(target=func, args=args)
        self.myThread.setDaemon(True)  # 主线程退出就直接让子线程跟随退出,不论是否运行完成。
        self.myThread.start()
    def collect_data(self, duration):
        self.clear_log_text()  # 在新的数据采集前清空文本
        name = self.get_name()
        duration = int(duration)

        # 创建两个队列，用于获取进程的返回值
        result_queue1 = multiprocessing.Queue()
        result_queue2 = multiprocessing.Queue()
        # 创建两个进程，分别执行 radar_run 和 PPG_run
        process1 = multiprocessing.Process(target=radar_running, args=(str(name), duration, result_queue1))
        process2 = multiprocessing.Process(target=PPG_running, args=(str(name), duration, result_queue2))

        # 启动两个进程
        process1.start()
        process2.start()

        # 等待两个进程完成
        process1.join()
        process2.join()

        # radar_data_path = self.result_thread1
        # ppg_data_path = self.result_thread2
        # 获取进程的返回值
        radar_data_path = result_queue1.get()
        ppg_data_path = result_queue2.get()
        print("雷达数据路径:", radar_data_path)
        print("PPG数据路径:", ppg_data_path)
        # 调用画图函数，并将数据文件路径作为参数传递给它
        self.draw_plot(radar_data_path, ppg_data_path)

    def draw_plot(self, radar_data_path, ppg_data_path):
        show_plt(radar_data_path)
        showPLT(ppg_data_path)

    def get_name(self):
        # 使用entry.get()获取输入框中的病人姓名
        patient_name = self.entry.get()
        print("病人姓名：", patient_name)
        self.run_log_print(message="病人姓名:"+patient_name)
        return patient_name

    def run_log_print(self, message):
        self.run_log.config(state=NORMAL)
        self.run_log.insert(END, "\n" + message + "\n")
        self.run_log.see(END)
        self.run_log.update()
    def clear_log_text(self):
        self.run_log.delete("1.0", "end")  # 清空文本
    def clos_window(self):
        ans = askyesno(title='脉搏波采集程序v1.0', message='是否确定退出程序？')
        if ans:
            self.init_window_name.destroy()

if __name__ == '__main__':
    """ 把button方法打包进线程，现实运行不卡顿 """
    """ 实例化出一个父窗口 """
    init_window = Tk()
    init_window.after(100,update_gui)
    """ tk界面置顶 """
    init_window.attributes("-topmost", 1)
    """ 创建Gui类对象 """
    test_gui = RaspiGui(init_window)
    """ 初始化GUi组件 """
    init_window.mainloop()
