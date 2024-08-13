import numpy as np
from scipy.io import loadmat
from scipy.signal import butter, lfilter, lfilter_zi
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from pywt import wavedec,waverec

#################### 用来作为rawdata的库文件，没有if main
def SpecAnalysis(data, Fs):
    N = len(data)  # 数据长度（离散点）
    t = np.arange(0, N) / Fs  # 时间数组
    f = Fs * np.arange(N//2 + 1) / N  # 频谱频率范围

    # 原始信号绘图
    plt.figure(figsize=(10, 6))
    plt.subplot(3, 1, 1)
    plt.plot(t, data)
    plt.title('Original signal')
    plt.xlabel('t (s)')
    plt.ylabel('Amplitude')

    plt.subplot(3, 1, 2)
    plt.plot(t, -data)
    plt.title('Original signal')
    plt.xlabel('t (s)')
    plt.ylabel('Amplitude')

    # 原始信号单边频谱
    Y = np.fft.fft(data)
    P2 = abs(Y) / N
    P1 = P2[:N//2 + 1]
    P1[1:-1] = 2 * P1[1:-1]

    plt.subplot(3, 1, 3)
    plt.plot(f, P1)
    plt.title('Single-Sided Amplitude Spectrum of Original signal')
    plt.xlabel('f (Hz)')
    plt.ylabel('Amplitude')

    plt.tight_layout()
    plt.show()

def wavelet(signal):
    level = 8
    coeffs = wavedec(signal, 'db8', level=level)
    approx = coeffs[0]
    cd8, cd7, cd6, cd5, cd4, cd3, cd2, cd1 = coeffs[1:]
    # 以下代码段的注释部分表示您可以选择保留哪些细节系数（cd1 到 cd8）和阈值选择
    approx[:] = 0
    # cd1[:] = 0
    # cd2[:] = 0
    cd3[:] = 0
    # cd4[:] = 0.3*cd4[:]    #80Hz:5-10     30Hz:1.875-3.75
    # cd5[:] = 0
    # cd6[:] = 0
    cd7[:] = 0   #80Hz:0.625-1.25   30Hz:0.234375-0.46875
    cd8[:] = 0   #80Hz:0.3125-0.625  30Hz:0.1171875-0.234375
    # 假设您想保留所有细节系数，可以如下组装c1
    c1 = [approx] + [cd8, cd7, cd6, cd5, cd4, cd3, cd2, cd1]

    s2 = waverec(c1, 'db8')  # 重构信号

    return s2
def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    zi = lfilter_zi(b, a)
    y, _ = lfilter(b, a, data, zi=zi*data[0])
    return y

# Usage example:
# Wavesignal = bandpass(signal, order, low_stop, high_stop, Fs)

def beam_formed(num_antennas, num_beams, max_angle_degrees, d_by_lambda, raw_data):   #, theta
    angle_vector = np.radians(np.linspace(-max_angle_degrees, max_angle_degrees, num_beams))
    weights = np.zeros((num_antennas, num_beams), dtype=complex)
    for iBeam in range(num_beams):
        angle = angle_vector[iBeam]
        for iAntenna in range(num_antennas):
            weights[iAntenna, iBeam] = np.exp(
                1j * 2 * np.pi * iAntenna * d_by_lambda * np.sin(angle))  # /sqrt(num_antennas)
    weights = weights
    num_frame, num_samples, num_antennas  = raw_data.shape    #3  400 256
    rd_beam_formed = np.zeros((num_frame, num_samples, num_beams), dtype=complex);
    for iBeam in range(num_beams):
        acc = np.zeros((num_frame, num_samples), dtype=complex)
        for iAntenna in range(num_antennas):
            acc += raw_data[:, :, iAntenna] * weights[num_antennas - iAntenna - 1, iBeam]
        rd_beam_formed[:, :, iBeam] = acc
    return rd_beam_formed

def unwrap_data(data):
    Frame,ADCSamples = data.shape

    # Compute the FFT
    fft1 = np.fft.fft(data, axis=1)
    fft_data_last = np.zeros(ADCSamples)
    range_max = -1000

    # Calculate the nonstatic part
    nonstatic = fft1 - np.sum(fft1, axis=0) / Frame
    for j in range(ADCSamples):
        for i in range(Frame // 2):
            fft_data_last[j] += abs(nonstatic[i, j])
        if fft_data_last[j] > range_max:
            range_max = fft_data_last[j]
            max_num = j
    range_bin = fft1[:, max_num]

    # Extract and unwrap the phase
    phase_extraction = np.angle(range_bin)
    phase_unwrapped = np.unwrap(phase_extraction)
    phase_unwrapped = phase_unwrapped - np.mean(phase_unwrapped)
    unwrap_data = phase_unwrapped
    return unwrap_data

def show_plt(PATHNAME,fs=110,ibeam_num=66):
    s = loadmat(PATHNAME)  # 加载MAT文件
    raw_data = s['pulsedata']  # 加载文件格式为结构体
    num_rx_antennas = 3
    num_beams = 121
    max_angle_degrees = 60
    d_by_lambda = 0.5

    s = beam_formed(num_rx_antennas, num_beams, max_angle_degrees, d_by_lambda, raw_data)  # 波束形成
    s = s[:,:,ibeam_num]
    phase = unwrap_data(s)  # 相位解包裹
    phase1 = wavelet(phase)  # 小波变换去除趋势项
    waveform = lowpass_filter(phase1, 6, fs, order=6)  # 带通滤波
    SpecAnalysis(waveform, fs)  # 频谱分析
