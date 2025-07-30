
### Installation

```bash
pip install loglu-pytorch
```

### Implementation

```python
import torch
from loglu_pytorch import LogLU

# Define the model
class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.fc1 = nn.Linear(784, 128)
        self.loglu = LogLU()        # <----- In This Way
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.fc1(x)
        x = self.loglu(x)
        x = self.fc2(x)
        return F.softmax(x, dim=1)  # Equivalent to 'softmax' activation in final layer

# Instantiate the model
model = MyModel()

# Print the model summary (you can use torchsummary for a detailed view)
from torchsummary import summary
summary(model, input_size=(1, 784))

```

## License

LogLU_Pytorch is released under the [Apache License 2.0](https://github.com/XenReZ/LogLU-PyTorch/blob/main/LICENSE).
