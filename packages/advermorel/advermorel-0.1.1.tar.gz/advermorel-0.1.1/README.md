# AdverMOREL

> A multi-objective optimization framework for improving DNN robustness against adversarial attacks.

## Installation

```python
conda create -n advermorel python=3.13
conda activate advermorel
pip install advermorel
# To install CUDA‐enabled PyTorch, run (or visit: https://pytorch.org/get-started/locally/):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
Or, to install the latest code from GitHub:
```python
conda create -n advermorel python=3.13
conda activate advermorel
git clone https://github.com/salomonhotegni/MOREL.git
cd src/advermorel
pip install -e .
# To install CUDA‐enabled PyTorch, run (or visit: https://pytorch.org/get-started/locally/):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Basic usage
Assume you want to train a ResNet-18 model with MOREL on the CIFAR-10 dataset. The advermorel package provides three objective functions for robust prediction—TRADES, MART, and LOAT—but you can also supply your own. Below is an end-to-end example training ResNet-18 for 10 epochs. By default, PGD-10 with `epsilon = 0.031` is considered for training.
```python
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
from torchvision.models import resnet18
from advermorel import MOREL

EPOCHS = 10
BATCH_SIZE = 128

my_model = resnet18()
classifier_layer = "fc" # the name of the classifier in resnet18()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Initialize the MOREL class
morel = MOREL(original_model=my_model, 
              name_last_layer=classifier_layer,
              num_class=10, device=device, accu_obj="mart")

# Prepare the train dataloader:
transform_train = torchvision.transforms.Compose(
            [
                torchvision.transforms.RandomCrop(32, padding=4),
                torchvision.transforms.RandomHorizontalFlip(),
                torchvision.transforms.ToTensor(),
            ]
        )
trainset = torchvision.datasets.CIFAR10(
            root="data/cifar10", train=True, download=True, transform=transform_train
        )
train_loader = torch.utils.data.DataLoader(
        trainset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2
    )

# Choose an optimizer:
optimizer = optim.SGD(
                morel.model.parameters(),
                lr=0.001,
                momentum=0.9,
                weight_decay=2e-4,
            )

# Train the model:
morel.train(optimizer=optimizer,
            scheduler=scheduler,
            num_epochs=EPOCHS, 
            train_loader=train_loader, 
            val_loader=test_loader, seed=0)
```
 Let’s evaluate the model’s robustness on the test dataset using a new adversarial attack. The `advermorel` package accepts attack methods from the `adversarial-robustness-toolbox`. In this example, we apply the CW-∞ attack:
```python
from art.attacks.evasion import CarliniLInfMethod
from art.estimators.classification import PyTorchClassifier

# Prepare the test dataloader:
transform_test = torchvision.transforms.Compose(
            [
                torchvision.transforms.ToTensor(),
            ]
        )
testset = torchvision.datasets.CIFAR10(
            root="data/cifar10", train=False, download=True, transform=transform_test
        )
test_loader = torch.utils.data.DataLoader(
        testset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2
    )

# Create the CW-inf attack
classifier_att = PyTorchClassifier(
                    model=morel.model,
                    clip_values=(0.0, 1.0),
                    loss=nn.CrossEntropyLoss(),
                    optimizer=optimizer,
                    input_shape=(3, 32, 32),
                    nb_classes=morel.num_class,
                )
attack = CarliniLInfMethod(
            classifier=classifier_att,
            targeted=False,
            initial_const=15,
            learning_rate=1e-2,
            max_iter=10,
            batch_size=BATCH_SIZE,
        )

# Test the robustness of the trained model against this attack:
clean_accuracy, robust_accuracy = morel.test(test_loader, attack=attack)
```
## Citation
If you find `advermorel` useful in your research, please consider citing:
```
@inproceedings{hotegni2025morel,
  title     = {Enhancing Adversarial Robustness through Multi-Objective Representation Learning},
  author    = {Hotegni, Sedjro Salomon and Peitz, Sebastian},
  booktitle = {International Conference on Artificial Neural Networks},
  year      = {2025},
  publisher = {Springer}
}

```
