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

"""Human name detection using rule-based lookup and BiLSTM model."""

from pathlib import Path
from typing import Optional, Set, Tuple
import torch
import torch.nn as nn
from nameparser import HumanName


class BiLSTMClassifier(nn.Module):
    """BiLSTM model for binary classification."""
    
    def __init__(self, vocab_size: int, embed_dim: int = 64, hidden_dim: int = 128, 
                 num_layers: int = 2, dropout: float = 0.3):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim, hidden_dim, num_layers=num_layers,
            bidirectional=True, batch_first=True, dropout=dropout
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim * 2, 2)  # Binary classification
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        # x shape: (batch_size, seq_len)
        embedded = self.embedding(x)  # (batch_size, seq_len, embed_dim)
        
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Use last hidden state (concatenate forward and backward)
        # hidden shape: (num_layers * 2, batch_size, hidden_dim)
        last_hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)  # (batch_size, hidden_dim * 2)
        
        output = self.dropout(last_hidden)
        logits = self.classifier(output)  # (batch_size, 2)
        
        return logits


class HumanNameDetector:
    """Detector for human names using rule-based lookup + BiLSTM fallback."""
    
    def __init__(self, known_names: Set[str], device: str = 'cpu', 
                 model_path: Optional[Path] = None):
        """
        Initialize human name detector.
        
        Args:
            known_names: Set of known human first names (lowercase)
            device: Device for model inference
            model_path: Path to trained model file
        """
        self.known_names = known_names
        self.device = device
        self.model_path = model_path or Path(__file__).parent / "human_detector.pth"
        
        # Model will be lazy loaded
        self._model = None
        self._char2idx = None
        self._max_len = 50
    
    def _extract_first_name(self, full_name: str) -> str:
        """Extract first name using nameparser."""
        try:
            parsed = HumanName(full_name)
            return parsed.first.lower() if parsed.first else full_name.split()[0].lower()
        except:
            # Fallback to first word
            return full_name.split()[0].lower() if full_name.split() else ""
    
    def _load_model(self):
        """Lazy load the BiLSTM model."""
        if not self.model_path.exists():
            # Return None if model not trained yet
            return None, None
            
        try:
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            model = BiLSTMClassifier(
                vocab_size=checkpoint['vocab_size'],
                embed_dim=checkpoint.get('embed_dim', 64),
                hidden_dim=checkpoint.get('hidden_dim', 128),
                num_layers=checkpoint.get('num_layers', 2),
                dropout=checkpoint.get('dropout', 0.3)
            )
            
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)
            model.eval()
            
            char2idx = checkpoint['char2idx']
            
            return model, char2idx
        except Exception as e:
            print(f"Warning: Could not load human detector model: {e}")
            return None, None
    
    def _encode_name(self, name: str) -> torch.Tensor:
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
    
    def predict_single(self, full_name: str) -> Tuple[bool, float]:
        """
        Predict if name is human.
        
        Args:
            full_name: Full name string
            
        Returns:
            Tuple of (is_human, confidence)
        """
        # Extract first name
        first_name = self._extract_first_name(full_name)
        
        if not first_name:
            return False, 0.0
        
        # Check in known names first
        if first_name in self.known_names:
            return True, 1.0
        
        # Use model for unknown names
        if self._model is None:
            self._model, self._char2idx = self._load_model()
        
        # If model not available, return False for unknown names
        if self._model is None or self._char2idx is None:
            return False, 0.0
        
        # Encode and predict
        encoded = self._encode_name(first_name)
        if encoded is None:
            return False, 0.0
        
        with torch.no_grad():
            logits = self._model(encoded)
            probabilities = torch.softmax(logits, dim=1)
            human_prob = probabilities[0, 1].item()  # Probability of being human
            
            is_human = human_prob > 0.5
            confidence = max(human_prob, 1 - human_prob)
            
            return is_human, confidence

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

    def predict_batch(self, full_names: list[str]) -> list[Tuple[bool, float]]:
        """
        Predict if names are human for a batch of names.
        
        Args:
            full_names: List of full name strings
            
        Returns:
            List of (is_human, confidence) tuples
        """
        if not full_names:
            return []
        
        results = []
        
        # Extract first names and check known names
        first_names = []
        known_results = {}
        
        for i, full_name in enumerate(full_names):
            first_name = self._extract_first_name(full_name)
            first_names.append(first_name)
            
            if not first_name:
                results.append((False, 0.0))
                known_results[i] = True
            elif first_name in self.known_names:
                results.append((True, 1.0))
                known_results[i] = True
            else:
                results.append(None)  # Placeholder for model prediction
                known_results[i] = False
        
        # Get indices of names that need model prediction
        unknown_indices = [i for i in range(len(full_names)) if not known_results[i]]
        
        if unknown_indices:
            # Load model if needed
            if self._model is None:
                self._model, self._char2idx = self._load_model()
            
            # If model available, predict for unknown names
            if self._model is not None and self._char2idx is not None:
                unknown_first_names = [first_names[i] for i in unknown_indices]
                
                # Encode batch
                encoded_batch = self._encode_names_batch(unknown_first_names)
                
                if encoded_batch is not None:
                    with torch.no_grad():
                        logits = self._model(encoded_batch)
                        probabilities = torch.softmax(logits, dim=1)
                        
                        # Process each prediction
                        for j, batch_idx in enumerate(unknown_indices):
                            human_prob = probabilities[j, 1].item()
                            is_human = human_prob > 0.5
                            confidence = max(human_prob, 1 - human_prob)
                            results[batch_idx] = (is_human, confidence)
                else:
                    # Couldn't encode, mark as not human
                    for batch_idx in unknown_indices:
                        results[batch_idx] = (False, 0.0)
            else:
                # Model not available, mark unknown names as not human
                for batch_idx in unknown_indices:
                    results[batch_idx] = (False, 0.0)
        
        return results

    def predict(self, names, batch_size: Optional[int] = None):
        """
        Unified predict function that handles both single names and batches.
        
        Args:
            names: Either a single name string or list of name strings
            batch_size: If provided and names is a list, process in chunks of this size
            
        Returns:
            If names is str: Same as predict_single()
            If names is list: List of prediction results (same as predict_batch())
        """
        # Handle single name
        if isinstance(names, str):
            return self.predict_single(names)
        
        # Handle list of names
        if not isinstance(names, list):
            raise ValueError("names must be either a string or list of strings")
        
        if not names:
            return []
        
        # If no batch_size specified, process all at once
        if batch_size is None:
            return self.predict_batch(names)
        
        # Process in chunks
        results = []
        for i in range(0, len(names), batch_size):
            batch = names[i:i + batch_size]
            batch_results = self.predict_batch(batch)
            results.extend(batch_results)
        
        return results 