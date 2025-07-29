import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import gc
from torch.utils.data import DataLoader, TensorDataset, Subset
import os
from tqdm.notebook import tqdm_notebook
import torch.nn.functional as F
import heapq
import math
import pandas as pd
from typing import Dict
from sklearn.metrics import f1_score


def souping(models_folder, save_path,num_labels=3, label2id={"Negative": 0, "Neutral": 1, "Positive": 2}):
    """
    Averages the weights of multiple fine-tuned models and saves the resulting model 
    (a "model soup").
    
    Args:
        models_folder (str): Path to the folder containing saved models.
        save_path (str): Path to save the averaged model.
        
    Returns:
        None
    """
    id2label = {v: k for k, v in label2id.items()}
    # Collect subdirectories for each fine-tuned model
    model_dirs = [
        os.path.join(models_folder, d)
        for d in os.listdir(models_folder)
        if os.path.isdir(os.path.join(models_folder, d))
    ]
    if not model_dirs:
        raise ValueError(f"No model directories found in {models_folder}")

    # Load the first model as a base
    base_model = AutoModelForSequenceClassification.from_pretrained(
        model_dirs[0], use_auth_token=False, num_labels=num_labels,
        label2id=label2id,id2label=id2label
    )
    base_state_dict = base_model.state_dict()

    # Initialize an accumulator for the parameter sum
    avg_state_dict = {
        k: torch.zeros_like(v) for k, v in base_state_dict.items()
    }

    # Number of models we are averaging
    num_models = len(model_dirs)

    # Sum up the weights of all models
    for model_dir in tqdm_notebook(model_dirs, desc="Loading & Summing Models"):
        model = AutoModelForSequenceClassification.from_pretrained(
            model_dir, use_auth_token=False, num_labels=num_labels,
            label2id=label2id,id2label=id2label
        )
        model_sd = model.state_dict()

        # Optional shape‐check (skip mismatched keys)
        for k in avg_state_dict.keys():
            if k not in model_sd:
                # Key missing in this model, skip
                continue
            if model_sd[k].shape != avg_state_dict[k].shape:
                # Shape mismatch, skip or handle differently
                print(f"Skipping {k} in {model_dir} due to shape mismatch.")
                continue
            
            avg_state_dict[k] += model_sd[k]

    # Divide by number of models to get the average
    for k in tqdm_notebook(avg_state_dict.keys(), desc="Averaging"):
        avg_state_dict[k] /= num_models

    # Load the averaged weights into the base model
    base_model.load_state_dict(avg_state_dict)

    # Use the tokenizer from the FIRST model (or the base checkpoint).
    # All models presumably share the same tokenizer if they started from the same checkpoint.
    tokenizer = AutoTokenizer.from_pretrained(
        model_dirs[0], use_auth_token=False
    )

    # Save the averaged model and tokenizer
    base_model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)

    print(f"Model soup saved to {save_path}")
    gc.collect()
    torch.cuda.empty_cache()


