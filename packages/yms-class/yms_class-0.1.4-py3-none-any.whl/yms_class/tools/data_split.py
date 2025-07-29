import os
import shutil
import random
from collections import defaultdict

import numpy as np


# def split_dataset(source_dir, target_root, ratio=(0.8, 0.2), seed=42):
#     # 检查源文件夹是否存在
#     if not os.path.exists(source_dir):
#         print(f"源文件夹 {source_dir} 不存在。")
#         return
#     # 按前缀分组图片
#     prefix_groups = defaultdict(list)
#     for filename in os.listdir(source_dir):
#         prefix = filename.split('_')[0]
#         file_path = os.path.join(source_dir, filename)
#         prefix_groups[prefix].append((filename, file_path))
#
#     # 创建目标文件夹
#     train_dir = os.path.join(target_root, 'train')
#     val_dir = os.path.join(target_root, 'val')
#     os.makedirs(train_dir, exist_ok=True)
#     os.makedirs(val_dir, exist_ok=True)
#
#     # 对每个分组按比例划分并复制文件
#     random.seed(seed)
#     for prefix, files in prefix_groups.items():
#         total = len(files)
#         if total == 0:
#             continue
#         train_num = int(total * ratio[0])
#         val_num = total - train_num
#
#         random.shuffle(files)
#         train_files = files[:train_num]
#         val_files = files[train_num:]
#
#         def copy_files(file_list, target_dir):
#             for filename, src_path in file_list:
#                 target_file_path = os.path.join(target_dir, filename)
#                 try:
#                     shutil.move(src_path, target_file_path)
#                 except Exception as e:
#                     print(f"复制 {filename} 时出错: {e}")
#
#         copy_files(train_files, train_dir)
#         copy_files(val_files, val_dir)
#         print(f"前缀 {prefix}：共 {total} 张，划分 train:{len(train_files)} | val:{len(val_files)}")

def split_dataset(source_dir, target_root, ratio=(0.8, 0.2), seed=42):
    # 检查源文件夹是否存在
    if not os.path.exists(source_dir):
        print(f"源文件夹 {source_dir} 不存在。")
        return

    # 按前缀分组图片
    prefix_groups = defaultdict(list)
    all_classes = set()  # 用于收集所有类别

    for filename in os.listdir(source_dir):
        # 提取类别（假设文件名格式为'class_数字_...'）
        class_name = filename.split('_')[0]
        all_classes.add(class_name)

        file_path = os.path.join(source_dir, filename)
        prefix_groups[class_name].append((filename, file_path))

    # 创建目标文件夹
    train_dir = os.path.join(target_root, 'train')
    val_dir = os.path.join(target_root, 'val')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    # 生成类别映射
    classes = sorted(all_classes)
    classes_to_idx = {cls: i for i, cls in enumerate(classes)}
    idx_to_labels = {i: cls for i, cls in enumerate(classes)}

    # 保存映射为npy文件
    np.save(os.path.join(target_root, 'classes_to_idx.npy'), classes_to_idx)
    np.save(os.path.join(target_root, 'idx_to_labels.npy'), idx_to_labels)
    print(f"类别映射已保存至 {target_root}/classes_to_idx.npy 和 {target_root}/idx_to_labels.npy")

    # 对每个分组按比例划分并复制文件
    random.seed(seed)
    for class_name, files in prefix_groups.items():
        total = len(files)
        if total == 0:
            continue

        train_num = int(total * ratio[0])
        val_num = total - train_num

        random.shuffle(files)
        train_files = files[:train_num]
        val_files = files[train_num:]

        def copy_files(file_list, target_dir):
            for filename, src_path in file_list:
                target_file_path = os.path.join(target_dir, filename)
                try:
                    shutil.move(src_path, target_file_path)
                except Exception as e:
                    print(f"移动 {filename} 到 {target_dir} 时出错: {e}")

        copy_files(train_files, train_dir)
        copy_files(val_files, val_dir)
        print(f"类别 {class_name}: 共 {total} 张，划分 train: {len(train_files)} | val: {len(val_files)}")



