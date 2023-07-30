from pathlib import Path
from sklearn.model_selection import train_test_split
from transformers import DistilBertForSequenceClassification, Trainer, TrainingArguments
import json
import torch
from collections import Counter
from torch.optim import AdamW
from sklearn import preprocessing
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast


# https://huggingface.co/transformers/v3.2.0/custom_datasets.html

# Reads Data and splits into Train/Test/Validation Set

# This function basically gets all the labels and their corresponding text
def read_data_split(json_file_path):
    # Path to where data is found
    json_file_path = Path(json_file_path)

    # Open the file and load the json
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    texts = []
    labels = []
    for item in data:
        texts.append(item['description'])
        labels.append(item['code'])

    # This will tell you how many labels you have (put in the model)
    counter = Counter(labels)
    # As of right now, reduce the data to 1000 each per code
    return texts, labels


# DO NOT RUN THIS ON YOUR LOCAL COMPUTER, I ASSURE YOU IT IS NOT POWERFUL ENOUGH
def train_model():
    # If this file does not exist locally, run get_training_data from datacleaning.py
    train_texts, train_labels = read_data_split('../model_training_data.json')
    # test_texts, test_labels = read_data_split('aclImdb/test')

    train_texts, val_texts, train_labels, val_labels = train_test_split(train_texts, train_labels, test_size=.2)

    # Label Encoding for strings
    le = preprocessing.LabelEncoder()
    # Assuming train_labels and val_labels are your labels
    train_labels = le.fit_transform(train_labels)
    val_labels = le.transform(val_labels)

    # Tokenization
    from transformers import DistilBertTokenizerFast

    tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')

    # What the tokenizer does (for this and a lot of other cases) is convert the text into tokens (usually numbers)
    # that the model understands
    train_encodings = tokenizer(train_texts, truncation=True, padding=True)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True)

    # test_encodings = tokenizer(test_texts, truncation=True, padding=True)

    class Dataset(torch.utils.data.Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)

    train_dataset = Dataset(train_encodings, train_labels)
    val_dataset = Dataset(val_encodings, val_labels)
    # test_dataset = Dataset(test_encodings, test_labels)

    # So far the steps above prepared the datasets in the way that the trainer is expected

    # Training the model
    training_args = TrainingArguments(
        output_dir='./results',  # output directory
        num_train_epochs=1,
        # total number of training epochs : This means how many times the training loop will go through entire data set
        per_device_train_batch_size=16,  # batch size per device during training
        per_device_eval_batch_size=64,  # batch size for evaluation
        warmup_steps=500,  # number of warmup steps for learning rate scheduler
        weight_decay=0.01,  # strength of weight decay
        logging_dir='./logs',  # directory for storing logs
        logging_steps=10,
        use_mps_device=True,
    )

    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=48)

    trainer = Trainer(
        model=model,  # the instantiated 🤗 Transformers model to be trained
        args=training_args,  # training arguments, defined above
        train_dataset=train_dataset,  # training dataset
        eval_dataset=val_dataset  # evaluation dataset
    )
    print("Starting Training")
    trainer.train()
    print("All Finished")


def get_label_decoder():
    # If running file alone uncomment this and comment the one below
    # train_texts, train_labels = read_data_split('../model_training_data.json')

    # If running through manage.py
    train_texts, train_labels = read_data_split('model_training_data.json')

    # test_texts, test_labels = read_data_split('aclImdb/test')

    train_texts, val_texts, train_labels, val_labels = train_test_split(train_texts, train_labels, test_size=.2)

    # Label Encoding for strings
    le = preprocessing.LabelEncoder()
    # Assuming train_labels and val_labels are your labels
    train_labels = le.fit_transform(train_labels)
    val_labels = le.transform(val_labels)

    return le


# Le is the label encoder
def classify_code(description: str, le):
    # specify the model class and the tokenizer
    model_class = DistilBertForSequenceClassification
    tokenizer_class = DistilBertTokenizerFast

    # load the model

    # If running file alone, uncomment this and comment the one below
    # model = model_class.from_pretrained('../trademarkSearch/result')

    # If running through manage.py
    model = model_class.from_pretrained('trademarkSearch/result')

    # load the tokenizer
    tokenizer = tokenizer_class.from_pretrained('distilbert-base-uncased')

    # Suppose we want to predict the label for the following text

    # We first need to tokenize the text
    inputs = tokenizer(description, truncation=True, padding=True, return_tensors="pt")

    # Then we can feed the tokenized text into the model and get a prediction
    outputs = model(**inputs)

    # The model returns the logits
    logits = outputs.logits

    # The predicted class is the one that has the highest score in the logits vector
    predicted_class = torch.argmax(logits, dim=1)

    # This converts the predicted_class back into whatever the original label was (the code)
    predicted_label = le.inverse_transform(predicted_class.detach().numpy())

    return predicted_label