@torch.no_grad()
def greedy_souping(
    models_folder: str,
    save_path: str,
    df_val: pd.DataFrame,
    col_label: str,
    text_col: str,
    num_labels: int = 3,
    label2id: Dict[str, int] = {"Negative": 0, "Neutral": 1, "Positive": 2},
    batch_size: int = 1,
    device: str = "cuda",
    use_fp16: bool = True,          # ← new flag
):
    # ── set-up ───────────────────────────────────────────────────────────
    device  = device or ("cuda" if torch.cuda.is_available() else "cpu")
    fp16_ok = use_fp16 and device == "cuda"           # only meaningful on GPU
    id2label = {v: k for k, v in label2id.items()}

    model_dirs = sorted(
        d for d in (os.path.join(models_folder, x) for x in os.listdir(models_folder))
        if os.path.isdir(d)
    )
    if not model_dirs:
        raise ValueError(f"No checkpoint dirs found in {models_folder}")

    tokenizer = AutoTokenizer.from_pretrained(model_dirs[0])
    encodings = tokenizer(
        list(df_val[text_col]),
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt",
    )
    labels = torch.tensor(
        df_val[col_label].map(label2id).to_numpy()
        if df_val[col_label].dtype == "O"
        else df_val[col_label].to_numpy()
    )

    # ---------- helper: evaluation in AMP ----------
    def eval_f1(model) -> float:
        model.eval().to(device)
        preds = []
        for i in range(0, len(labels), batch_size):
            batch = {k: v[i:i+batch_size].to(device) for k, v in encodings.items()}
            with torch.cuda.amp.autocast(enabled=fp16_ok, dtype=torch.float16):
                logits = model(**batch).logits
            preds.extend(logits.argmax(-1).cpu().tolist())
        return f1_score(labels, preds, average="macro")

    # ---------- helper: loader in FP16 ----------
    def load_ckpt(path):
        return AutoModelForSequenceClassification.from_pretrained(
            path,
            num_labels=num_labels,
            label2id=label2id,
            id2label=id2label,
            torch_dtype=torch.float16 if fp16_ok else None,  # <─ FP16 here
        )

    # ── 1️⃣  score individual checkpoints ───────────────────────────────
    print("Scoring checkpoints on validation set …")
    scores = []
    for d in tqdm_notebook(model_dirs):
        m = load_ckpt(d)
        scores.append((eval_f1(m), d))
        del m; torch.cuda.empty_cache()
    scores.sort(key=lambda x: x[0], reverse=True)
    ordered_dirs = [d for _, d in scores]

    # ── 2️⃣  initialise soup with best checkpoint ────────────────────────
    soup_state = load_ckpt(ordered_dirs[0]).state_dict()
    soup_size, best_metric = 1, scores[0][0]
    print(f"Start soup with {ordered_dirs[0]}  (F1 = {best_metric:.4f})")

    def running_mean(curr_sd, new_sd, k):
        return {k_: curr_sd[k_] + (new_sd[k_] - curr_sd[k_]) / (k+1)
                if k_ in new_sd and curr_sd[k_].shape == new_sd[k_].shape
                else curr_sd[k_] for k_ in curr_sd}

    # ── 3️⃣  greedy-add remaining checkpoints ────────────────────────────
    for d in tqdm_notebook(ordered_dirs[1:]):
        cand_state = running_mean(soup_state, load_ckpt(d).state_dict(), soup_size)

        tmp_model = load_ckpt(ordered_dirs[0])
        tmp_model.load_state_dict(cand_state, strict=False)
        metric_val = eval_f1(tmp_model)
        del tmp_model; torch.cuda.empty_cache()

        if metric_val > best_metric:
            soup_state, best_metric, soup_size = cand_state, metric_val, soup_size+1
            print(f"kept   {d}   (F1 = {metric_val:.4f})")
        else:
            print(f"skipped {d}   (F1 = {metric_val:.4f})")

    # ── 4️⃣  save final soup ─────────────────────────────────────────────
    final_model = load_ckpt(ordered_dirs[0])
    final_model.load_state_dict(soup_state, strict=False)
    final_model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    print(f"\nGreedy soup ({soup_size} checkpoints) saved to {save_path}  |  dev F1 = {best_metric:.4f}")


def task_arithmetic(
    models_folder: str,
    save_path: str,
    pre_trained_model: str,
    num_labels: int = 3,
    label2id: dict = {"Negative": 0, "Neutral": 1, "Positive": 2},
    lambda_scale: float = 1.0,
    sum_task_vectors: bool = True
):
    """
    Perform task arithmetic over multiple fine-tuned models, 
    merging their 'task vectors' (θ_ft - θ_pre) into one model.

    Arguments:
      models_folder (str): folder containing fine-tuned model subdirectories.
      save_path (str): where to save the merged model.
      pre_trained_model (str): the path or identifier of the base pretrained model.
      num_labels (int): number of labels for classification.
      label2id (dict): label name -> label ID.
      lambda_scale (float): scaling factor (λ) to apply to the summed or averaged task vector.
      sum_task_vectors (bool): 
          - If True, we do θ_pre + (τ_1 + τ_2 + ... + τ_n) * λ
          - If False, we do θ_pre + (1/n) * (τ_1 + τ_2 + ... + τ_n) * λ
    """

    # Build reverse mapping
    id2label = {v: k for k, v in label2id.items()}

    # Find subdirectories containing fine-tuned models
    model_dirs = [
        os.path.join(models_folder, d)
        for d in os.listdir(models_folder)
        if os.path.isdir(os.path.join(models_folder, d))
    ]
    if not model_dirs:
        raise ValueError("No models found in models_folder.")

    # Load the *base* model
    base_model = AutoModelForSequenceClassification.from_pretrained(
        pre_trained_model,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
        use_auth_token=False
    )
    base_sd = base_model.state_dict()

    # Initialize combined task vector over ALL keys
    combined_task_vector = {
        k: torch.zeros_like(v) for k, v in base_sd.items()
    }

    # Summation of task vectors
    for model_dir in tqdm_notebook(model_dirs, desc="Summing task vectors"):
        ft_model = AutoModelForSequenceClassification.from_pretrained(
            model_dir, 
            num_labels=num_labels,
            use_auth_token=False
        )
        ft_sd = ft_model.state_dict()

        # Accumulate the difference for every key
        for k in base_sd.keys():
            # We assume shapes match. If not, you'd skip or handle accordingly.
            combined_task_vector[k] += (ft_sd[k] - base_sd[k])

    # Decide on summation vs. averaging
    if sum_task_vectors:
        # Summation: θ_pre + λ * Σ (θ_ft_i - θ_pre)
        pass  # combined_task_vector is already sum of all differences
    else:
        # Averaging: θ_pre + λ * (1/n) * Σ (θ_ft_i - θ_pre)
        for k in combined_task_vector.keys():
            combined_task_vector[k] /= len(model_dirs)

    # Merge into base
    merged_sd = {}
    for k in base_sd.keys():
        merged_sd[k] = base_sd[k] + lambda_scale * combined_task_vector[k]

    # Load back into the base model
    base_model.load_state_dict(merged_sd)

    # Save merged model and tokenizer
    os.makedirs(save_path, exist_ok=True)
    base_model.save_pretrained(save_path)
    tokenizer = AutoTokenizer.from_pretrained(pre_trained_model,use_auth_token=False)
    tokenizer.save_pretrained(save_path)

    print(f"Task Arithmetic merged model saved to {save_path}.")
    gc.collect()
    torch.cuda.empty_cache()




