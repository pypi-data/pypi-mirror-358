# nametrace: Human name detection and demographic prediction package.
# Copyright (C) 2025 Paul Bose

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Demographics prediction (gender and subregion) using character-level BiLSTM."""

from pathlib import Path
from typing import Dict, Optional, Tuple
import torch
import torch.nn as nn


class DemographicsBiLSTM(nn.Module):
    """BiLSTM model for joint gender and subregion prediction."""
    
    def __init__(self, vocab_size: int, num_genders: int, num_regions: int,
                 embed_dim: int = 64, hidden_dim: int = 128, 
                 num_layers: int = 2, dropout: float = 0.3):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim, num_layers=num_layers,
            bidirectional=True, batch_first=True, dropout=dropout
        )
        self.dropout = nn.Dropout(dropout)
        
        # Separate heads for gender and region prediction
        self.gender_classifier = nn.Linear(hidden_dim * 2, num_genders)
        self.region_classifier = nn.Linear(hidden_dim * 2, num_regions)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass."""
        # x shape: (batch_size, seq_len)
        embedded = self.embedding(x)  # (batch_size, seq_len, embed_dim)
        
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Use last hidden state (concatenate forward and backward)
        # hidden shape: (num_layers * 2, batch_size, hidden_dim)
        last_hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)  # (batch_size, hidden_dim * 2)
        
        features = self.dropout(last_hidden)
        
        # Predictions
        gender_logits = self.gender_classifier(features)  # (batch_size, num_genders)
        region_logits = self.region_classifier(features)  # (batch_size, num_regions)
        
        return gender_logits, region_logits


