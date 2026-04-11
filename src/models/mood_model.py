import torch
import torch.nn as nn
import torch.nn.functional as F

class MoodNet(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_moods):
        super(MoodNet, self).__init__()
        
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.dropout1 = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.dropout2 = nn.Dropout(0.2)
        self.fc3 = nn.Linear(hidden_dim // 2, num_moods)
        
    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout1(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc3(x)
        
        # Use sigmoid if multi-label, softmax if single-label
        return torch.sigmoid(x)