def ties(
    models_folder: str,
    save_path: str,
    base_model_name: str,
    num_labels: int = 3,
    label2id: dict = {"Negative": 0, "Neutral": 1, "Positive": 2},
    top_k: float = 20.0,
    lambda_scale: float = 1.0  # optional scaling factor λ
):
    """
    TIES merging method (Trim, Elect Sign, and Merge), implementing global top-k%
    trimming per task vector and optional scaling, as described in the TIES paper.

    Args:
        models_folder (str): Path containing fine-tuned models.
        save_path (str): Path to save merged model.
        base_model_name (str): Name or path of the original base model.
        num_labels (int): Number of labels for classification.
        label2id (dict): Label->ID mapping for classification.
        top_k (float): Percentage of largest magnitudes to retain per task (default=20).
        lambda_scale (float): Scaling factor λ for the final merged vector (default=1.0).
    """
    # Build reverse mapping
    id2label = {v: k for k, v in label2id.items()}

    # Gather all fine-tuned model directories in models_folder
    model_dirs = [
        os.path.join(models_folder, d)
        for d in os.listdir(models_folder)
        if os.path.isdir(os.path.join(models_folder, d))
    ]
    if not model_dirs:
        raise ValueError(f"No models found in {models_folder}.")

    # Load the base (pretrained) model + base state_dict
    base_model = AutoModelForSequenceClassification.from_pretrained(
        base_model_name,
        use_auth_token=False,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id
    )
    base_state_dict = base_model.state_dict()

    # 1) Compute each task vector (θ_ft - θ_base) for all models
    task_vectors = []
    for model_dir in tqdm_notebook(model_dirs, desc="Loading fine-tuned models"):
        tuned_model = AutoModelForSequenceClassification.from_pretrained(
            model_dir,
            use_auth_token=False,
            num_labels=num_labels,
            id2label=id2label,
            label2id=label2id
        )
        tuned_sd = tuned_model.state_dict()

        # Build the param-delta dict for this model
        task_vector = {
            k: (tuned_sd[k] - base_state_dict[k]).detach()  # detach to ensure no gradients
            for k in base_state_dict.keys()
        }
        task_vectors.append(task_vector)

    # 2) TIES Step 1: TRIM (global top-k% for each task vector)
    #    Instead of trimming per-parameter, we flatten all params for each task vector,
    #    determine the magnitude cutoff for top-k% globally, and then zero out everything below it.
    for i in tqdm_notebook(range(len(task_vectors)), desc="Global top-k% trimming"):
        # Concatenate absolute values of all params into a single vector
        all_abs_vals = []
        param_shapes = {}
        param_names = list(task_vectors[i].keys())  # consistent ordering

        for param_name in param_names:
            param_delta = task_vectors[i][param_name]
            param_shapes[param_name] = param_delta.shape
            # Flatten abs values on CPU
            all_abs_vals.append(param_delta.abs().view(-1).float().cpu())

        abs_vector = torch.cat(all_abs_vals, dim=0)
        numel = abs_vector.numel()

        if numel == 0:
            continue  # edge case if something has zero parameters

        # Calculate the cutoff index for top-k%
        keep_fraction = 1.0 - (top_k / 100.0)
        kth_index = int(math.ceil(numel * keep_fraction))

        # Make sure kth_index is in [1, numel]
        kth_index = max(1, min(kth_index, numel))

        # We want the "kth largest" threshold => do topk
        # We'll take top_count = numel - kth_index + 1
        top_count = numel - kth_index + 1
        val_topk, _ = torch.topk(abs_vector, top_count, largest=True)
        cutoff = val_topk[-1]  # smallest value within the top block

        # Zero out param deltas below cutoff
        for param_name in param_names:
            param_delta = task_vectors[i][param_name]
            mask = param_delta.abs() >= cutoff
            task_vectors[i][param_name] = param_delta * mask

    # 3) TIES Step 2 & 3: For each parameter p, Elect sign and Disjoint Merge
    merged_task_vector = {}
    for param_name in tqdm_notebook(base_state_dict.keys(), desc="Elect sign & merge"):
        # Stack all tasks' trimmed updates for this parameter
        param_stack = torch.stack([tv[param_name] for tv in task_vectors], dim=0)

        # Elect sign
        # sum of positive entries vs. sum of negative entries
        pos_mag = torch.sum(param_stack * (param_stack > 0), dim=0)
        neg_mag = torch.sum(-param_stack * (param_stack < 0), dim=0)
        elected_sign = torch.where(pos_mag >= neg_mag, 1.0, -1.0)

        # Disjoint Merge: only average deltas that share the elected sign
        consistent_mask = (param_stack.sign() == elected_sign.unsqueeze(0))
        valid_updates = param_stack * consistent_mask

        non_zero_counts = consistent_mask.sum(dim=0).clamp(min=1)
        merged_update = valid_updates.sum(dim=0) / non_zero_counts

        merged_task_vector[param_name] = merged_update

    # 4) Add the (optionally scaled) merged deltas back onto the base model
    merged_state_dict = {}
    for k, base_param in tqdm_notebook(base_state_dict.items(), desc="Final assembly"):
        merged_state_dict[k] = base_param + lambda_scale * merged_task_vector[k]

    # Load the merged state into the base model and save
    base_model.load_state_dict(merged_state_dict)
    base_model.save_pretrained(save_path)
    # Save tokenizer (assuming the same tokenizer for all)
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, use_auth_token=False)
    tokenizer.save_pretrained(save_path)

    print(f"TIES-merged model saved to {save_path}")
    gc.collect()
    torch.cuda.empty_cache()