class DemographicsPredictor:
    """Predictor for gender and geographic subregion from names."""
    
    def __init__(self, device: str = 'cpu',
                 model_path: Optional[Path] = None):
        """
        Initialize demographics predictor.
        
        Args:
            device: Device for model inference
            model_path: Path to trained model file
        """
        self.device = device
        self.model_path = model_path or Path(__file__).parent / "demographics.pth"
        
        # Model components will be lazy loaded
        self._model = None
        self._char2idx = None
        self._gender2idx = None
        self._region2idx = None
        self._idx2gender = None
        self._idx2region = None
        self._max_len = 50
    
    def _load_model(self):
        """Lazy load the demographics model."""
        if not self.model_path.exists():
            return None, None, None, None, None, None
            
        try:
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            model = DemographicsBiLSTM(
                vocab_size=checkpoint['vocab_size'],
                num_genders=checkpoint['num_genders'],
                num_regions=checkpoint['num_regions'],
                embed_dim=checkpoint.get('embed_dim', 64),
                hidden_dim=checkpoint.get('hidden_dim', 128),
                num_layers=checkpoint.get('num_layers', 2),
                dropout=checkpoint.get('dropout', 0.3)
            )
            
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)
            model.eval()
            
            char2idx = checkpoint['char2idx']
            gender2idx = checkpoint['gender2idx']
            region2idx = checkpoint['region2idx']
            idx2gender = checkpoint['idx2gender']
            idx2region = checkpoint['idx2region']
            
            return model, char2idx, gender2idx, region2idx, idx2gender, idx2region
        except Exception as e:
            print(f"Warning: Could not load demographics model: {e}")
            return None, None, None, None, None, None
    
    def _encode_name(self, name: str) -> Optional[torch.Tensor]:
        """Encode name for model input."""
        if self._char2idx is None:
            return None
            
        name = name.lower()
        encoded = [self._char2idx.get('<START>', 0)]
        
        for char in name:
            encoded.append(self._char2idx.get(char, self._char2idx.get('<UNK>', 0)))
        
        encoded.append(self._char2idx.get('<END>', 0))
        
        # Pad or truncate
        if len(encoded) > self._max_len:
            encoded = encoded[:self._max_len]
        else:
            pad_idx = self._char2idx.get('<PAD>', 0)
            encoded.extend([pad_idx] * (self._max_len - len(encoded)))
        
        return torch.tensor(encoded, dtype=torch.long).unsqueeze(0).to(self.device)
    
    def predict_single(self, name: str, topk: Optional[int] = 1) -> Tuple[Optional[str], Optional[str], Dict[str, float]]:
        """
        Predict gender and subregion for a name.
        
        Args:
            name: Input name string
            topk: Number of top predictions to return (default: 1)
            
        Returns:
            If topk=1: Tuple of (gender, subregion, confidence_dict)
            If topk>1: Tuple of (gender_list, subregion_list, confidence_dict)
                where gender_list and subregion_list are lists of (prediction, confidence) tuples
        """
        # Lazy load model
        if self._model is None:
            (self._model, self._char2idx, self._gender2idx, 
             self._region2idx, self._idx2gender, self._idx2region) = self._load_model()
        
        # If model not available, return None
        if (self._model is None or self._char2idx is None or 
            self._idx2gender is None or self._idx2region is None):
            if topk == 1:
                return None, None, {'gender': 0.0, 'subregion': 0.0}
            else:
                return [], [], {'gender': 0.0, 'subregion': 0.0}
        
        # Encode name
        encoded = self._encode_name(name)
        if encoded is None:
            if topk == 1:
                return None, None, {'gender': 0.0, 'subregion': 0.0}
            else:
                return [], [], {'gender': 0.0, 'subregion': 0.0}
        
        # Predict
        with torch.no_grad():
            gender_logits, region_logits = self._model(encoded)
            
            # Convert to probabilities
            gender_probs = torch.softmax(gender_logits, dim=1)
            region_probs = torch.softmax(region_logits, dim=1)
            
            if topk == 1:
                # Get single best predictions
                gender_idx = torch.argmax(gender_probs, dim=1).item()
                region_idx = torch.argmax(region_probs, dim=1).item()
                
                gender = self._idx2gender.get(gender_idx)
                subregion = self._idx2region.get(region_idx)
                
                # Get confidence scores
                gender_conf = gender_probs[0, gender_idx].item()
                region_conf = region_probs[0, region_idx].item()
                
                return gender, subregion, {
                    'gender': gender_conf,
                    'subregion': region_conf
                }
            else:
                # Get top k predictions (separately for gender and region)
                k_gender = min(topk, len(self._idx2gender))
                k_region = min(topk, len(self._idx2region))
                
                gender_topk_probs, gender_topk_indices = torch.topk(gender_probs[0], k_gender)
                region_topk_probs, region_topk_indices = torch.topk(region_probs[0], k_region)
                
                # Build result lists
                gender_results = []
                for i in range(k_gender):
                    idx = gender_topk_indices[i].item()
                    prob = gender_topk_probs[i].item()
                    gender_name = self._idx2gender.get(idx)
                    if gender_name:
                        gender_results.append((gender_name, prob))
                
                region_results = []
                for i in range(k_region):
                    idx = region_topk_indices[i].item()
                    prob = region_topk_probs[i].item()
                    region_name = self._idx2region.get(idx)
                    if region_name:
                        region_results.append((region_name, prob))
                
                # Get confidence scores (best predictions)
                best_gender_conf = gender_results[0][1] if gender_results else 0.0
                best_region_conf = region_results[0][1] if region_results else 0.0
                
                return gender_results, region_results, {
                    'gender': best_gender_conf,
                    'subregion': best_region_conf
                }

    def _encode_names_batch(self, names: list[str]) -> Optional[torch.Tensor]:
        """Encode batch of names for model input."""
        if self._char2idx is None:
            return None
            
        batch_encoded = []
        for name in names:
            name = name.lower()
            encoded = [self._char2idx.get('<START>', 0)]
            
            for char in name:
                encoded.append(self._char2idx.get(char, self._char2idx.get('<UNK>', 0)))
            
            encoded.append(self._char2idx.get('<END>', 0))
            
            # Pad or truncate
            if len(encoded) > self._max_len:
                encoded = encoded[:self._max_len]
            else:
                pad_idx = self._char2idx.get('<PAD>', 0)
                encoded.extend([pad_idx] * (self._max_len - len(encoded)))
            
            batch_encoded.append(encoded)
        
        return torch.tensor(batch_encoded, dtype=torch.long).to(self.device)

    def predict_batch(self, names: list[str], topk: Optional[int] = 1) -> list[Tuple[Optional[str], Optional[str], Dict[str, float]]]:
        """
        Predict gender and subregion for a batch of names.
        
        Args:
            names: List of input name strings
            topk: Number of top predictions to return (default: 1)
            
        Returns:
            List of prediction results, same format as predict() for each name
        """
        if not names:
            return []
            
        # Lazy load model
        if self._model is None:
            (self._model, self._char2idx, self._gender2idx, 
             self._region2idx, self._idx2gender, self._idx2region) = self._load_model()
        
        # If model not available, return None/empty for each name
        if (self._model is None or self._char2idx is None or 
            self._idx2gender is None or self._idx2region is None):
            if topk == 1:
                return [(None, None, {'gender': 0.0, 'subregion': 0.0})] * len(names)
            else:
                return [([], [], {'gender': 0.0, 'subregion': 0.0})] * len(names)
        
        # Encode batch of names
        encoded_batch = self._encode_names_batch(names)
        if encoded_batch is None:
            if topk == 1:
                return [(None, None, {'gender': 0.0, 'subregion': 0.0})] * len(names)
            else:
                return [([], [], {'gender': 0.0, 'subregion': 0.0})] * len(names)
        
        # Predict for batch
        results = []
        with torch.no_grad():
            gender_logits, region_logits = self._model(encoded_batch)
            
            # Convert to probabilities
            gender_probs = torch.softmax(gender_logits, dim=1)  # (batch_size, num_genders)
            region_probs = torch.softmax(region_logits, dim=1)  # (batch_size, num_regions)
            
            # Process each item in batch
            for i in range(len(names)):
                if topk == 1:
                    # Get single best predictions
                    gender_idx = torch.argmax(gender_probs[i]).item()
                    region_idx = torch.argmax(region_probs[i]).item()
                    
                    gender = self._idx2gender.get(gender_idx)
                    subregion = self._idx2region.get(region_idx)
                    
                    # Get confidence scores
                    gender_conf = gender_probs[i, gender_idx].item()
                    region_conf = region_probs[i, region_idx].item()
                    
                    results.append((gender, subregion, {
                        'gender': gender_conf,
                        'subregion': region_conf
                    }))
                else:
                    # Get top k predictions (separately for gender and region)
                    k_gender = min(topk, len(self._idx2gender))
                    k_region = min(topk, len(self._idx2region))
                    
                    gender_topk_probs, gender_topk_indices = torch.topk(gender_probs[i], k_gender)
                    region_topk_probs, region_topk_indices = torch.topk(region_probs[i], k_region)
                    
                    # Build result lists
                    gender_results = []
                    for j in range(k_gender):
                        idx = gender_topk_indices[j].item()
                        prob = gender_topk_probs[j].item()
                        gender_name = self._idx2gender.get(idx)
                        if gender_name:
                            gender_results.append((gender_name, prob))
                    
                    region_results = []
                    for j in range(k_region):
                        idx = region_topk_indices[j].item()
                        prob = region_topk_probs[j].item()
                        region_name = self._idx2region.get(idx)
                        if region_name:
                            region_results.append((region_name, prob))
                    
                    # Get confidence scores (best predictions)
                    best_gender_conf = gender_results[0][1] if gender_results else 0.0
                    best_region_conf = region_results[0][1] if region_results else 0.0
                    
                    results.append((gender_results, region_results, {
                        'gender': best_gender_conf,
                        'subregion': best_region_conf
                    }))
        
        return results

    def predict(self, names, topk: Optional[int] = 1, batch_size: Optional[int] = None):
        """
        Unified predict function that handles both single names and batches.
        
        Args:
            names: Either a single name string or list of name strings
            topk: Number of top predictions to return (default: 1)
            batch_size: If provided and names is a list, process in chunks of this size
            
        Returns:
            If names is str: Same as predict_single()
            If names is list: List of prediction results (same as predict_batch())
        """
        # Handle single name
        if isinstance(names, str):
            return self.predict_single(names, topk=topk)
        
        # Handle list of names
        if not isinstance(names, list):
            raise ValueError("names must be either a string or list of strings")
        
        if not names:
            return []
        
        # If no batch_size specified, process all at once
        if batch_size is None:
            return self.predict_batch(names, topk=topk)
        
        # Process in chunks
        results = []
        for i in range(0, len(names), batch_size):
            batch = names[i:i + batch_size]
            batch_results = self.predict_batch(batch, topk=topk)
            results.extend(batch_results)
        
        return results
    
