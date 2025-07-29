from zoneinfo import ZoneInfo


from kaggle.api.kaggle_api_extended import KaggleApi


def list_my_datasets():
    # 初始化Kaggle API
    api = KaggleApi()
    api.authenticate()

    # 获取用户名称（使用config_value方法）
    username = api.config_values['username']

    # 获取用户的所有数据集
    datasets = api.dataset_list(user=username, page=1)

    if not datasets:
        print("未找到你的数据集。")
        return

        # 准备数据集信息列表
    dataset_info = []
    for dataset in datasets:
        dataset_info.append({
                'title': dataset.title,
                'ref': dataset.ref,
                'creator_name': dataset.creator_name,
                'ID': dataset.id,
                'updated_time': dataset.last_updated.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
                'view_count': dataset.view_count,
                'vote_count': dataset.vote_count,
                'size(MB)': dataset.total_bytes / (1024 * 1024) if dataset.total_bytes else 0,
                'URL': f"https://www.kaggle.com/datasets/{dataset.ref}"
            })
    if not dataset_info:
        print("没有可用的数据集信息")
    else:
        # 提取表格数据（显式转换 headers 为列表）
        # headers = list(dataset_info[0].keys())  # 关键修改点
        headers = ['title', 'ref', 'creator_name', 'ID', 'updated_time', 'view_count','vote_count', 'size(MB)', 'URL']
        api.print_table(dataset_info, headers)
            # rows = [list(data.values()) for data in dataset_info]
            #
            # # 打印表格
            # print(tabulate(rows, headers=headers, tablefmt="grid", showindex=True))
            #
            # # 打印统计信息
            # print(f"\n共有 {len(dataset_info)} 个数据集")
            # total_size = sum(data['数据集大小(MB)'] for data in dataset_info)
            # print(f"总大小: {total_size:.2f} MB")


def list_my_kernels():
    # 初始化 Kaggle API
    api = KaggleApi()
    # 验证 API 凭证
    api.authenticate()

    try:
        # 获取用户名称（使用config_value方法）
        username = api.config_values['username']

        # 获取用户所有内核
        kernels = api.kernels_list(user=username, page_size=1000)

        if not kernels:
            print("未找到任何内核。")
            return

            # 准备数据集信息列表
        kernels_info = []
        for kernel in kernels:
            kernels_info.append({
                    '标题': kernel.title,
                    '链接': kernel.ref,
                    '创建人': kernel.author,
                    '数据集ID': kernel.id,
                    '更新日期': kernel.last_run_time.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
                    # '查看次数': kernel.view_count,
                    # '投票次数': kernel.vote_count,
                    'URL': f"https://www.kaggle.com/datasets/{kernel.ref}"
                })
        return kernels_info

    except Exception as e:
        print(f"发生错误: {str(e)}")
        print("请确保已正确配置 Kaggle API 凭证 (kaggle.json)")
        print("更多信息请参考: https://www.kaggle.com/docs/api")
