import os

import torch
from PIL import Image
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from yms_class.src.efficient_kan import KAN


class CustomDataset(Dataset):
    def __init__(self, root_dir, transform=None, class_to_label=None):
        self.root_dir = root_dir
        self.transform = transform or transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.class_to_label = class_to_label if class_to_label is not None else {}
        self.images = [f for f in os.listdir(root_dir) if f.endswith(('.bmp', '.jpg', '.png'))]

        # 如果没有提供class_to_label字典，我们在这里创建它
        if not self.class_to_label:
            self._create_class_to_label_mapping()
            self.idx_to_labels = {i: cls_name for i, cls_name in enumerate(self.class_to_label)}

    def _create_class_to_label_mapping(self):
        # 假设类别是从0开始编号的连续整数
        self.classes = sorted(set([filename.split('_')[0] for filename in self.images]))
        self.class_to_label = {cls: i for i, cls in enumerate(self.classes)}

    def get_class_to_label(self):
        return self.class_to_label

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        # 获取图片路径
        image_path = os.path.join(self.root_dir, self.images[idx])
        # 打开图片并转换为RGB格式
        image = Image.open(image_path)
        # 如果有变换，则进行变换
        if self.transform:
            image = self.transform(image).view(-1)

        # 提取文件名中的类别
        base_filename = os.path.splitext(self.images[idx])[0]
        class_name = base_filename.split('_')[0]
        # 将类别转换为标签
        label = self.class_to_label[class_name]

        return image, label

def create_dataloader(data_path, batch_size, transform=None, num_workers=0, train_shuffle=True):
    # 训练集数据加载器
    train_dir = os.path.join(data_path, 'train')
    train_dataset = CustomDataset(root_dir=train_dir, transform=transform)
    # 初始化验证集Dataset
    validation_dir = os.path.join(data_path, 'val')  # 替换为你的验证集图片目录
    validation_dataset = CustomDataset(root_dir=validation_dir, transform=transform)
    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=train_shuffle,
                                  num_workers=num_workers)
    val_loader = DataLoader(dataset=validation_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader

class AutoencoderClassifier(nn.Module):
    def __init__(self, input_dim=30000, latent_dim=512, num_classes=4):
        super(AutoencoderClassifier, self).__init__()

        # 分类器部分
        self.classifier = nn.Sequential(
            # nn.Linear(1024, 512),
            # nn.BatchNorm1d(512),
            # nn.ReLU(),
            # nn.Dropout(0.3),
            #
            # nn.Linear(512, 256),
            # nn.BatchNorm1d(256),
            # nn.ReLU(),
            #
            # nn.Linear(input_dim, 16384),
            # nn.BatchNorm1d(16384),
            # nn.ReLU(),
            # nn.Dropout(0.5),

            nn.Linear(input_dim, 8192),
            nn.BatchNorm1d(8192),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(8192, 4096),
            nn.BatchNorm1d(4096),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(4096, 2048),
            nn.BatchNorm1d(2048),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(2048, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(1024, 4),

            # nn.Linear(4096, 2048),
            # nn.BatchNorm1d(2048),
            # nn.ReLU(),
            # nn.Dropout(0.5),

            # KAN([4096, 2048, 1024, 512, 256, 128, 4]),
            # nn.ReLU(),
            # nn.Linear(128, num_classes)
        )

        # 可学习阈值 (K-1个阈值)
        self.thresholds = nn.Parameter(
            torch.linspace(-1, 1, num_classes - 1),
            requires_grad=True
        )

    def coral_loss(self, logits, targets):
        """
        CORAL损失函数 + 阈值有序正则化
        logits: 网络输出 [batch_size, 1]
        targets: 真实类别 [batch_size]
        """
        # 1. 准备阈值比较
        logits = logits.expand(-1, self.num_classes - 1)  # [batch_size, K-1]
        diff = logits - self.thresholds  # 与阈值比较

        # 2. 构建目标矩阵 (K-1个二分类任务)
        target_matrix = (targets.view(-1, 1) >
                         torch.arange(0, self.num_classes - 1, device=targets.device))
        target_matrix = target_matrix.float()

        # 3. 计算CORAL损失
        loss_fn = nn.BCEWithLogitsLoss()
        coral_loss = loss_fn(diff, target_matrix)

        # 4. 阈值有序性正则化 (确保阈值递增)
        threshold_diffs = self.thresholds[1:] - self.thresholds[:-1]
        reg_loss = torch.sum(torch.clamp(-threshold_diffs, min=0))  # 惩罚负差值

        return coral_loss + self.lambda_reg * reg_loss

    def forward(self, x):
        # 分类
        logits = self.classifier(x)

        return logits

    def predict(self, logits=None, x=None):
        """预测有序类别"""
        if logits is None and x is None:
            raise ValueError("logits和x不能同时为空，请至少提供其中一个参数")

        with torch.no_grad():
            # 计算超过的阈值数量即为预测类别
            if logits is None and x is not None:
                logits = self.forward(x)
            return (logits > self.thresholds).sum(dim=1)


if __name__ == '__main__':
    data = CustomDataset(r'D:\Code\0-data\7-images\2-wear\data\val')