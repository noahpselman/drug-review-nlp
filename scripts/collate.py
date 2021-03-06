import json
import torch
from torch.nn.utils.rnn import pad_sequence


def make_collate_rnn(vocab, device='cpu'):
    """
    builds collate function for recurrent layers
    requires padding sequences such that all examples become equal
    in length to the longest in the batch

    Args:
        vocab (vocab object): can map tokens to indexes
        device (str, optional): cuda or cpu

    Returns:
        fn: collate function that takes batches
    """

    SENTIMENT_CATEGORIES = {
        "Negative": 0,
        "Neutral": 1,
        "Positive": 2
    }
    try:
        PADDING_IDX = vocab['<pad>']
    except Exception:
        print("probably don't have '<pad>' in your vocab, add that then try again")
        raise

    def collate_rnn(batch):
        labels = []
        revs = []
        lengths = []
        for (l, t) in batch:
            labels.append(SENTIMENT_CATEGORIES[l])
            tokens = json.loads(t['tokens'])
            review = torch.tensor([vocab.stoi[token.lower()]
                                  for token in tokens])
            revs.append(review)
            lengths.append(len(tokens))

        revs = pad_sequence(revs, batch_first=True, padding_value=PADDING_IDX)

        return {"labels": torch.tensor(labels).to(device), "reviews": revs.to(device), "lengths": torch.tensor(lengths).to('cpu')}

    return collate_rnn


def make_collate_rnn_lemmas(vocab, device='cpu'):
    """
    builds collate function for recurrent layers
    requires padding sequences such that all examples become equal
    in length to the longest in the batch
    uses lemmas instead of tokens
    this could be refactored and combined with the previous function

    Args:
        vocab (vocab object): can map tokens to indexes
        device (str, optional): cuda or cpu

    Returns:
        fn: collate function that takes batches
    """

    SENTIMENT_CATEGORIES = {
        "Negative": 0,
        "Neutral": 1,
        "Positive": 2
    }
    try:
        PADDING_IDX = vocab['<pad>']
    except Exception:
        print("probably don't have '<pad>' in your vocab, add that then try again")
        raise

    def collate_rnn_lemmas(batch):
        labels = []
        revs = []
        lengths = []
        for (l, t) in batch:
            labels.append(SENTIMENT_CATEGORIES[l])
            tokens = json.loads(t['lemmas'])
            review = torch.tensor([vocab.stoi[token.lower()]
                                  for token in tokens])
            revs.append(review)
            lengths.append(len(tokens))

        revs = pad_sequence(revs, batch_first=True, padding_value=PADDING_IDX)

        return {"labels": torch.tensor(labels).to(device), "reviews": revs.to(device), "lengths": torch.tensor(lengths).to('cpu')}

    return collate_rnn_lemmas


def make_collate_plus(device='cpu', vocab={}, encoded_cols=[], encoding_lengths={}):
    """
    builds collate function for recurrent layers
    requires padding sequences such that all examples become equal
    in length to the longest in the batch

    Args:
        vocab (vocab object): can map tokens to indexes
        device (str, optional): cuda or cpu
        encoded_cols (list of str, optional): list of key names that must be turned into
            one-hot encodings
        encoding_lengths: (dict {encoding_cols: int}): maps encoding_cols to length of the
            one-hot vector

    Returns:
        fn: collate function that takes batches
    """
    SENTIMENT_CATEGORIES = {
        "Negative": 0,
        "Neutral": 1,
        "Positive": 2
    }
    try:
        PADDING_IDX = vocab['<pad>']
    except Exception:
        print("probably don't have '<pad>' in your vocab, add that then try again")
        raise

    def collate_rnn_plus(batch):
        labels = []
        revs = []
        lengths = []
        encodings = {col: [] for col in encoded_cols}
        for i, (l, t) in enumerate(batch):
            labels.append(SENTIMENT_CATEGORIES[l])
            toks = json.loads(t['tokens'])

            review = torch.tensor([vocab.stoi[token.lower()]
                                   for token in toks])
            revs.append(review)
            lengths.append(len(toks))
            for col in encoded_cols:
                indices = json.loads(t[col])
                one_hot_list = []
                for idx in indices:
                    one_hot = [0] * encoding_lengths[col]
                    one_hot[idx] = 1
                    one_hot_list.append(one_hot)
                one_hot_tensor = torch.tensor(one_hot_list)

                encodings[col].append(one_hot_tensor)

        revs = pad_sequence(revs, batch_first=True, padding_value=PADDING_IDX)
        for e in encodings:
            encodings[e] = pad_sequence(
                encodings[e], batch_first=True, padding_value=PADDING_IDX).to(device)

        lengths_tensor = torch.tensor(lengths)

        return {"labels": torch.tensor(labels).to(device), "reviews": revs.to(device), "lengths": lengths_tensor, **encodings}

    return collate_rnn_plus
