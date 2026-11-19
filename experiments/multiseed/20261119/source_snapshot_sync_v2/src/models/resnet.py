"""CIFAR ResNet-32 (He et al., 2016), implemented as a supporting architecture.

The shortcut uses option A: spatial subsampling and symmetric zero padding.
No DS-AL author implementation is used in this module.
"""
import torch
from torch import nn
from torch.nn import functional as F


class BasicBlock(nn.Module):
    """Two 3x3 convolutions with an option-A identity shortcut."""
    def __init__(self, in_channels, channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, channels, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)
        self.stride, self.padding = stride, (channels - in_channels) // 2

    def forward(self, x):
        residual = x[:, :, ::self.stride, ::self.stride]
        if self.padding:
            residual = F.pad(residual, (0, 0, 0, 0, self.padding, self.padding))
        out = F.relu(self.bn1(self.conv1(x)))
        return F.relu(self.bn2(self.conv2(out)) + residual)


class CifarResNet32(nn.Module):
    """Standard 32-layer CIFAR network with a 64-dimensional feature vector."""
    feature_dimension = 64

    def __init__(self, classes=50):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, 1, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(16)
        self.layer1 = self._stage(16, 16, 1)
        self.layer2 = self._stage(16, 32, 2)
        self.layer3 = self._stage(32, 64, 2)
        self.linear = nn.Linear(64, classes)
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")

    @staticmethod
    def _stage(in_channels, channels, stride):
        return nn.Sequential(BasicBlock(in_channels, channels, stride),
                             *[BasicBlock(channels, channels) for _ in range(4)])

    def features(self, x):
        """Extract a batch of 64-D pooled backbone features without the classifier."""
        x = F.relu(self.bn1(self.conv1(x)))
        return F.adaptive_avg_pool2d(self.layer3(self.layer2(self.layer1(x))), 1).flatten(1)

    def forward(self, x):
        return self.linear(self.features(x))
