from torch.nn import functional as F
from torch.autograd import Variable
from torch import nn, optim
import torch

class VAE(nn.Module):
    def __init__(self):
        super(VAE, self).__init__()

        self.fc1 = nn.Linear(784, 400)
        self.fc21 = nn.Linear(400, 20)
        self.fc22 = nn.Linear(400, 20)
        self.fc3 = nn.Linear(20, 400)
        self.fc4 = nn.Linear(400, 784)

    def encode(self, x):
        h1 = F.relu(self.fc1(x))
        return self.fc21(h1), self.fc22(h1)

    def reparameterize(self, mu, logvar):
        if self.training:
            std = torch.exp(0.5*logvar)
            eps = Variable(std.data.new(std.size()).normal_())
            return eps.mul(std).add_(mu)
        else:
            return mu

    def decode(self, z):
        h3 = F.relu(self.fc3(z))
        return F.sigmoid(self.fc4(h3))

    def forward(self, x):
        mu, logvar = self.encode(x.view(-1, 784))
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar

class CVAE(nn.Module):
    def __init__(self):
        super(CVAE, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(11, 3, 3, 1, 1),
            nn.ReLU(),
            nn.Conv2d(3, 1, 3, 1, 1),
            nn.ReLU()
        )
        self.fc1 = nn.Sequential(
            nn.Linear(784, 400, bias = True),
            nn.ReLU()
        )
        self.fc21 = nn.Linear(400, 20, bias = True)
        self.fc22 = nn.Linear(400, 20, bias = True)
        self.fc3 = nn.Sequential(
            nn.Linear(30, 392, bias = True),
            nn.ReLU()
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(2, 11, 3, 1, 1),
            nn.ReLU(),
            nn.UpsamplingNearest2d(scale_factor = 2),
            nn.Conv2d(11, 3, 3, 1, 1),
            nn.ReLU(),
            nn.Conv2d(3, 1, 3, 1, 1),
            nn.Sigmoid()
        )

    def encode(self, x, y):
        onehot = torch.zeros(x.size(0), 10, 28, 28)
        for idx, single_t in enumerate(y):
            onehot[idx, single_t, :, :] += 1
        onehot = Variable(onehot).cuda()
        x = torch.cat([x, onehot], 1)
        h1 = self.fc1(self.conv1(x).view(-1, 784))
        return self.fc21(h1), self.fc22(h1)

    def reparameterize(self, mu, logvar):
        if self.training:
            std = torch.exp(0.5*logvar)
            eps = Variable(std.data.new(std.size()).normal_())
            return eps.mul(std).add_(mu)
        else:
            return mu

    def decode(self, z, y):
        y = torch.stack([y], -1)
        onehot = torch.FloatTensor(y.size(0), 10)
        onehot.zero_()
        onehot.scatter_(1, y, 1)
        onehot = Variable(onehot).cuda()
        z = torch.cat([onehot, z], 1)
        h1 = self.fc3(z).view(y.size(0), 2, 14, 14)
        return self.conv2(h1)

    def forward(self, x, y):
        mu, logvar = self.encode(x, y)
        z = self.reparameterize(mu, logvar)
        return self.decode(z, y), mu, logvar

if __name__ == '__main__':
    net = CVAE()
    print(net)