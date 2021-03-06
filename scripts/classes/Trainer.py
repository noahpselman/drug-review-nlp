import time
import torch


class Trainer():
    """
    Object that can train a model
    """

    def __init__(self, *, loss_fn, optimizer, unpack_batch_fn):
        """
        Args:
            loss_fn: pytorch loss function such as CrossEntropyLoss 
            optimizer: pytorch optimizer
            unpack_batch_fn (fn): takes output of dataloader and formats it into tuple
                that can be passed to model # shouldn't be an attribute
        """
        self.loss_fn = loss_fn
        self.optimizer = optimizer
        self.unpack_batch_fn = unpack_batch_fn

    def train_an_epoch(self, *, model, log_interval, train_dataloader):
        """
        trains an epoch...

        Args:
            model (nn.Module)
            log_interval (int): how often the loss of an interation should be printed
            train_dataloader (DataLoader)
        """
        model.train()
        for idx, (data) in enumerate(train_dataloader):
            self.optimizer.zero_grad()
            inputs = self.unpack_batch_fn(data)  # should be a parameter
            predictions = model(*inputs)

            label = data['labels']
            loss = self.loss_fn(predictions, label)
            loss.backward()
            self.optimizer.step()
            if idx % log_interval == 0 and idx > 0:
                print(f'At iteration {idx} the loss is {loss:.3f}.')

    def train(self, *, model, evaluator, num_epochs, log_interval, train_dataloader, valid_dataloader):
        """
        executes all training

        Args:
            model (nn.Module)
            evaluator (Evaluator)
            num_epochs (int): num epochs to run
            log_interval (int): how often the loss of an interation should be printed
            train_dataloader (DataLoader)
            valid_dataloader (DataLoader)

        Returns:
            float: total time taken
        """

        total_time_taken = 0
        for epoch in range(num_epochs):
            epoch_start_time = time.time()
            self.train_an_epoch(
                model=model, log_interval=log_interval, train_dataloader=train_dataloader)
            time_taken = time.time() - epoch_start_time
            total_time_taken += time_taken
            with torch.no_grad():
                metric = evaluator.after_epoch(
                    epoch=epoch, model=model, time_taken=time_taken, train_dataloader=train_dataloader, valid_dataloader=valid_dataloader)
            print(
                f'Epoch: {epoch}, time taken: {time_taken:.1f}s, validation accuracy: {metric:.3f}.')

        return total_time_taken
