import torch
from torch import nn


class CNN(nn.Module):
    def __init__(self, num_classes=4):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.avgpool = nn.AdaptiveAvgPool2d((6, 6))
        self.fc = nn.Sequential(
            nn.Linear(256 * 6 * 6, 4096),
            nn.ReLU(),
            nn.Dropout(p=0.5),

            nn.Linear(4096, 2048),
            nn.ReLU(),
            nn.Dropout(p=0.5),

            nn.Linear(2048, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


# class CNN(nn.Module):
#     def __init__(self, num_classes=10):
#         super().__init__()
#         self.features = FeatureExtractor()
#         self.classifier = nn.Sequential(
#             nn.Linear(4096, 2048),
#             nn.ReLU(),
#             nn.Linear(2048, num_classes)
#         )
#         # self.fc3 = nn.Linear(2048, num_classes)
#         self.relu = nn.ReLU()
#
#     def save(self, path):
#         torch.save(self.features, path)
#
#     def forward(self, x):
#         x = self.features(x)
#         x = self.relu(x)
#         x = self.classifier(x)
#         return x

if __name__ == '__main__':
    model = CNN(num_classes=4)
    y = model(torch.randn(1, 3, 100, 100))
    print(y)