def dare(
    models_folder: str,
    save_path: str,
    base_model_name: str,
    num_labels: int = 3,
    label2id: dict = {"Negative": 0, "Neutral": 1, "Positive": 2},
    p: float = 0.9,
    lambda_scale: float = 1.0,   # <-- single global λ
):
    """
    DARE merging with a single global scaling factor λ:
        θ_new = θ_pre + λ · Σ_i  DARE(θ_ft_i − θ_pre)

    Steps per model i
      1. Δ_i = θ_ft_i − θ_pre
      2. Randomly drop p % of entries, rescale survivors by 1/(1−p)
      3. Accumulate into Σ_i Δ̃_i
    """
    torch.manual_seed(42)

    id2label = {v: k for k, v in label2id.items()}

    # ----------------------------------------------------
    # 0) List fine-tuned model dirs
    # ----------------------------------------------------
    model_dirs = [
        os.path.join(models_folder, d)
        for d in os.listdir(models_folder)
        if os.path.isdir(os.path.join(models_folder, d))
    ]
    if not model_dirs:
        raise ValueError(f"No subdirectories found in {models_folder}")
    num_models = len(model_dirs)

    # ----------------------------------------------------
    # 1) Load the base model
    # ----------------------------------------------------
    base_model = AutoModelForSequenceClassification.from_pretrained(
        base_model_name,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
        use_auth_token=False,
    )
    base_sd = base_model.state_dict()

    # ----------------------------------------------------
    # 2) Prepare accumulator Σ_i Δ̃_i
    # ----------------------------------------------------
    merged_task_vector = {k: torch.zeros_like(v) for k, v in base_sd.items()}
    keep_fraction = 1.0 - p

    # ----------------------------------------------------
    # 3) Iterate over fine-tuned checkpoints
    # ----------------------------------------------------
    for model_dir in tqdm_notebook(model_dirs, desc="DARE (global λ)"):
        ft_sd = AutoModelForSequenceClassification.from_pretrained(
            model_dir,
            num_labels=num_labels,
            id2label=id2label,
            label2id=label2id,
            use_auth_token=False,
        ).state_dict()

        # --- compute & sparsify Δ_i ---
        with torch.no_grad():
            for k in base_sd.keys():
                delta = ft_sd[k] - base_sd[k]
                drop_mask = (torch.rand_like(delta) >= p).float()
                sparsified = (delta * drop_mask) / keep_fraction
                merged_task_vector[k] += sparsified  # accumulate

    # ----------------------------------------------------
    # 4) Add λ · Σ Δ̃_i back onto θ_pre
    # ----------------------------------------------------
    with torch.no_grad():
        for k in base_sd.keys():
            base_sd[k] += lambda_scale * merged_task_vector[k]

    # ----------------------------------------------------
    # 5) Save merged model + tokenizer
    # ----------------------------------------------------
    base_model.load_state_dict(base_sd)
    base_model.save_pretrained(save_path)
    AutoTokenizer.from_pretrained(base_model_name, use_auth_token=False).save_pretrained(save_path)
    print(f"DARE (global λ) model saved to {save_path}")

    gc.collect()
    torch.cuda.empty_cache()

