"""
TST5: Minimal library for TimeST5 time series instruction model inference

TimeST5 is a hybrid model that combines PatchTST encoder for time series data
and T5 decoder for natural language generation. The model works in instruction mode:
you provide a time series and a text instruction, and get a natural language answer.
"""

import torch
import torch.nn as nn
from transformers import (
    T5Config,
    T5ForConditionalGeneration,
    T5Tokenizer,
    PatchTSTConfig,
    PatchTSTModel,
    PreTrainedModel
)
from transformers.modeling_outputs import BaseModelOutput, Seq2SeqLMOutput
import numpy as np
from pathlib import Path
import os
import json
from safetensors.torch import load_file
from huggingface_hub import snapshot_download
import re

__version__ = "0.1.0"


class TimeST5Config(T5Config):
    """
    Custom configuration class that combines T5 and PatchTST configurations.
    
    This configuration extends the standard T5Config with PatchTST-specific
    parameters and instruction-specific settings.
    """
    model_type = "timest5"

    def __init__(self, t5_config_name="google/flan-t5-small", patch_tst_config=None, **kwargs):
        # Initialize with base T5 configuration
        t5_conf = T5Config.from_pretrained(t5_config_name)
        super().__init__(**t5_conf.to_dict())
        
        # Set bos_token_id if not provided
        if self.bos_token_id is None:
            self.bos_token_id = t5_conf.eos_token_id

        # PatchTST encoder configuration
        self.patch_tst_config = patch_tst_config if patch_tst_config else PatchTSTConfig(
            num_input_channels=1,
            context_length=50,
            patch_length=4,
            stride=4,
            d_model=128
        ).to_dict()
        
        # End-of-time-series token ID (separator between time series and text)
        self.eots_token_id = 32099  # <extra_id_0>
        
        # Maximum instruction length limit
        self.max_instruction_length = 256
        
        self.update(kwargs)


class TimeSeriesAdapter(nn.Module):
    """
    Adaptation layer that transforms PatchTST embeddings to T5-compatible format.
    
    This module bridges the gap between PatchTST's time series representation
    and T5's text representation space, enabling seamless integration.
    """
    
    def __init__(self, patch_tst_dim, t5_dim, num_layers=1):
        """
        Initialize the adapter.
        
        Args:
            patch_tst_dim (int): PatchTST embedding dimension
            t5_dim (int): T5 model dimension
            num_layers (int): Number of adaptation layers (default: 1)
        """
        super().__init__()
        
        if num_layers == 1:
            # Simple linear projection for preserving temporal information
            self.projection = nn.Linear(patch_tst_dim, t5_dim)
        else:
            # Multi-layer projection for better transformation
            layers = []
            current_dim = patch_tst_dim
            
            # Intermediate layers with non-linearities
            for i in range(num_layers - 1):
                next_dim = patch_tst_dim + (t5_dim - patch_tst_dim) * (i + 1) // num_layers
                layers.extend([
                    nn.Linear(current_dim, next_dim),
                    nn.LayerNorm(next_dim),
                    nn.GELU(),
                    nn.Dropout(0.1)
                ])
                current_dim = next_dim
            
            # Final projection layer
            layers.append(nn.Linear(current_dim, t5_dim))
            self.projection = nn.Sequential(*layers)
        
    def forward(self, hidden_states):
        """
        Forward pass through the adapter.
        
        Args:
            hidden_states (torch.Tensor): PatchTST output tensor
                Shape: [batch_size, seq_len, patch_tst_dim] or [batch_size, 1, seq_len, patch_tst_dim]
        
        Returns:
            torch.Tensor: T5-compatible tensor [batch_size, seq_len, t5_dim]
        """
        original_shape = hidden_states.shape
        
        # Handle 4D tensor by removing dimension of size 1
        if hidden_states.dim() == 4 and hidden_states.shape[1] == 1:
            hidden_states = hidden_states.squeeze(1)
        
        # Validate tensor dimensions
        if hidden_states.dim() != 3:
            raise ValueError(
                f"Expected 3D tensor [batch, seq, dim], got: {hidden_states.shape} "
                f"(original: {original_shape})"
            )
        
        # Project to T5 dimension space
        projected = self.projection(hidden_states)
        return projected


