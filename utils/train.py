import torch
from torch import nn

from tqdm import tqdm
import datetime
import copy
import time


def train_model(model, dataloaders, criterion, optimizer, scheduler, num_epochs=5):
    since = time.time()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size = dataloaders["train"].batch_size
    dataset_sizes = {x: len(dataloaders[x])
                     * batch_size for x in ['train', 'val']}
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 100)

        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            print(datetime.datetime.now(), "\n")
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            count = 0
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)
                count = count + 1

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                # track history if only in train
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)
                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                # statistics
                running_loss += loss.item()
                running_corrects += torch.sum(preds == labels.data)

                if count % 100 == 0:
                    print("-"*40)
                    print("STEP : ", count, "/", len(dataloaders[phase]))
                    print('ACC : {:.4f}'.format(running_corrects.double(
                    )/(count*batch_size)), phase.upper(), "LOSS: {:.4f}".format(running_loss / count))
#                     if phase == "train": writer.add_scalar('training loss',running_loss / count , epoch * len(train_dataloader) + count)
#                     if phase == "train": writer.add_scalar('training Accuracy',running_corrects.double() / (count*batch_size) , epoch * len(train_dataloader) + count)
#                     if phase == "test": writer.add_scalar('testing loss',running_loss / count , epoch * len(test_dataloader) + count)
#                     if phase == "test": writer.add_scalar('testing Accuracy',running_corrects.double() / (count*batch_size) , epoch * len(test_dataloader) + count)
#                     if phase == "train": writer.add_histogram("FC1 - Weights",model.fc1.weight.cpu().detach().numpy(),count)
#                     if phase == "train": writer.add_histogram("Conv1 - Weights",model.conv_1.weight.cpu().detach().numpy(),count)
#                     if phase == "train": writer.add_histogram("Conv2 - Weights",model.conv_2.weight.cpu().detach().numpy(),count)
#                     if phase == "train": writer.add_histogram("Conv3 - Weights",model.conv_3.weight.cpu().detach().numpy(),count)
#                     if phase == "train": writer.add_histogram("Conv4 - Weights",model.conv_4.weight.cpu().detach().numpy(),count)
#                     writer.flush()

            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / len(dataloaders[phase])
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print("-"*100)
            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))

            # deep copy the model
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

    time_elapsed = time.time() - since
    print("-"*100)
    print("-"*100)
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model
