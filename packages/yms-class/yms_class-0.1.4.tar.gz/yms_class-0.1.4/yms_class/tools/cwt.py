import glob
import sys

import matplotlib.pyplot as plt
import numpy as np
import pywt
from tqdm import tqdm
import os
from scipy.io import loadmat
'''
num: 图片保存时防止名字重复，通过末尾数字区分
total: 保存的图片总量
start_num: 从csv表格的第几行开始读取（一般从第二行读取，0代表第二行）
space: 读取间隔（我这里是每1024个采样点作为一个样本）
sampling_period: 采样率（根据数据集实际情况设置，比如数据集采样率为12kHz，则sampling_period = 1.0 / 12000）
totalscal: 小波变换尺度（我这里是256）
wavename: 小波基函数（morl用的比较多，还有很多如：cagu8，cmor1-1等等）
'''


def img_time_freq(data, total, start_num, end_num, space, sampling_period, totalscal, wavename, class_name, save_path):
    bar_format = '{percentage:.1f}%| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'
    for i in tqdm(range(0, total), bar_format=bar_format, file=sys.stdout, colour='green'):
        # 加载数据集
        signal = data[start_num:end_num]
        start_num += space
        end_num += space

        # 计算小波基函数的中心频率fc,然后根据totalscal 计算参数cparam
        # 通过除以np.arange(totalscal, 0, -1) 来生成一系列尺度值，并存储在scales中
        fc = pywt.central_frequency(wavename)
        cparam = 2 * fc * totalscal
        scales = cparam / np.arange(totalscal, 0, -1)

        # 连续小波变换函数
        coefficients, frequencies = pywt.cwt(signal, scales, wavename, sampling_period)

        # 计算变换系数的幅度
        amp = abs(coefficients)

        # 根据采样周期生成时间轴
        t = np.linspace(1, sampling_period, (end_num-start_num), endpoint=False)

        # 绘制时频图
        image_path = os.path.join(save_path, (class_name + '_' + str(i)+'.jpg'))
        plt.figure(figsize=(42 / 100, 42 / 100))
        plt.contourf(t, frequencies, amp, cmap='jet')
        plt.axis('off')  # 去坐标轴
        plt.xticks([])  # 去x轴刻度
        plt.yticks([])  # 去y轴刻度
        # 去白边
        plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
        plt.close()


# def img_time_freq(data, start_num, end_num, space, sampling_period, totalscal, wavename, save_dir):
#     n = data.shape[1]
#     # for i in range(0, n):
#     bar_format = '{percentage:.1f}%| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'
#     for i in tqdm(range(0, n), bar_format=bar_format):
#         signals = data[:, i]
#         total = int(signals.shape[0] / space)
#         start = start_num
#         end = end_num
#         for j in range(0, total):
#             signal = signals[start:end]
#             start += space
#             end += space
#             # 计算小波基函数的中心频率fc,然后根据totalscal 计算参数cparam
#             # 通过除以np.arange(totalscal, 0, -1) 来生成一系列尺度值，并存储在scales中
#             fc = pywt.central_frequency(wavename)
#             cparam = 2 * fc * totalscal
#             scales = cparam / np.arange(totalscal, 0, -1)
#             # 连续小波变换函数
#             coefficients, frequencies = pywt.cwt(signal, scales, wavename, sampling_period)
#             # 计算变换系数的幅度
#             amp = abs(coefficients)
#             # frequencies.max()
#             # 根据采样周期生成时间轴
#             t = np.linspace(1, sampling_period, 1024, endpoint=False)
#             # 绘制时频图
#             plt.figure(figsize=(42 / 100, 42 / 100))
#             plt.contourf(t, frequencies, amp, cmap='jet')
#             plt.axis('off')  # 去坐标轴
#             plt.xticks([])  # 去x轴刻度
#             plt.yticks([])  # 去y轴刻度
#             # image_name = r"D:\Code\0-data\2-滚刀磨损数据集\工况2(2db)"
#             image_name = os.path.join(save_dir, str(i) + '_' + str(j))
#             plt.savefig("{}_resized.jpg".format(image_name.split(".jpg")[0]), bbox_inches='tight', pad_inches=0)
#             plt.close()


def time_freq(data, num, total, start_num, end_num, space, sampling_period, totalscal, wavename, image_path):
    for i in tqdm(range(0, total)):
        # for i in range(0, total):
        # data = data.loc[start_num:end_num, 'data']
        signals = data[start_num:end_num]
        # 计算小波基函数的中心频率fc,然后根据totalscal 计算参数 cparam
        # 通过除以np.arange(totalscal, 0, -1) 来生成一系列尺度值，并存储在scales中
        fc = pywt.central_frequency(wavename)
        cparam = 2 * fc * totalscal
        scales = cparam / np.arange(totalscal, 0, -1)

        # 连续小波变换函数
        coefficients, frequencies = pywt.cwt(signals, scales, wavename, sampling_period)

        # 计算变换系数的幅度
        amp = abs(coefficients)
        # frequencies.max()

        # 根据采样周期生成时间轴
        t = np.linspace(1, sampling_period, 1024, endpoint=False)

        # 绘制时频图
        image_name = os.path.join(image_path, str(num) + '.jpg')
        plt.figure(figsize=(224 / 100, 224 / 100))
        plt.contourf(t, frequencies, amp, cmap='jet')
        plt.axis('off')  # 去坐标轴
        plt.xticks([])  # 去x轴刻度
        plt.yticks([])  # 去y轴刻度
        # 去白边
        plt.savefig(image_name, bbox_inches='tight', pad_inches=0)
        plt.close()
        start_num += space
        end_num += space
        num += 1