class TimeST5Model(T5ForConditionalGeneration):
    """
    Hybrid model combining PatchTST encoder, T5 encoder, and T5 decoder.
    
    This model operates in instruction mode: past_values + input_ids -> answer.
    The architecture consists of:
    1. PatchTST encoder for time series processing
    2. TimeSeriesAdapter for dimension alignment
    3. T5 encoder for text instruction processing
    4. T5 decoder for answer generation
    """
    config_class = TimeST5Config

    def __init__(self, config: TimeST5Config):
        """
        Initialize the TimeST5 model.
        
        Args:
            config (TimeST5Config): Model configuration
        """
        super().__init__(config)
        
        # Initialize PatchTST encoder for time series
        patch_tst_conf = PatchTSTConfig(**config.patch_tst_config)
        self.time_series_encoder = PatchTSTModel(patch_tst_conf)
        
        # Initialize adaptation layer for T5 compatibility
        self.ts_adapter = TimeSeriesAdapter(
            patch_tst_dim=patch_tst_conf.d_model,
            t5_dim=config.d_model,
            num_layers=1  # Simple projection for preserving temporal information
        )

    def _encode_time_series(self, past_values, **kwargs):
        """
        Internal method for encoding time series data.
        
        Args:
            past_values (torch.Tensor): Time series data
                Shape: [batch_size, seq_len, num_channels] or [batch_size, num_channels, seq_len]
        
        Returns:
            torch.Tensor: Adapted embeddings [batch_size, num_patches, d_model]
        """
        # Validate and correct input dimensions
        if past_values.dim() == 3:
            if past_values.shape[1] == 1:  # [batch, 1, seq_len] -> [batch, seq_len, 1]
                past_values = past_values.transpose(1, 2)
            elif past_values.shape[2] == 1:  # Already correct format [batch, seq_len, 1]
                pass
            else:
                raise ValueError(f"Unexpected past_values shape: {past_values.shape}")
        
        # Encode time series through PatchTST
        ts_outputs = self.time_series_encoder(
            past_values=past_values,
            return_dict=True,
            **kwargs
        )
        
        # Adapt embeddings for T5 compatibility
        adapted_hidden_states = self.ts_adapter(ts_outputs.last_hidden_state)
        return adapted_hidden_states

    def encode_instruct_input(self, past_values, input_ids, attention_mask=None, **kwargs):
        """
        Encode time series + text instruction into unified representation.
        
        Format: [timeseries_patches] + [<extra_id_0>] + [instruction_text]
        
        Args:
            past_values (torch.Tensor): Time series data
            input_ids (torch.Tensor): Text instruction tokens [batch_size, text_len]
            attention_mask (torch.Tensor, optional): Attention mask for text
        
        Returns:
            tuple: (BaseModelOutput with combined embeddings, combined_attention_mask)
        """
        batch_size = past_values.shape[0]
        device = past_values.device
        
        # Encode time series
        ts_embeddings = self._encode_time_series(past_values, **kwargs)
        
        # Limit instruction length
        if input_ids.shape[1] > self.config.max_instruction_length:
            input_ids = input_ids[:, :self.config.max_instruction_length]
            if attention_mask is not None:
                attention_mask = attention_mask[:, :self.config.max_instruction_length]
        
        # Encode text instruction through T5 encoder
        text_outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        text_embeddings = text_outputs.last_hidden_state
        
        # Create end-of-time-series token embedding
        eots_token_ids = torch.full((batch_size, 1), self.config.eots_token_id, device=device)
        eots_embeddings = self.shared(eots_token_ids)
        
        # Concatenate: [timeseries] + [<EOTS>] + [text]
        combined_embeddings = torch.cat([
            ts_embeddings,      # [batch, num_patches, d_model]
            eots_embeddings,    # [batch, 1, d_model]  
            text_embeddings     # [batch, text_len, d_model]
        ], dim=1)
        
        # Create combined attention mask
        ts_mask = torch.ones(batch_size, ts_embeddings.shape[1], device=device)
        eots_mask = torch.ones(batch_size, 1, device=device)
        
        if attention_mask is None:
            text_mask = torch.ones(batch_size, text_embeddings.shape[1], device=device)
        else:
            text_mask = attention_mask.float()
            
        combined_attention_mask = torch.cat([ts_mask, eots_mask, text_mask], dim=1)
        
        return BaseModelOutput(
            last_hidden_state=combined_embeddings,
            hidden_states=None,
            attentions=None
        ), combined_attention_mask

    def generate(self, past_values, input_ids, attention_mask=None, **kwargs):
        """
        Generate text based on time series and instruction.
        
        Args:
            past_values (torch.Tensor): Time series data (required)
            input_ids (torch.Tensor): Instruction tokens (required)
            attention_mask (torch.Tensor, optional): Attention mask
            **kwargs: Additional generation parameters
        
        Returns:
            torch.Tensor: Generated token IDs
        """
        if past_values is None:
            raise ValueError("past_values is required for generation")
        if input_ids is None:
            raise ValueError("input_ids is required for instruction mode")
            
        # Encode input data
        encoder_outputs, combined_attention_mask = self.encode_instruct_input(
            past_values, input_ids, attention_mask
        )
        kwargs['encoder_outputs'] = encoder_outputs
        kwargs['attention_mask'] = combined_attention_mask
            
        # Call standard T5 generation
        return super().generate(**kwargs)