#####################################################################################################################

# -------------------------------
# 1) DataLoader Initialization
# -------------------------------
def initialize_dataloader(
    df,
    text_col,
    label_col,
    model_name,
    label2id={"Negative": 0, "Neutral": 1, "Positive": 2},
    batch_size=6,
    max_length=512,
    shuffle=True
):
    """
    Initializes a DataLoader from a DataFrame, ensuring labels align with model's label2id mapping.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=False)

    texts = df[text_col].tolist()
    raw_labels = df[label_col].tolist()
    # Map labels using label2id
    labels = [label2id[label] for label in raw_labels]

    encodings = tokenizer(
        texts, 
        truncation=True, 
        padding=True, 
        max_length=max_length, 
        return_tensors="pt"
    )
    dataset = TensorDataset(
        encodings["input_ids"],
        encodings["attention_mask"],
        torch.tensor(labels, dtype=torch.long)
    )
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
    return dataloader


# -------------------------------
# 2) Corrected Diagonal Fisher
#    with ONE Forward Pass per Sample
# -------------------------------
def compute_diag_fisher(model, dataloader, device="cuda"):
    """
    Computes a diagonal Fisher Information matrix approximation using the 
    'model-based' approach:
    
       F(theta) = E_x [ sum_c p(c | x) * (grad_theta log p(c | x))^2 ].
       
    Implementation:
    - For each batch, iterate over samples individually.
    - For each sample, do a forward pass (shape [1, ...]).
    - Then for each class c, do backward() to get grad(log p(c|x)).
    - Multiply param.grad^2 by p(c|x) and accumulate.

    Doing one forward pass per sample avoids repeated backward() on the
    same graph, which can trigger the “graph freed” RuntimeError in PyTorch.
    """
    model.eval()
    
    # Create a Fisher accumulator, matching each parameter's shape
    fisher_dict = {
        n: torch.zeros_like(p, device=device) 
        for n, p in model.named_parameters()
        if p.requires_grad
    }

    total_samples = 0

    for batch in tqdm_notebook(dataloader, desc="Computing Fisher"):
        input_ids, attention_mask, _ = batch

        # Move the entire batch to device first for convenience
        input_ids = input_ids.to(device)
        attention_mask = attention_mask.to(device)
        
        # Iterate over each sample in the batch
        batch_size = input_ids.size(0)
        for i in range(batch_size):
            # Single-sample tensors
            input_ids_i = input_ids[i : i+1]
            attention_mask_i = attention_mask[i : i+1]

            # Forward pass for just this one sample
            outputs = model(input_ids=input_ids_i, attention_mask=attention_mask_i)
            logits = outputs.logits  # shape: (1, num_classes)

            log_probs = F.log_softmax(logits, dim=-1)  # shape: (1, num_classes)
            probs = log_probs.exp()                    # shape: (1, num_classes)
            
            num_classes = logits.size(1)
            # For each class c, accumulate grad^2 * p(c|x)
            for c in range(num_classes):
                model.zero_grad()
                # This single scalar log_probs[0, c]
                retain = (c < num_classes - 1)  # retain graph for all but the last class
                log_probs[0, c].backward(retain_graph=retain)

                p_c = probs[0, c].item()
                
                # Accumulate param.grad^2 * p(c|x_i)
                for name, param in model.named_parameters():
                    if param.grad is not None and name in fisher_dict:
                        fisher_dict[name] += (param.grad ** 2) * p_c

            total_samples += 1

    # Average over total samples
    for n in fisher_dict:
        fisher_dict[n] /= float(total_samples)

    return fisher_dict


def dataloaders_and_dirs(model_dirs, dataloaders):
    """
    Utility generator to pair each model directory with its corresponding DataLoader.
    """
    if len(dataloaders) != len(model_dirs):
        raise ValueError("Number of dataloaders does not match number of model directories.")
    for mdir, dl in zip(model_dirs, dataloaders):
        yield mdir, dl


# -------------------------------
# 3) Fisher Merging
# -------------------------------
def fisher_merging(
    models_folder,
    save_path,
    base_model_name,
    dataloaders,
    num_labels=3,  # Make sure this matches your label2id length
    label2id={"Negative":0, "Neutral":1, "Positive":2},
    sorted_folders=True,
    lambda_terms=None,
    device="cuda"
):
    """
    Fisher-weighted model merging, as in:
        theta^*(j) = sum_i [ lambda_i * F_i^j * theta_i^j ] / sum_i [ lambda_i * F_i^j ]

    For K fine-tuned models:
      1) Load each model's weights (theta_ft).
      2) Compute task_vector = (theta_ft - theta_base).
      3) Compute each model's diagonal Fisher (fisher_diag).
      4) Accumulate fisher_diag * task_vector for numerators,
         and fisher_diag for denominators (scaled by lambda_i).
      5) Weighted-avg each parameter dimension by fisher sum.
    """
    id2label = {v: k for k, v in label2id.items()}

    # Gather subdirectories for each fine-tuned model (sorted if needed)
    model_dirs = [
        os.path.join(models_folder, d)
        for d in os.listdir(models_folder)
        if os.path.isdir(os.path.join(models_folder, d))
    ]
    

    if not model_dirs:
        raise ValueError(f"No subdirectories found in {models_folder}.")
    num_models = len(model_dirs)
    if sorted_folders==True:
        model_dirs = sorted(model_dirs, key=lambda x: float(os.path.basename(x)))
        print("The model directory is:",model_dirs)
    # If no lambdas specified, default to uniform
    if lambda_terms is None:
        lambda_terms = [1.0 / num_models] * num_models
    elif len(lambda_terms) != num_models:
        raise ValueError(
            f"lambda_terms length ({len(lambda_terms)}) does not match number "
            f"of models found ({num_models})."
        )

    # 1) Load the base model
    base_model = AutoModelForSequenceClassification.from_pretrained(
        base_model_name,
        use_auth_token=False,
        num_labels=num_labels,
        label2id=label2id,
        id2label=id2label
    ).to(device)
    base_sd = base_model.state_dict()

    # 2) Prepare accumulators for Fisher-weighted numerators/denominators
    merged_numerators = {}
    merged_denominators = {}
    for k, v in base_sd.items():
        merged_numerators[k] = torch.zeros_like(v, device=device)
        merged_denominators[k] = torch.zeros_like(v, device=device)

    # 3) Loop over each fine-tuned model + corresponding dataloader
    for idx, (model_dir, dl) in tqdm_notebook(enumerate(dataloaders_and_dirs(model_dirs, dataloaders)), desc="Looping over each model"):
        lambda_i = lambda_terms[idx]

        # 3A) Load the fine-tuned model
        ft_model = AutoModelForSequenceClassification.from_pretrained(
            model_dir,
            use_auth_token=False,
            num_labels=num_labels,
            label2id=label2id,
            id2label=id2label
        ).to(device)
        ft_sd = ft_model.state_dict()

        # 3B) Compute task vector = (theta_ft - theta_base)
        task_vector = {}
        for k in tqdm_notebook(base_sd, desc="Compute task vector"):
            if k not in ft_sd:
                raise ValueError(f"Key {k} not found in model {model_dir}")
            if ft_sd[k].shape != base_sd[k].shape:
                raise ValueError(
                    f"Shape mismatch for {k}: base={base_sd[k].shape}, fine-tuned={ft_sd[k].shape}"
                )
            task_vector[k] = ft_sd[k].to(device) - base_sd[k].to(device)

        # 3C) Compute diagonal Fisher for this fine-tuned model
        fisher_diag = compute_diag_fisher(ft_model, dl, device=device)

        # 3D) Weighted accumulation
        for name in tqdm_notebook(base_sd, desc="Weighted accumulation"):
            if name in fisher_diag:
                merged_numerators[name] += lambda_i * fisher_diag[name] * task_vector[name]
                merged_denominators[name] += lambda_i * fisher_diag[name]

    # 4) Combine base parameters + Fisher-weighted average
    merged_state_dict = {}
    for k in tqdm_notebook(base_sd):
        merged_value = base_sd[k].clone().to(device)
        denom = merged_denominators[k]

        # If fisher denominator is zero => keep base parameter
        nonzero_mask = (denom != 0)
        if nonzero_mask.any():
            merged_value[nonzero_mask] += (
                merged_numerators[k][nonzero_mask] / denom[nonzero_mask]
            )

        merged_state_dict[k] = merged_value

    # 5) Load merged weights & save
    base_model.load_state_dict(merged_state_dict, strict=False)
    base_model.save_pretrained(save_path)

    # Save tokenizer from base
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, use_auth_token=False)
    tokenizer.save_pretrained(save_path)

    print(f"Fisher-merged model saved to {save_path}.")

    gc.collect()
    torch.cuda.empty_cache()


###############################################################################################

def compute_layer_inout(
    model,
    dataloader,
    device="cuda",
    max_batches=1000,
    float16=False,       # existing param: optional bfloat16
    use_autocast=False,  # new param: use autocast for forward pass
    cpu_matmul=False     # new param: do (X^T X) on CPU entirely
):
    """
    Gathers X^T X and X^T Y for each torch.nn.Linear module in 'model'.
    - The main forward pass can optionally use bfloat16 autocast (use_autocast=True).
    - If cpu_matmul=True, the dot products happen on CPU, so we do X.cpu() first.

    Returns a dict: layer_name -> {"xtx":..., "xty":..., "in_dim":..., "out_dim":...}
    """

    model.eval()
    model.to(device)

    if float16:
        # Convert entire model to bfloat16 (or half if you prefer).
        model.to(torch.bfloat16)

    layer_stats = {}

    # Gather references to each Linear module
    linear_modules = {}
    for name, module_ in model.named_modules():
        if isinstance(module_, torch.nn.Linear):
            linear_modules[name] = module_

    def make_hook(layer_name):
        def hook(m, inp, out):
            """
            We'll still cast hooking inputs to float32 before matmul,
            but if cpu_matmul=True, we'll do the entire matmul on CPU.
            """
            X = inp[0].detach().float()
            Y_raw = out.detach().float()

            # Flatten if 3D
            if X.dim() == 3:
                B, T, in_dim = X.shape
                X = X.view(B * T, in_dim)
            if Y_raw.dim() == 3:
                B, T, out_dim = Y_raw.shape
                Y_raw = Y_raw.view(B * T, out_dim)

            # Subtract bias
            if m.bias is not None:
                bias_ = m.bias.detach().float().view(1, -1)
                Y = Y_raw - bias_
            else:
                Y = Y_raw

            # Initialize if first time
            if layer_name not in layer_stats:
                in_dim = X.shape[1]
                out_dim = Y.shape[1]
                layer_stats[layer_name] = {
                    "xtx": torch.zeros(in_dim, in_dim),
                    "xty": torch.zeros(in_dim, out_dim),
                    "in_dim": in_dim,
                    "out_dim": out_dim
                }

            # Depending on cpu_matmul flag:
            if cpu_matmul:
                # Move X, Y to CPU first, do the entire matmul on CPU
                X_cpu = X.cpu()
                Y_cpu = Y.cpu()
                temp_xtx = (X_cpu.t() @ X_cpu)
                temp_xty = (X_cpu.t() @ Y_cpu)
            else:
                # Do it on GPU (in float32), then move result to CPU
                temp_xtx = (X.t() @ X).cpu()
                temp_xty = (X.t() @ Y).cpu()

            # Accumulate on CPU
            layer_stats[layer_name]["xtx"] += temp_xtx
            layer_stats[layer_name]["xty"] += temp_xty

        return hook

    # Register hooks
    hooks = []
    for name, mod in linear_modules.items():
        h = mod.register_forward_hook(make_hook(name))
        hooks.append(h)

    # Use inference_mode
    with torch.inference_mode():
        for batch_idx, batch in enumerate(tqdm_notebook(dataloader, desc="Collecting X/Y")):
            if batch_idx >= max_batches:
                break

            # Move inputs to GPU
            if isinstance(batch, (list, tuple)):
                input_ids, attention_mask, labels = batch
                inputs = {
                    "input_ids": input_ids.to(device),
                    "attention_mask": attention_mask.to(device),
                }
            else:
                inputs = {k: v.to(device) for k, v in batch.items()}

            # If we want autocast for forward pass
            if use_autocast:
                with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                    model(**inputs)
            else:
                model(**inputs)

    # Remove hooks
    for h in hooks:
        h.remove()

    return layer_stats


def regmean_merging(
    models_folder,
    save_path,
    base_model_name,
    dataloaders,
    num_labels=3,
    label2id=None,
    sorted_folders=True,
    max_batches=10000,
    float16=False,
    use_autocast=False,   # new
    cpu_matmul=False,     # new
    alpha=1.0,
    device="cuda"
):
    """
    RegMean merging with optional half/bfloat16 hooking to reduce VRAM usage.
    Additionally:
      - use_autocast: wrap forward pass in bfloat16 autocast (helpful for DeBERTa-large).
      - cpu_matmul: do matmul for hooking on CPU to save GPU memory even further.
    """
    if label2id is None:
        label2id = {"Negative": 0, "Neutral": 1, "Positive": 2}
    id2label = {v: k for k, v in label2id.items()}

    # Gather subdirs
    model_dirs = [
        os.path.join(models_folder, d)
        for d in os.listdir(models_folder)
        if os.path.isdir(os.path.join(models_folder, d))
    ]
    if not model_dirs:
        raise ValueError(f"No models found in {models_folder}")
    num_models = len(model_dirs)

    if sorted_folders:
        model_dirs = sorted(model_dirs, key=lambda x: float(os.path.basename(x)))
        print("Model subdirs (sorted):", model_dirs)

    if len(dataloaders) != num_models:
        raise ValueError("Number of DataLoaders != number of models")

    # 1) Load base model => template
    base_model = AutoModelForSequenceClassification.from_pretrained(
        base_model_name,
        use_auth_token=False,
        num_labels=num_labels,
        label2id=label2id,
        id2label=id2label
    ).to(device)
    base_sd = base_model.state_dict()

    # 2) Accumulate stats
    accumulated_stats = {}
    all_state_dicts = []

    for (model_dir, dl) in tqdm_notebook(zip(model_dirs, dataloaders), total=num_models, desc="RegMean Stage"):
        # Load fine-tuned
        ft_model = AutoModelForSequenceClassification.from_pretrained(
            model_dir,
            use_auth_token=False,
            num_labels=num_labels,
            label2id=label2id,
            id2label=id2label
        ).to(device)

        # 2A) collect stats with the new options
        layer_stats = compute_layer_inout(
            ft_model,
            dl,
            device=device,
            max_batches=max_batches,
            float16=float16,
            use_autocast=use_autocast,
            cpu_matmul=cpu_matmul
        )

        # 2B) accumulate them in CPU
        for layer_name, stat in layer_stats.items():
            if layer_name not in accumulated_stats:
                accumulated_stats[layer_name] = {
                    "xtx": stat["xtx"].clone(),
                    "xty": stat["xty"].clone(),
                    "in_dim": stat["in_dim"],
                    "out_dim": stat["out_dim"]
                }
            else:
                accumulated_stats[layer_name]["xtx"] += stat["xtx"]
                accumulated_stats[layer_name]["xty"] += stat["xty"]

        # Also gather final weights if needed
        all_state_dicts.append(ft_model.state_dict())

        # Cleanup
        del ft_model, layer_stats
        torch.cuda.empty_cache()
        gc.collect()

    # 3) Build merged state dict
    merged_state_dict = dict(base_sd)
    del base_sd
    def param_key_to_layer_name(k: str) -> str:
        if k.endswith(".weight"):
            return k.rsplit(".", 1)[0]
        return k

    # 4) Solve for each linear weight
    for k, base_param in merged_state_dict.items():
        if base_param.ndim == 2:
            layer_name = param_key_to_layer_name(k)
            if layer_name in accumulated_stats:
                in_dim = accumulated_stats[layer_name]["in_dim"]
                out_dim = accumulated_stats[layer_name]["out_dim"]
                if (base_param.shape[0] != out_dim) or (base_param.shape[1] != in_dim):
                    # fallback
                    arr = torch.stack([sd[k] for sd in all_state_dicts], dim=0).mean(dim=0)
                    merged_state_dict[k] = arr
                    continue

                xtx = accumulated_stats[layer_name]["xtx"].clone()
                xty = accumulated_stats[layer_name]["xty"].clone()

                # off-diagonal shrink
                if alpha < 1.0:
                    diag_part = torch.diag(torch.diag(xtx))
                    xtx = alpha * xtx + (1.0 - alpha) * diag_part

                try:
                    w_t = torch.linalg.solve(xtx, xty)  # (in_dim, out_dim) on CPU
                    merged_w = w_t.transpose(0, 1).contiguous()  # (out_dim, in_dim)
                    merged_state_dict[k] = merged_w
                except RuntimeError as e:
                    print(f"Warning: xtx not invertible for {layer_name}. Fall back to avg. {e}")
                    arr = torch.stack([sd[k] for sd in all_state_dicts], dim=0).mean(dim=0)
                    merged_state_dict[k] = arr
            else:
                # no stats => average
                arr = torch.stack([sd[k] for sd in all_state_dicts], dim=0).mean(dim=0)
                merged_state_dict[k] = arr
        else:
            # For bias, LN, embeddings => average
            arr = torch.stack([sd[k] for sd in all_state_dicts], dim=0).mean(dim=0)
            merged_state_dict[k] = arr

    # 5) Load & save
    base_model.load_state_dict(merged_state_dict, strict=False)
    base_model.save_pretrained(save_path)
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, use_auth_token=False)
    tokenizer.save_pretrained(save_path)

    print(f"RegMean-merged model saved to {save_path}. (alpha={alpha}, float16={float16}, use_autocast={use_autocast}, cpu_matmul={cpu_matmul})")
    gc.collect()
    torch.cuda.empty_cache()