def calculate_optimal_parameter(folder_path, window=None, overlap_ratio=None, num_blocks=None):
    """
    根据MAT文件中DE数据的长度，计算满足条件的采样参数最大值

    参数:
        folder_path: MAT文件所在文件夹路径
        window: 采样窗口长度
        overlap_ratio: 重叠率(0-1之间的小数)
        num_blocks: 分割块数

    返回:
        计算得到的参数最大值
    """
    # 确保提供了两个参数
    provided_params = sum(p is not None for p in [window, overlap_ratio, num_blocks])
    if provided_params != 2:
        raise ValueError("必须提供三个参数中的任意两个")

    # 读取所有MAT文件中的DE数据长度
    mat_files = glob.glob(os.path.join(folder_path, "*.mat"))
    data_lengths = []

    for file_path in mat_files:
        try:
            mat_data = loadmat(file_path)
            if 'DE' in mat_data:
                data_lengths.append(len(mat_data['DE'].reshape(-1)))
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")

    if not data_lengths:
        raise ValueError("未找到包含DE键的MAT文件")

    min_length = min(data_lengths)  # 所有文件中最短的DE数据长度
    print(f"所有MAT文件中DE数据的最小长度: {min_length}")

    # 根据已知参数计算第三个参数
    if window is not None and overlap_ratio is not None:
        # 已知窗口和重叠率，计算最大块数
        if window <= 0 or overlap_ratio < 0 or overlap_ratio >= 1:
            raise ValueError("窗口长度必须大于0，重叠率必须在0到1之间")

        effective_length = window * (1 - overlap_ratio)
        if effective_length <= 0:
            raise ValueError("有效长度不能为0或负数")

        max_num_blocks = int((min_length - window) // effective_length + 1)
        max_num_blocks = max(1, max_num_blocks)  # 至少1块
        overlap_length = int(window * overlap_ratio)
        print(f"采样窗口长度: {window}, 重叠率: {overlap_ratio * 100:.2f}%, 最大分割块数: {max_num_blocks}, 重叠窗口大小:{overlap_length}")


    elif window is not None and num_blocks is not None:
        # 已知窗口和块数，计算最大重叠率
        if window <= 0 or num_blocks < 1:
            raise ValueError("窗口长度必须大于0，块数必须至少为1")

        if num_blocks == 1:
            max_overlap_ratio = 0.0  # 只有一块时无需重叠
        else:
            # required_length = (num_blocks - 1) * window
            # if required_length > min_length:
            #     raise ValueError(f"块数{num_blocks}和窗口{window}无法满足最小数据长度{min_length}")

            max_overlap_ratio = 1 - (min_length - window) / ((num_blocks - 1) * window)
            max_overlap_ratio = max(0.0, min(max_overlap_ratio, 0.95))  # 限制重叠率在0-95%
            overlap_length = int(window * max_overlap_ratio)

            print(f"采样窗口长度: {window}, 最大重叠率: {max_overlap_ratio * 100:.2f}%, 分割块数: {num_blocks}"
                    f"重叠窗口: {overlap_length}")


    elif overlap_ratio is not None and num_blocks is not None:
        # 已知重叠率和块数，计算最大窗口
        if overlap_ratio < 0 or overlap_ratio >= 1 or num_blocks < 1:
            raise ValueError("重叠率必须在0到1之间，块数必须至少为1")

        if num_blocks == 1:
            max_window = min_length  # 只有一块时窗口等于数据长度
        else:
            denominator = 1 + (num_blocks - 1) * (1 - overlap_ratio)
            if denominator <= 0:
                raise ValueError("参数组合导致分母为0或负数")

            max_window = int(min_length // denominator)
            max_window = max(1, max_window)  # 窗口至少为1

        print(f"最大采样窗口长度: {max_window}, 重叠率: {overlap_ratio * 100:.2f}%, 分割块数: {num_blocks}")


    else:
        raise ValueError("参数组合错误")


if __name__ == '__main__':
    # data_dir = r'D:\Code\0-data\6-数据集-mat\3-industrial-bigdata\mat_Noised_SNR-2'
    # mat_names = os.listdir(data_dir)
    # for mat_name in mat_names:
    #     class_name = mat_name.split('.')[0]
    #     mat_path = os.path.join(data_dir, mat_name)
    #     data = loadmat(mat_path)['DE'].reshape(-1)
    #     img_time_freq(data, 500, 0, 1024, 512, 1.0/120000,
    #                   256, 'morl', class_name, r'D:\Code\0-data\7-images\3-industrial-bigdata\小波变换\images')

    # data = loadmat(r'D:\Code\0-data\7-HOB\HOB\1-H1.mat')['DE'].reshape(-1)
    # img_time_freq(data, 1000, 0, 2048, 2048, 1.0/10000,
    #               256, 'morl', '1-H1', r'D:\Code\0-data\0-故障诊断结果输出\HOB\1-H1')
    calculate_optimal_parameter(r'D:\Code\0-data\6-数据集-mat\1-CRWU\0HP',
                                    window=1024, overlap_ratio=0.75)

