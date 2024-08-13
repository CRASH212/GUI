# ===========================================================================
# Copyright (C) 2022 Infineon Technologies AG
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ==============原名rawdataV3===================新版波束形成+自动选波束  11.17txt改为Config  11.18打包为雷达exe====11.24改为函数文件对接图形窗口=================================
# from ifxradarsdk import get_version
from ifxradarsdk.fmcw import DeviceFmcw
from ifxradarsdk.fmcw.types import FmcwSimpleSequenceConfig, FmcwSequenceChirp

import numpy as np
# from showplt_V3 import show_plt
from scipy.io import savemat
# import matplotlib;matplotlib.use('TKAgg')

from os import getcwd
from os.path import join
from time import strftime, localtime


def save_mat(patient_name,duration,mat):
    folder = getcwd()  # 获取当前工作目录
    # print(folder)
    # 读取pulsedata文件夹
    pulsedata_folder = join(folder, 'Desktop/11.25版本5图形界面/pulsedata')
    # timestamp = current_time.replace(':', '-')
    current_time = strftime('%y-%m-%d_%H-%M-%S', localtime())
    new_name = f'{current_time}_{patient_name}_雷达数据{duration}s.mat'
    path = join(pulsedata_folder, new_name)  # 使用os.path.join拼接路径
    savemat(path, {'pulsedata': mat})
    # print(path)
    return path

def radar_run(name,duration):
    frate = 110
    frame_numbers = duration*frate
    config = FmcwSimpleSequenceConfig(
        frame_repetition_time_s=1/frate,  # Frame repetition time 0.15s (frame rate of 6.667Hz) 40Hz
        chirp_repetition_time_s=0.000264,  # Chirp repetition time (or pulse repetition time) of 0.5ms
        num_chirps=1,  # chirps per frame 128
        tdm_mimo=False,  # MIMO disabled
        chirp=FmcwSequenceChirp(
            start_frequency_Hz=58_000_000_000,  # start frequency: 60 GHz   60e9
            end_frequency_Hz=63_000_000_000,  # end frequency: 61.5 GHz   61.5e9
            sample_rate_Hz=2.5e6,  # ADC sample rate of 1MHz  1e6
            num_samples=16,  # 64 samples per chirp
            rx_mask=7,  # RX antennas 1 and 3 activated
            tx_mask=1,  # TX antenna 1 activated
            tx_power_level=31,  # TX power level of 31
            if_gain_dB=33,  # 33dB if gain
        )
    )
    # lp_cutoff_Hz = 500000,  # Anti-aliasing cutoff frequency of 500kHz
    # hp_cutoff_Hz = 80000,  # 80kHz cutoff frequency for high-pass filter
    with DeviceFmcw() as device:
        print("Sensor: " + str(device.get_sensor_type()))

        sequence = device.create_simple_sequence(config)
        device.set_acquisition_sequence(sequence)
        print("开始采集雷达信号！等待"+str(duration)+"秒..")
        #gui_instance.run_log_print(message="开始采集雷达信号！等待"+str(duration)+"秒..")
        mat = np.zeros((frame_numbers, config.chirp.num_samples,3))
        for frame_number in range(frame_numbers):
            frame_contents = device.get_next_frame()  #print("this is frameshape:"+str(len(frame_contents)))   #其实只有一个frame在frame_contents里
            frame = frame_contents[0]
            for i_ant in range(3):
                mat[frame_number, :,i_ant] = np.squeeze(frame[i_ant, 0, :])
    # print("采集完成！数据形状：" + str(mat.shape))  # (3, 200, 256)    采集完成！数据形状：(400, 64, 3)
    print("雷达数据采集完成！")
    # io.savemat(SavePath, {'pulsedata': mat})
    SavePath = save_mat(name,duration,mat)
    print("稍等..波形显示为..")
    # show_plt(SavePath, frate)
    #gui_instance.run_log_print(message="雷达数据采集完成！") # 将信息插入 Text 组件
    #gui_instance.run_log_print(message= "稍等..波形显示为..")

    #gui_instance.result_thread1 = SavePath  # 存储结果到 gui_instance
    return SavePath
# if __name__ == '__main__':
#     radar_run('吴彦祖',20)
