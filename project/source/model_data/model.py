from torch import float32, triu, ones, nn, softmax, abs, log
import numpy as np


def generate_causal_mask(size):
    mask = triu(ones(size, size), diagonal=1).bool()
    return mask


class EnhancedLSTMSkipBlock(nn.Module):
    def __init__(self, input_size, hidden_size, dropout: float):
        super().__init__()        
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.lstm_dropout = nn.Dropout(dropout)
        self.lstm_norm = nn.LayerNorm(hidden_size)
        self.lstm_activation = nn.Mish()
        
        # Улучшенные свертки
        self.conv = nn.Conv1d(hidden_size, hidden_size, kernel_size=5, 
                             padding=2, groups=hidden_size)

        self.dilated_conv = nn.Conv1d(
            hidden_size, hidden_size, kernel_size=3, padding=2, dilation=2)
        self.norm = nn.LayerNorm(hidden_size)
        
        self.activation = nn.Mish()
        
        # Регуляризация
        self.dropout = nn.Dropout(dropout)
        self.res_scale = nn.Parameter(ones(1))
        
        # Проекция
        self.proj = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.Dropout(dropout / 2)
        ) if input_size != hidden_size else None

        # Инициализация
        self._init_weights()

    def _init_weights(self):
        for name, param in self.lstm.named_parameters():
            if 'weight_ih' in name or 'weight_hh' in name:
                nn.init.orthogonal_(param)
        nn.init.xavier_uniform_(self.conv.weight)

    def forward(self, x):
        residual = x
        
        # Новый порядок операций:
        out, _ = self.lstm(x)
        out = self.lstm_norm(out)
        out = self.lstm_activation(out)
        out = self.lstm_dropout(out)
        
        # Обработка конволюциями
        x_permuted = out.permute(0, 2, 1)
        conv_out = self.conv(x_permuted).permute(0, 2, 1)
        dilated_out = self.dilated_conv(x_permuted).permute(0, 2, 1)
        
        out = conv_out + dilated_out
        out = self.norm(out)
        out = self.activation(out)
        out = self.dropout(out)

        if self.proj is not None:
            residual = self.proj(residual)
            
        return out + residual * self.res_scale
     
    
class KryptoModelWithAttention(nn.Module):
    def __init__(self, size: list, dropout=0.2, num_attention_heads_2=4, avg=1, device='cpu'):
        super().__init__()
        num_attention_heads_1 = size[0]
        num_layers = len(size) - 1
        self.size = size
        self.avg = avg
        
        self.attention_layer = nn.MultiheadAttention(embed_dim=size[0], num_heads=num_attention_heads_1, 
                                                           dropout=dropout, batch_first=True)
        self.attention_norm = nn.LayerNorm(size[0])
        self.attention_act = nn.Mish()
        
        for p in self.attention_layer.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
        
        self.unattention_layer = nn.MultiheadAttention(embed_dim=size[0], num_heads=num_attention_heads_1, 
                                                           dropout=dropout, batch_first=True)
        self.unattention_norm = nn.LayerNorm(size[0])
        self.unattention_act = nn.Mish()
        
        for p in self.unattention_layer.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
        
               
        self.layers = nn.ModuleList()
        
        for i in range(num_layers):
            self.layers.append(EnhancedLSTMSkipBlock(size[i], size[i+1], dropout).to(device))
           
        self.glodal_attention_norm = nn.LayerNorm(size[-1])
        self.glodal_attention = nn.MultiheadAttention(embed_dim=size[-1], num_heads=num_attention_heads_2, 
                                                           dropout=dropout, batch_first=True)
        self.global_act = nn.Mish()
        
        self.agr = nn.AdaptiveAvgPool1d(avg)
        self.fc = nn.Linear(size[-1]*avg, 5)
        self.relu = nn.ReLU()

    def forward(self, x):   
        feature_weights = softmax(x, dim=1)
        
        feature_unweights = abs(1 - softmax(x, dim=1))
        
        mask = generate_causal_mask(x.shape[1]).to(x.device)
        
        x_norm = self.attention_norm(x)
        feature_weights = softmax(x_norm, dim=-1)  # Softmax по фичам
        values = feature_weights * x_norm
        x_1, _ = self.attention_layer(x_norm, x_norm, values, attn_mask=mask)
        
        # Аналогично для unattention
        x_unorm = self.unattention_norm(x)
        feature_unweights = 1 - softmax(x_unorm, dim=1)
        unvalues = feature_unweights * x_unorm
        x_2, _ = self.unattention_layer(x_unorm, x_unorm, unvalues, attn_mask=mask)
        
        # Добавлен шлюз для комбинирования ветвей
        x = self.attention_act(x_1) + self.unattention_act(x_2)
             
        
        for layer in self.layers:
            x = layer(x)    # LSTM
        
            
        mask = generate_causal_mask(x.shape[1]).to(x.device)
            
        x_global = self.glodal_attention_norm(x)
        x_attn, _ = self.glodal_attention(x_global, x_global, x_global, attn_mask=mask)
        x = x + self.global_act(x_attn)
        
        x = self.agr(x.permute(0, 2, 1)).squeeze()
        if self.avg != 1:
            x = x.flatten(1)
        x = self.fc(x)
        x = self.relu(x)
        
        return log(x + 1) 
    
    
def cyclic_encode(unit, mode: str):
    angle = None
    if mode == 'hour':
        angle = 2 * np.pi * unit / 24
    elif mode == 'day':
        angle = 2 * np.pi * unit / 7
    elif mode == 'month':
        angle = 2 * np.pi * unit / 12
    return np.sin(angle), np.cos(angle)

        
if __name__ == '__main__':
    krpt_model = KryptoModelWithAttention(size=(19, 32, 64, 128, 256), dropout=0.2, avg=1)
    krpt_model = krpt_model.to(float32)