def copy_images_by_prefix(source_folder, destination_folder, prefix):
    # 检查源文件夹是否存在
    if not os.path.exists(source_folder):
        print(f"源文件夹 {source_folder} 不存在。")
        return
    # 若目标文件夹不存在则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        # 检查文件名是否以指定前缀开头
        if filename.startswith(prefix):
            source_file_path = os.path.join(source_folder, filename)
            destination_file_path = os.path.join(destination_folder, filename)
            try:
                # 复制文件
                shutil.move(source_file_path, destination_file_path)
                print(f"已移动 {filename} 到 {destination_folder}")
            except Exception as e:
                print(f"移动 {filename} 时出错: {e}")


def split_3dataset(source_dir, target_root, ratio=(0.7, 0.2, 0.1), seed=42):
    # 检查源文件夹是否存在
    if not os.path.exists(source_dir):
        print(f"源文件夹 {source_dir} 不存在。")
        return

    # 按前缀分组图片
    prefix_groups = defaultdict(list)
    all_classes = set()  # 用于收集所有类别

    for filename in os.listdir(source_dir):
        # 提取类别（假设文件名格式为'class_数字_...'）
        class_name = filename.split('_')[0]
        all_classes.add(class_name)

        file_path = os.path.join(source_dir, filename)
        prefix_groups[class_name].append((filename, file_path))

    # 创建目标文件夹
    train_dir = os.path.join(target_root, 'train')
    val_dir = os.path.join(target_root, 'val')
    test_dir = os.path.join(target_root, 'test')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    # 生成类别映射
    classes = sorted(all_classes)
    classes_to_idx = {cls: i for i, cls in enumerate(classes)}
    idx_to_labels = {i: cls for i, cls in enumerate(classes)}

    # 保存映射为npy文件
    np.save(os.path.join(target_root, 'classes_to_idx.npy'), classes_to_idx)
    np.save(os.path.join(target_root, 'idx_to_labels.npy'), idx_to_labels)
    print(f"类别映射已保存至 {target_root}/classes_to_idx.npy 和 {target_root}/idx_to_labels.npy")

    # 对每个分组按比例划分并复制文件
    random.seed(seed)
    for class_name, files in prefix_groups.items():
        total = len(files)
        if total == 0:
            continue

        train_num = int(total * ratio[0])
        val_num = int(total * ratio[1])
        test_num = total - train_num - val_num

        random.shuffle(files)
        train_files = files[:train_num]
        val_files = files[train_num:train_num + val_num]
        test_files = files[train_num + val_num:]

        def copy_files(file_list, target_dir):
            for filename, src_path in file_list:
                target_file_path = os.path.join(target_dir, filename)
                try:
                    shutil.move(src_path, target_file_path)
                except Exception as e:
                    print(f"移动 {filename} 到 {target_dir} 时出错: {e}")

        copy_files(train_files, train_dir)
        copy_files(val_files, val_dir)
        copy_files(test_files, test_dir)
        print(
            f"类别 {class_name}: 共 {total} 张，划分 train:{len(train_files)} | val: {len(val_files)} | test: {len(test_files)}")


# 使用示例
source_dir = r'D:\Code\0-data\7-images\2-wear\500'  # 替换为实际的源文件夹路径
target_root = r'D:\Code\0-data\7-images\2-wear\5'  # 替换为实际的目标文件夹路径
split_dataset(source_dir, target_root)
# split_3dataset(source_dir, target_root)
    # 演示如何加载保存的映射
# loaded_classes_to_idx = np.load(os.path.join(target_root, 'classes_to_idx.npy'), allow_pickle=True).item()
# loaded_idx_to_labels = np.load(os.path.join(target_root, 'idx_to_labels.npy'), allow_pickle=True).item()
# print("加载的类别到索引映射:")
# for cls, idx in loaded_classes_to_idx.items():
#     print(f"{cls}: {idx}")
# A 2-B-007 1-IR-014 2-IR-014 1-OR-007 0-OR-014 1-OR-021
# 使用示例
# source_folder = r'D:\Code\2-ZSL\Zero-Shot-Learning\data\images'  # 替换为实际的源文件夹路径
# destination_folder = r'D:\Code\2-ZSL\Zero-Shot-Learning\data\B\unseen\images'  # 替换为实际的目标文件夹路径
# prefix_list = ['1-IR-007', '2-B-014', '0-OR-021', '2-IR-021', '0-B-014', '1-OR-014']
# for prefix in prefix_list:
#     copy_images_by_prefix(source_folder, destination_folder, prefix)
