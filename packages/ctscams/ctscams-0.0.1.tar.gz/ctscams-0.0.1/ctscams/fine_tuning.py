import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, EarlyStoppingCallback, set_seed
from datasets import Dataset
import gc
from sklearn.metrics import precision_recall_fscore_support,accuracy_score, roc_auc_score, average_precision_score
from tqdm.notebook import tqdm_notebook
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit
import shutil
import stat
import os
import pandas as pd



def finetune_individual(train_data, val_data, model_name,cluster_no,folder_name,
                        text_col='text', label_col="label", learning_rate=1e-5,
                        warmup_ratio=0.05, weight_decay=0.1,epochs=5, batch_size=8,
                        label2id = {"Positive": 2, "Negative": 0, "Neutral": 1},
                        early_stopping_patience=2):
    base_model_name = model_name.split("/")[-1]
    new_folder_name = f"{folder_name}/{base_model_name}/{cluster_no}"
    print("Finetuning!")
    set_seed(42)
    id2label = {v: k for k, v in label2id.items()}
    # Ensure labels are mapped to integers
    train_data[label_col] = train_data[label_col].map(label2id).astype(int)
    val_data[label_col] = val_data[label_col].map(label2id).astype(int)

    # Convert to Hugging Face Dataset
    train_dataset = Dataset.from_pandas(train_data)
    val_dataset = Dataset.from_pandas(val_data)

    if model_name=="vinai/bertweet-large":
        tokenizer = AutoTokenizer.from_pretrained(model_name,use_auth_token=False, use_fast=False)
    else:
        # Tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_name,use_auth_token=False)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(label2id), 
                                                               label2id=label2id,id2label=id2label,
                                                               use_auth_token=False).to("cuda")

    # Tokenize function with padding and truncation
    def tokenize_function(example):
        return tokenizer(
            example[text_col],
            padding="max_length",
            truncation=True,
            max_length=512
        )
    
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    val_dataset = val_dataset.map(tokenize_function, batched=True)
    # Rename the label column to "labels" (required by the Trainer)
    train_dataset = train_dataset.rename_column(label_col, "labels")
    val_dataset = val_dataset.rename_column(label_col, "labels")
    train_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])
    val_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

    def compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions

        # Apply Softmax to get probability distributions
        probs = torch.nn.functional.softmax(torch.tensor(preds), dim=1).numpy()

        # Get class labels from predictions
        pred_labels = np.argmax(probs, axis=1)

        precision, recall, f1, _ = precision_recall_fscore_support(labels, pred_labels, average="weighted")
        acc = accuracy_score(labels, pred_labels)

        # AUROC & AUPRC need probability distributions, not hard labels
        auroc = roc_auc_score(labels, probs, average="weighted", multi_class="ovr")  
        auprc = average_precision_score(labels, probs, average="weighted")

        return {
            'accuracy': acc,
            'f1': f1,
            'precision': precision,
            'recall': recall,
            'auroc': auroc,
            'auprc': auprc
        }

    training_args = TrainingArguments(
        output_dir=f"./results/{new_folder_name}",
        overwrite_output_dir=True,
        logging_dir=f"./log/{new_folder_name}", 
        evaluation_strategy="epoch",  
        save_strategy="epoch",  
        logging_strategy="epoch",   
        learning_rate=learning_rate,
        warmup_ratio=warmup_ratio,
        weight_decay=weight_decay,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        load_best_model_at_end=True,
        metric_for_best_model="auroc",
        greater_is_better=True,
        seed = 42,
        data_seed=42,
        max_grad_norm=1.0,  
        lr_scheduler_type="cosine"
        )
    
    early_stopping_callback = EarlyStoppingCallback(early_stopping_patience=early_stopping_patience)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        callbacks=[early_stopping_callback]  # Explicitly pass tokenizer
        )


    # Train model
    trainer.train()
    
    # Save the model and tokenizer
    model.save_pretrained(f"models/{new_folder_name}")
    tokenizer.save_pretrained(f"models/{new_folder_name}")

    gc.collect()
    torch.cuda.empty_cache()
    del model, tokenizer, train_dataset, val_dataset, trainer, training_args
    

def delete_folders(new_folder_name):
    results_dir = f"./results/{new_folder_name}"
    # delete all results folder to prevent memory clog
    if os.path.exists(results_dir):
        # os.chmod(results_dir , stat.S_IWRITE)
        shutil.rmtree(results_dir, ignore_errors=True)  # Deletes all files and subdirectories
        print(f"Deleted: {results_dir}")
    else:
        print(f"Directory does not exist: {results_dir}")



