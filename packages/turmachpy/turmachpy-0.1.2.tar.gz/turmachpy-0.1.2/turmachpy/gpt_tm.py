'''
Read from the safetensors file itself to store on a tape. Note that to use this module you have to first download the model weights from huggingface.
You needn't pull the model and all the relevant configuration using GPT2LModelHead. Instead, only download the model.safetensors file from https://huggingface.co/openai-community/gpt2/blob/main/model.safetensors and save the file in the same directory.
'''
import tiktoken
import numpy as np
from safetensors import safe_open
import random

class tape_desc:

    def __init__(self, token_id, position):
        self.token_id = token_id
        self.position = position
        self.embedding = None
        self.layer_data = {}

class gpt_turing_machine:

    def __init__(self, model_path="model.safetensors"):
    
        self.tokenizer = tiktoken.get_encoding("gpt2")
        self.params = {}
        
        with safe_open(model_path, framework="np") as f:
            for key in f.keys():
                self.params[key] = f.get_tensor(key)

        self.n_heads = 12
        self.embed_dim = 768
        self.head_dim = self.embed_dim // self.n_heads

    def _compute_embeddings(self, tape):

        token_ids = np.array([cell.token_id for cell in tape])
        positions = np.array([cell.position for cell in tape])

        wte = self.params["wte.weight"][token_ids]
        wpe = self.params["wpe.weight"][positions]

        embeddings = wte + wpe
        for i, cell in enumerate(tape):
            cell.embedding = embeddings[i]

    def _layer_norm(self, x, gain, bias, eps=1e-5):

        mean = np.mean(x, axis=-1, keepdims=True)
        variance = np.var(x, axis=-1, keepdims=True)

        x = (x - mean) / np.sqrt(variance + eps)
        return gain * x + bias

    def _attention(self, tape, layer_idx):
        
        T = len(tape)
        X = np.stack([cell.embedding for cell in tape], axis=0)
        
        ln1_weight = self.params[f"h.{layer_idx}.ln_1.weight"]
        ln1_bias = self.params[f"h.{layer_idx}.ln_1.bias"]
        
        X_norm = self._layer_norm(X, ln1_weight, ln1_bias)

        weight = self.params[f"h.{layer_idx}.attn.c_attn.weight"] 
        bias = self.params[f"h.{layer_idx}.attn.c_attn.bias"]     

        qkv = X_norm @ weight + bias 
        q, k, v = np.split(qkv, 3, axis=-1)  

        q = q.reshape(T, self.n_heads, self.head_dim)
        k = k.reshape(T, self.n_heads, self.head_dim)
        v = v.reshape(T, self.n_heads, self.head_dim)

        attn_outputs = np.zeros((T, self.embed_dim))
        for head in range(self.n_heads):
            Q = q[:, head, :]  
            K = k[:, head, :]
            V = v[:, head, :]
            scores = Q @ K.T / np.sqrt(self.head_dim)

            mask = np.tril(np.ones((T, T), dtype=bool))
            scores = np.where(mask, scores, -np.inf)
            probs = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
            probs = probs / probs.sum(axis=-1, keepdims=True)

            attn = probs @ V
            attn_outputs[:, head*self.head_dim:(head+1)*self.head_dim] = attn

        weight_proj = self.params[f"h.{layer_idx}.attn.c_proj.weight"]
        bias_proj = self.params[f"h.{layer_idx}.attn.c_proj.bias"]    
        attn_proj = attn_outputs @ weight_proj + bias_proj

        for i, cell in enumerate(tape):
            cell.embedding = cell.embedding + attn_proj[i]

    def _feed_forward(self, tape, layer_idx):

        X = np.stack([cell.embedding for cell in tape], axis=0)

        ln2_weight = self.params[f"h.{layer_idx}.ln_2.weight"]
        ln2_bias = self.params[f"h.{layer_idx}.ln_2.bias"]

        X_norm = self._layer_norm(X, ln2_weight, ln2_bias)

        weight_fc = self.params[f"h.{layer_idx}.mlp.c_fc.weight"] 
        bias_fc = self.params[f"h.{layer_idx}.mlp.c_fc.bias"]     

        hidden = X_norm @ weight_fc + bias_fc
        hidden = 0.5 * hidden * (1 + np.tanh(np.sqrt(2/np.pi) * (hidden + 0.044715 * hidden**3)))

        weight_proj = self.params[f"h.{layer_idx}.mlp.c_proj.weight"]  
        bias_proj = self.params[f"h.{layer_idx}.mlp.c_proj.bias"]      
        hidden = hidden @ weight_proj + bias_proj 

        for i, cell in enumerate(tape):
            cell.embedding = cell.embedding + hidden[i]

    def _sample_top_k(self, logits, k=50):

        top_k_indices = np.argpartition(-logits, k)[:k]
        top_k_logits = logits[top_k_indices]

        probs = np.exp(top_k_logits - np.max(top_k_logits))
        probs = probs / probs.sum()

        next_token = np.random.choice(top_k_indices, p=probs)
        return next_token

    def generate(self, prompt, max_new_tokens, top_k=50):

        tokens = self.tokenizer.encode(prompt)
        tape = [tape_desc(token_id, pos) for pos, token_id in enumerate(tokens)]
        self._compute_embeddings(tape)

        for layer_idx in range(12):
            self._attention(tape, layer_idx)
            self._feed_forward(tape, layer_idx)

        for _ in range(max_new_tokens):

            final_embedding = tape[-1].embedding
            final_embedding = self._layer_norm(
                final_embedding,
                self.params["ln_f.weight"],
                self.params["ln_f.bias"]
            )

            wte = self.params["wte.weight"]
            logits = wte @ final_embedding 

            next_token = self._sample_top_k(logits, k=top_k)
            new_cell = tape_desc(next_token, len(tape))

            tape.append(new_cell)
            self._compute_embeddings([new_cell])

            for layer_idx in range(12):
                self._attention(tape, layer_idx)
                self._feed_forward([new_cell], layer_idx)
                
        return self.tokenizer.decode([cell.token_id for cell in tape])
