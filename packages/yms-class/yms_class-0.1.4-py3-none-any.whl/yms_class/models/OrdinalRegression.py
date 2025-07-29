import sys
from typing import cast

import torch
from sklearn.metrics import accuracy_score
from torch import nn
from tqdm import tqdm


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_channel, out_channel, stride=1, downsample=None, **kwargs):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=in_channel, out_channels=out_channel,
                               kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channel)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(in_channels=out_channel, out_channels=out_channel,
                               kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channel)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        if self.downsample is not None:
            identity = self.downsample(x)

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        out += identity
        out = self.relu(out)

        return out


class Bottleneck(nn.Module):
    """
    注意：原论文中，在虚线残差结构的主分支上，第一个1x1卷积层的步距是2，第二个3x3卷积层步距是1。
    但在pytorch官方实现过程中是第一个1x1卷积层的步距是1，第二个3x3卷积层步距是2，
    这么做的好处是能够在top1上提升大概0.5%的准确率。
    可参考Resnet v1.5 https://ngc.nvidia.com/catalog/model-scripts/nvidia:resnet_50_v1_5_for_pytorch
    """
    expansion = 4

    def __init__(self, in_channel, out_channel, stride=1, downsample=None,
                 groups=1, width_per_group=64):
        super(Bottleneck, self).__init__()

        width = int(out_channel * (width_per_group / 64.)) * groups

        self.conv1 = nn.Conv2d(in_channels=in_channel, out_channels=width,
                               kernel_size=1, stride=1, bias=False)  # squeeze channels
        self.bn1 = nn.BatchNorm2d(width)
        # -----------------------------------------
        self.conv2 = nn.Conv2d(in_channels=width, out_channels=width, groups=groups,
                               kernel_size=3, stride=stride, bias=False, padding=1)
        self.bn2 = nn.BatchNorm2d(width)
        # -----------------------------------------
        self.conv3 = nn.Conv2d(in_channels=width, out_channels=out_channel*self.expansion,
                               kernel_size=1, stride=1, bias=False)  # unsqueeze channels
        self.bn3 = nn.BatchNorm2d(out_channel*self.expansion)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        if self.downsample is not None:
            identity = self.downsample(x)

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        out += identity
        out = self.relu(out)

        return out


class ResNet(nn.Module):

    def __init__(self,
                 block,
                 blocks_num,
                 num_classes=1000,
                 include_top=True,
                 groups=1,
                 width_per_group=64):
        super(ResNet, self).__init__()
        self.include_top = include_top
        self.in_channel = 64

        self.groups = groups
        self.width_per_group = width_per_group

        self.conv1 = nn.Conv2d(3, self.in_channel, kernel_size=7, stride=2,
                               padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(self.in_channel)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, blocks_num[0])
        self.layer2 = self._make_layer(block, 128, blocks_num[1], stride=2)
        self.layer3 = self._make_layer(block, 256, blocks_num[2], stride=2)
        self.layer4 = self._make_layer(block, 512, blocks_num[3], stride=2)
        if self.include_top:
            self.avgpool = nn.AdaptiveAvgPool2d((1, 1))  # output size = (1, 1)
            self.fc = nn.Linear(512 * block.expansion, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')

    def _make_layer(self, block, channel, block_num, stride=1):
        downsample = None
        if stride != 1 or self.in_channel != channel * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channel, channel * block.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(channel * block.expansion))

        layers = []
        layers.append(block(self.in_channel,
                            channel,
                            downsample=downsample,
                            stride=stride,
                            groups=self.groups,
                            width_per_group=self.width_per_group))
        self.in_channel = channel * block.expansion

        for _ in range(1, block_num):
            layers.append(block(self.in_channel,
                                channel,
                                groups=self.groups,
                                width_per_group=self.width_per_group))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        if self.include_top:
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
            x = self.fc(x)

        return x

# 编码器
class ContinuousTransitionCNN(nn.Module):
    def __init__(self, in_channels=3, num_classes=4, lambda_reg=0.1):
        super().__init__()
        self.num_classes = num_classes
        self.lambda_reg = lambda_reg

        self.model = ResNet(Bottleneck, [3, 4, 6, 3], num_classes=1, include_top=True)

        # 可学习阈值 (K-1个阈值)
        self.thresholds = nn.Parameter(
            torch.linspace(-1, 1, num_classes - 1),
            requires_grad=True
        )

    def forward(self, x):
        x = self.model(x)
        return x
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

    def predict(self, logits):
        """预测有序类别"""
        with torch.no_grad():
            # 计算超过的阈值数量即为预测类别
            return (logits > self.thresholds).sum(dim=1)



def train_model(model, train_loader, device, optimizer, epoch):
    mean_loss = torch.zeros(1).to(device)
    all_predictions = []
    all_labels = []
    model.train()
    train_iterator = tqdm(train_loader, file=sys.stdout, desc=f'the {epoch + 1} epoch is training....', colour='blue')
    for step, (images, labels) in enumerate(train_iterator):
        # 将数据转移到设备
        images, labels = images.to(device), labels.to(device)
        # 梯度清0
        optimizer.zero_grad()
        # 前向传播
        outputs = model(images)
        # 计算损失
        loss = model.coral_loss(outputs, labels)
        # 反向传播
        loss.backward()
        # 更新参数
        optimizer.step()

        mean_loss = (mean_loss * step + loss.detach()) / (step + 1)
        predicted = model.predict(outputs)
        # 设置进度条
        train_iterator.set_postfix(loss=loss.item(), mean_loss=mean_loss.item())
        all_predictions.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    train_accuracy = accuracy_score(y_true=all_labels, y_pred=all_predictions)
    return mean_loss.item(), train_accuracy


@torch.no_grad()
def val_model(model, val_loader, device, epoch):
    result = {"y_pred": [], "y_true": [], 'val_loss': 0.}
    result = cast(dict, result)
    val_loss = torch.zeros(1).to(device)
    model.eval()
    val_iterator = tqdm(val_loader, file=sys.stdout, desc=f'{epoch + 1} epoch is validation...', colour='GREEN')
    for step, (images, labels) in enumerate(val_iterator):
        # 将数据转移到设备
        images, labels = images.to(device), labels.to(device)
        # 计算结果
        outputs = model(images)
        # 计算损失
        loss = model.coral_loss(outputs, labels)
        # 计算数据集上的全部损失
        val_loss = (val_loss * step + loss.detach()) / (step + 1)
        # 计算预测正确的样本
        predicted = model.predict(outputs)
        val_iterator.set_postfix(loss=loss.item(), val_loss=val_loss.item())

        result["y_pred"].extend(predicted.cpu().numpy())
        result["y_true"].extend(labels.cpu().numpy())

    result['val_loss'] = val_loss.item()
    return result

# if __name__ == '__main__':
#     model = ContinuousTransitionCNN(num_classes=4, lambda_reg=0.1)
#     l = torch.randn(3, 1)
#     t = torch.randn(3)
#     loss = model.coral_loss(l, t)
#     print()