def stratified_train_test_split(df, stratified_col, test_size=None, random_state=42):
    """
    Splits a DataFrame into train and test sets using stratified sampling.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to split.
    stratified_col (str): The column used for stratification.
    test_size (float, optional): Proportion of the dataset to include in the test split.
    random_state (int, optional): Random seed for reproducibility.
    
    Returns:
    pd.DataFrame, pd.DataFrame: Train and test DataFrames.
    """
    if test_size is None:
        lowest_val_count = df[stratified_col].value_counts().min()
        
        if (lowest_val_count / 10) > 1:
            test_size = 0.1
        elif (lowest_val_count / 10) > (1/3):
            test_size = 0.3
            print("increasing test size to",test_size)
        else:
            test_size=1/lowest_val_count
            print("increasing test size to",test_size)
    
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    
    for train_idx, val_idx in splitter.split(df, df[stratified_col]):
        train_data = df.iloc[train_idx]
        val_data = df.iloc[val_idx]
    
    return train_data.reset_index(drop=True), val_data.reset_index(drop=True)



def finetune(df, model_name,folder_name,
             cluster_col_name=None, 
             text_col='text', label_col="label", learning_rate=1e-5,
             warmup_ratio=0.05, weight_decay=0.1,epochs=5, batch_size=8,
             label2id = {"Positive": 2, "Negative": 0, "Neutral": 1},
             early_stopping_patience=3, return_val_data=True):
    
    if cluster_col_name==None:
        train_data, val_data = train_test_split(df, test_size=0.1, random_state=42)
        cluster_no=0
        df_val_all=val_data
        finetune_individual(train_data, val_data, model_name,cluster_no,folder_name, text_col=text_col, label_col=label_col, label2id = label2id, learning_rate=learning_rate, warmup_ratio=warmup_ratio, weight_decay=weight_decay, epochs=epochs, batch_size=batch_size,early_stopping_patience=early_stopping_patience)
        gc.collect()
        torch.cuda.empty_cache()        

    else:
        df_val_all = pd.DataFrame()
        for i in tqdm_notebook(list(df[cluster_col_name].unique())):
            df_current=df[df[cluster_col_name]==i].reset_index(drop=True)
            list_of_labels=list(set(list(df_current[label_col])))


##############################################################################################################################################################################
            # making sure we have all labels here
            missing_keys = list(set(label2id.keys()) - set(list_of_labels))
            if missing_keys:
                print("Insufficient samples from a possible labels. Among those with insufficient samples, randomly selecting points from the entire dataset.")
                for j in missing_keys:
                    curr_label=df[df[label_col]==j].reset_index(drop=True)
                    sample_size = min(3, len(curr_label))
                    if sample_size>0:
                        to_sample=curr_label.sample(n=sample_size,random_state=42)
                        df_current=pd.concat([df_current,to_sample]).reset_index(drop=True)

            # making sure we have at least one label here
            labels_dict = df_current[label_col].value_counts().to_dict()
            keys_below_2 = [key for key, value in labels_dict.items() if value < 2]
            if len(keys_below_2)>0:
                print("Insufficient samples from a possible labels. Among those with insufficient samples, randomly selecting points from the entire dataset.")
                for k in keys_below_2:
                    curr_label=df[df[label_col]==k].reset_index(drop=True)
                    sample_size = min(3, len(curr_label))
                    if sample_size>0:
                        to_sample=curr_label.sample(n=sample_size,random_state=42)
                        df_current=pd.concat([df_current,to_sample]).reset_index(drop=True)
##############################################################################################################################################################################


            train_data, val_data = stratified_train_test_split(df_current, label_col)
            cluster_no=i
            finetune_individual(train_data, val_data, model_name,cluster_no,folder_name, text_col=text_col, label_col=label_col, label2id = label2id, learning_rate=learning_rate, warmup_ratio=warmup_ratio, weight_decay=weight_decay, epochs=epochs, batch_size=batch_size,early_stopping_patience=early_stopping_patience)
            df_val_all = pd.concat([df_val_all, val_data]).reset_index(drop=True)
            delete_folders(folder_name)
            gc.collect()
            torch.cuda.empty_cache()  
    if return_val_data==True:
        return(df_val_all)