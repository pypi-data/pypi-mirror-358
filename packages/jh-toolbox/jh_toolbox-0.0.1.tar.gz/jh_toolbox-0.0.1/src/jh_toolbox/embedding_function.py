import chromadb
from chromadb.utils import embedding_functions
import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer
from pathlib import Path

class CustomONNXEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_path=None, tokenizer_path=None):
        """
        Initialize ONNX embedding function
        
        Args:
            model_path: Path to your .onnx model file
            tokenizer_path: Path to tokenizer (optional, defaults to model directory)
        """
        parent = Path(__file__).parent
        model_path = model_path or Path.joinpath(parent, r"data\model.onnx")
        tokenizer_path = tokenizer_path or Path.joinpath(parent, r"data")


        # Load ONNX model
        self.session = ort.InferenceSession(model_path)
        
        # Load tokenizer
        if tokenizer_path is None:
            # Assume tokenizer is in same directory as model
            import os
            tokenizer_path = os.path.dirname(model_path)
        
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    
    def __call__(self, texts):
        """Generate embeddings for input texts"""
        # Handle single string
        if isinstance(texts, str):
            texts = [texts]
        
        # Tokenize texts
        encoded = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="np",
            max_length=512
        )
        
        # Prepare inputs for ONNX model
        inputs = {
            'input_ids': encoded['input_ids'].astype(np.int64),
            'attention_mask': encoded['attention_mask'].astype(np.int64)
        }
        
        # Add token_type_ids if model expects it
        if 'token_type_ids' in encoded:
            inputs['token_type_ids'] = encoded['token_type_ids'].astype(np.int64)
        
        # Run ONNX inference
        outputs = self.session.run(None, inputs)
        
        # Extract embeddings (adjust based on your model output)
        # Most models output last_hidden_state as first output
        embeddings = outputs[0]
        
        # Apply mean pooling with attention mask
        attention_mask = encoded['attention_mask']
        attention_mask_expanded = np.expand_dims(attention_mask, -1)
        embeddings = embeddings * attention_mask_expanded
        embeddings = np.sum(embeddings, axis=1) / np.sum(attention_mask, axis=1, keepdims=True)
        
        # Normalize embeddings (optional but recommended)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return embeddings.tolist()
