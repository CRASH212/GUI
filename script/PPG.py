from serial import Serial
# 只导入time模块中的time和 sleep函数
from time import time
# 只导入scipy.io模块中的savemat函数
from scipy.io import savemat,loadmat
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, lfilter_zi

##########11.17日txt改为config的版本  原名serial V4
from os import getcwd
from os.path import join
from time import strftime, localtime

def save_mat(patient_name,duration,mat):
    folder = getcwd()  # 获取当前工作目录
    # print(folder)
    ppgdata_folder = join(folder, 'Desktop/11.25版本5图形界面/ppgdata')      # 读取ppgdata文件夹
    #ppgdata_folder = join(folder, 'ppgdata') 
    current_time = strftime('%y-%m-%d_%H-%M-%S', localtime())
    new_name = f'{current_time}_{patient_name}_PPG数据{duration}s.mat'
    path = join(ppgdata_folder, new_name)  # 使用os.path.join拼接路径
    savemat(path, {'ppgdata': mat})
    # print(path)
    return path
def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    zi = lfilter_zi(b, a)
    y, _ = lfilter(b, a, data, zi=zi*data[0])
    #y = lfilter(b, a, data)
    return y
def showPLT(mat_filepath):
    # 从mat文件中读取数据
    mat_data = loadmat(mat_filepath)
    ppg_data = mat_data['ppgdata']
    # t = np.arange(0, 1.0, 1 / 113)
    amplitudes = [row[0] for row in ppg_data]
    # 应用低通滤波器
    filtered_data = lowpass_filter(amplitudes, 8, 113, order=6)

    # 绘制图表
    plt.plot(-filtered_data, label='filtered data')
    plt.xlabel('Points')
    plt.ylabel('Amplitude')
    plt.title('PPG Waveform')
    plt.show()

#11.2日新增波形显示，串口号更改  11.10优化了波形显示滤除了高频噪声
def open_txt():
    f = open("/home/ppg32/Desktop/11.25版本5图形界面/Config.txt", encoding="utf-8")
    lines = f.read().splitlines()
    # SavePath = '.\ppgdata\ppgdata.mat'   #linux要改为/  保存到上一级目录下的ppgdata并命名为ppgdata.mat
    # duration = int(lines[0])   #采集时长
    COM_num = lines[0]
    f.close()
    return COM_num

# if __name__ == '__main__':
def PPG_run(name, duration):  #gui_instance
    COM_num = open_txt()
    ser = Serial(str(COM_num), 115200)
    start_time = time()
    # duration = 30.0
    serial_data = b''
    print("开始采集ppg信号..等待"+str(duration)+"秒")
    while (time() - start_time) < duration:
        if ser.in_waiting > 0:
            byte_data = ser.read(ser.in_waiting)
            #print('bytedatais:')
            #print(byte_data)
            serial_data += byte_data

    decoded_data = serial_data.decode('ASCII', errors='ignore').strip()
    lines = decoded_data.split('\r\n')

    data_list = []
    lines = lines[1:]
    for line in lines:
        values = list(map(int, line.split(',')))  # 用逗号分隔每行数据，并将其转换为整数
        data_list.append(values)
    SavePath = save_mat(name,duration,data_list)
    # savemat(SavePath, {'ppgdata': data_list})
    print("PPG数据采集完成！")
    print("稍等..PPG波形为..")
    #showPLT(SavePath)
    #gui_instance.result_thread2 = SavePath  # 存储结果到 gui_instance
    return SavePath
#if __name__ == '__main__':
#    duration = 20
    
#    PPG_run('suwei', duration)  #, gui_instance