class TimeST5:
    """
    Simple interface for using TimeST5 model inference.
    
    This class provides a user-friendly API for loading and using
    pre-trained TimeST5 models for time series instruction tasks.
    """
    
    def __init__(self, model_path, device="auto"):
        """
        Initialize TimeST5 interface.
        
        Args:
            model_path (str): Path to model directory
            device (str): Device specification ("auto", "cuda", "cpu")
        """
        self.device = self._get_device(device)
        self.model_path = Path(model_path)
        
        # Load tokenizer from model directory or default
        if (self.model_path / "tokenizer_config.json").exists():
            print(f"Loading tokenizer from {self.model_path}")
            self.tokenizer = T5Tokenizer.from_pretrained(str(self.model_path))
        else:
            print("Using default flan-t5-small tokenizer")
            self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
        
        # Load and initialize model
        self.model = self._load_model()
        self.model.to(self.device)
        self.model.eval()
        
    def _get_device(self, device):
        """Determine the appropriate device for model execution."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    @staticmethod
    def _is_hf_hub_id(model_path_or_id):
        """
        Determine if the given string is a Hugging Face Hub model ID or local path.
        
        Args:
            model_path_or_id (str): Model path or Hub ID
            
        Returns:
            bool: True if it's a Hub ID, False if it's a local path
        """
        # If it's an absolute path, it's definitely local
        if os.path.isabs(model_path_or_id):
            return False
            
        # If it exists as a directory, it's local
        if os.path.exists(model_path_or_id):
            return False
            
        # Check if it matches Hub ID pattern (username/model-name)
        # Hub ID pattern: contains at least one '/' and looks like repo format
        if '/' in model_path_or_id:
            # Split by '/' and check if it looks like a valid Hub ID
            parts = model_path_or_id.split('/')
            if len(parts) >= 2:
                # Basic validation: no empty parts, reasonable characters
                username, repo_name = parts[0], '/'.join(parts[1:])
                if username and repo_name:
                    # Check for reasonable characters (alphanumeric, hyphens, underscores)
                    username_valid = re.match(r'^[a-zA-Z0-9][\w\-\.]*$', username)
                    repo_valid = re.match(r'^[a-zA-Z0-9][\w\-\.]*$', repo_name.replace('/', '-'))
                    if username_valid and repo_valid:
                        return True
        
        # Default to local path
        return False
    
    @staticmethod
    def _download_from_hf(model_id, cache_dir=None, token=None):
        """
        Download model from Hugging Face Hub.
        
        Args:
            model_id (str): Hub model ID (e.g., "username/model-name")
            cache_dir (str, optional): Custom cache directory
            token (str, optional): HF token for private repos
            
        Returns:
            str: Path to downloaded model directory
        """
        try:
            print(f"Downloading model '{model_id}' from Hugging Face Hub...")
            local_dir = snapshot_download(
                repo_id=model_id,
                cache_dir=cache_dir,
                token=token,
                repo_type="model"
            )
            print(f"Model downloaded to: {local_dir}")
            return local_dir
        except Exception as e:
            raise RuntimeError(f"Failed to download model '{model_id}' from HF Hub: {e}")
    
    def _load_model(self):
        """Load model from checkpoint files."""
        # Load configuration
        config_path = self.model_path / "config.json"
        if config_path.exists():
            # Load configuration directly from JSON file
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # Create TimeST5Config from dictionary
            config = TimeST5Config(
                t5_config_name="google/flan-t5-small",
                patch_tst_config=config_dict.get("patch_tst_config", {
                    "num_input_channels": 1,
                    "context_length": 50,
                    "patch_length": 4,
                    "stride": 4,
                    "d_model": 128
                }),
                **{k: v for k, v in config_dict.items() 
                   if k not in ['patch_tst_config', 'model_type', 'architectures']}
            )
            print(f"Loaded configuration: patch_length={config.patch_tst_config['patch_length']}, "
                  f"d_model={config.d_model}")
        else:
            # Default configuration
            config = TimeST5Config(
                t5_config_name="google/flan-t5-small",
                patch_tst_config={
                    "num_input_channels": 1,
                    "context_length": 50,
                    "patch_length": 4,
                    "stride": 4,
                    "d_model": 128
                }
            )
            print("Using default configuration")
        
        # Create model instance
        model = TimeST5Model(config)
        
        # Load model weights
        weights_path = self.model_path / "model.safetensors"
        if weights_path.exists():
            print(f"Loading weights from safetensors: {weights_path}")
            state_dict = load_file(str(weights_path), device=str(self.device))
            
            # Fix mapping for shared embeddings in T5
            if "shared.weight" in state_dict:
                # T5 uses shared embeddings for encoder and decoder
                if "encoder.embed_tokens.weight" not in state_dict:
                    state_dict["encoder.embed_tokens.weight"] = state_dict["shared.weight"]
                if "decoder.embed_tokens.weight" not in state_dict:  
                    state_dict["decoder.embed_tokens.weight"] = state_dict["shared.weight"]
                print("Mapped shared embeddings for encoder/decoder")
            
            # Analyze weights for critical components
            patch_tst_keys = [k for k in state_dict.keys() if 'time_series_encoder' in k]
            adapter_keys = [k for k in state_dict.keys() if 'ts_adapter' in k]
            
            print(f"Weight analysis:")
            print(f"   PatchTST encoder: {len(patch_tst_keys)} keys found")
            print(f"   Adapter: {len(adapter_keys)} keys found")
            
            if patch_tst_keys:
                print(f"   PatchTST will be loaded from checkpoint "
                      f"(sample keys: {patch_tst_keys[:3]})")
            else:
                print(f"   WARNING: PatchTST NOT FOUND in checkpoint - will use random initialization!")
                
            if adapter_keys:
                print(f"   Adapter will be loaded from checkpoint (keys: {adapter_keys})")
            else:
                print(f"   WARNING: Adapter NOT FOUND in checkpoint - will use random initialization!")
            
            # Load with missing key tolerance
            missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
            
            # Check for critical missing components
            critical_missing = [k for k in missing_keys 
                              if 'time_series_encoder' in k or 'ts_adapter' in k]
            
            if critical_missing:
                print(f"CRITICAL: Missing keys for PatchTST/Adapter:")
                for key in critical_missing[:10]:
                    print(f"   Missing: {key}")
                print(f"This means PatchTST/Adapter will be randomly initialized!")
            else:
                print(f"All critical components (PatchTST + Adapter) loaded from checkpoint!")
            
            if missing_keys:
                non_critical_missing = [k for k in missing_keys 
                                      if 'time_series_encoder' not in k and 'ts_adapter' not in k]
                if non_critical_missing:
                    print(f"Non-critical missing keys: {len(non_critical_missing)}")
                    print(f"   Sample: {non_critical_missing[:5]}")
            
            if unexpected_keys:
                print(f"Unexpected keys: {len(unexpected_keys)}")
                print(f"   Sample: {unexpected_keys[:5]}")
        else:
            # Try pytorch_model.bin as fallback
            weights_path = self.model_path / "pytorch_model.bin"
            if weights_path.exists():
                print(f"Loading weights from pytorch_model.bin: {weights_path}")
                state_dict = torch.load(weights_path, map_location=self.device, weights_only=False)
                
                # Apply same embedding fix and loading logic as above
                if "shared.weight" in state_dict:
                    if "encoder.embed_tokens.weight" not in state_dict:
                        state_dict["encoder.embed_tokens.weight"] = state_dict["shared.weight"]
                    if "decoder.embed_tokens.weight" not in state_dict:  
                        state_dict["decoder.embed_tokens.weight"] = state_dict["shared.weight"]
                    print("Mapped shared embeddings for encoder/decoder")
                
                missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
                
                if missing_keys:
                    print(f"Missing keys: {len(missing_keys)}")
                if unexpected_keys:
                    print(f"Unexpected keys: {len(unexpected_keys)}")
            else:
                raise FileNotFoundError(f"Model weights not found in {self.model_path}")
            
        return model
    
    @classmethod
    def from_pretrained(cls, model_path_or_id, device="auto", cache_dir=None, token=None):
        """
        Create TimeST5 instance from pre-trained model.
        
        Supports loading from:
        - Local directory path
        - Hugging Face Hub model ID (e.g., "username/model-name")
        
        Args:
            model_path_or_id (str): Local path or HF Hub model ID
            device (str): Device specification ("auto", "cuda", "cpu")
            cache_dir (str, optional): Custom cache directory for HF Hub downloads
            token (str, optional): HF token for accessing private repositories
            
        Returns:
            TimeST5: Ready-to-use model instance
            
        Examples:
            # Load from local path
            model = TimeST5.from_pretrained("./local_model")
            
            # Load from HF Hub
            model = TimeST5.from_pretrained("username/timest5-model")
            
            # Load private model from HF Hub
            model = TimeST5.from_pretrained("username/private-model", token="hf_xxx")
        """
        if cls._is_hf_hub_id(model_path_or_id):
            # Download from Hugging Face Hub
            local_model_path = cls._download_from_hf(
                model_id=model_path_or_id,
                cache_dir=cache_dir,
                token=token
            )
            return cls(local_model_path, device)
        else:
            # Use local path
            return cls(model_path_or_id, device)
    
    def predict(self, time_series, instruction, max_input_length=256, max_output_length=512, num_beams=4):
        """
        Main function for model inference.
        
        Args:
            time_series: Time series data (numpy array, list, or torch tensor)
            instruction (str): Text instruction/question
            max_input_length (int): Maximum input sequence length
            max_output_length (int): Maximum output sequence length  
            num_beams (int): Number of beams for beam search
            
        Returns:
            str: Model's answer
        """
        # Convert time series to tensor
        if isinstance(time_series, (list, np.ndarray)):
            time_series = torch.tensor(time_series, dtype=torch.float32)
        
        # Auto-interpolate to 50 points if needed
        if isinstance(time_series, torch.Tensor):
            if time_series.dim() == 1:
                seq_len = time_series.shape[0]
            elif time_series.dim() == 2:
                seq_len = time_series.shape[0] if time_series.shape[1] == 1 else time_series.shape[1]
            else:
                seq_len = time_series.shape[1]  # Assume [batch, seq, channels]
        else:
            # For other types, try to get length
            seq_len = len(time_series)
        
        # Interpolate to exactly 50 points if needed
        if seq_len != 50:
            print(f"⚠️  WARNING: Auto-interpolating time series from {seq_len} to 50 points")
            print(f"    This may affect pattern recognition accuracy for very short/long series")
            # Convert to 1D for interpolation
            if time_series.dim() == 1:
                values = time_series
            elif time_series.dim() == 2:
                values = time_series.squeeze()
            else:
                values = time_series.squeeze()
            
            # Interpolate using numpy linear interpolation
            old_indices = np.linspace(0, 1, seq_len)
            new_indices = np.linspace(0, 1, 50)
            values_np = values.cpu().numpy() if isinstance(values, torch.Tensor) else np.array(values)
            interpolated_values = np.interp(new_indices, old_indices, values_np)
            time_series = torch.tensor(interpolated_values, dtype=torch.float32)
        
        # Normalize dimensions
        if time_series.dim() == 1:
            time_series = time_series.unsqueeze(0).unsqueeze(-1)  # [1, seq_len, 1]
        elif time_series.dim() == 2:
            if time_series.shape[0] == 1:  # [1, seq_len]
                time_series = time_series.unsqueeze(-1)  # [1, seq_len, 1]
            else:  # [seq_len, channels]
                time_series = time_series.unsqueeze(0)  # [1, seq_len, channels]
        
        time_series = time_series.to(self.device)
        
        # Tokenize instruction
        inputs = self.tokenizer(
            instruction,
            max_length=max_input_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)
        
        # Generate answer
        with torch.no_grad():
            generated_ids = self.model.generate(
                past_values=time_series,
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=max_output_length,
                num_beams=num_beams,
                early_stopping=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                do_sample=False
            )
        
        # Decode answer
        answer = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        return answer


# Public API exports
__all__ = ['TimeST5', 'TimeST5Model', 'TimeST5Config', 'TimeSeriesAdapter'] 