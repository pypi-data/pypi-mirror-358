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

"""High-level API for name prediction."""

from pathlib import Path
from typing import Dict, List, Optional, Union
import torch

from .models.human_detector import HumanNameDetector
from .models.demographics import DemographicsPredictor
from .utils.data_utils import load_name_lists


class NameTracer:
    """Main API class for name prediction."""
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize the name tracer.
        
        Args:
            device: Device to run inference on ('cpu', 'cuda', or None for auto)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.data_dir = Path(__file__).parent / "data"
        
        # Load name lists for quick lookup
        self.known_names = load_name_lists(self.data_dir)
        
        # Initialize models (will be lazy loaded)
        self._human_detector = None
        self._demographics_predictor = None
    
    @property
    def human_detector(self) -> HumanNameDetector:
        """Lazy load human name detector."""
        if self._human_detector is None:
            self._human_detector = HumanNameDetector(
                known_names=self.known_names,
                device=self.device
            )
        return self._human_detector
    
    @property 
    def demographics_predictor(self) -> DemographicsPredictor:
        """Lazy load demographics predictor."""
        if self._demographics_predictor is None:
            self._demographics_predictor = DemographicsPredictor(
                device=self.device
            )
        return self._demographics_predictor
    
    def predict(self, names: Union[str, List[str]], topk: Optional[int] = 1, 
                batch_size: Optional[int] = None) -> Union[Dict, List[Dict]]:
        """
        Predict if name(s) are human and if so, predict gender and subregion.
        
        Args:
            names: Input name string or list of name strings
            topk: Number of top predictions to return for demographics (default: 1)
            batch_size: If provided and names is a list, process in chunks of this size
            
        Returns:
            If names is str: Dictionary containing prediction results
            If names is list: List of prediction dictionaries
            
            Each dictionary contains:
            - is_human: bool indicating if name is human
            - gender: predicted gender ('male'/'female') or list of (gender, confidence) tuples if topk>1
            - subregion: predicted subregion or list of (subregion, confidence) tuples if topk>1
            - confidence: confidence scores dict
        """
        # Handle single name
        if isinstance(names, str):
            # Check if name is human
            is_human, human_confidence = self.human_detector.predict(names)
            
            if not is_human:
                return {
                    'is_human': False,
                    'gender': None,
                    'subregion': None,
                    'confidence': {
                        'human': human_confidence,
                        'gender': None,
                        'subregion': None
                    }
                }
            
            # Predict demographics
            gender, subregion, demo_confidence = self.demographics_predictor.predict(names, topk=topk)
            
            return {
                'is_human': True,
                'gender': gender,
                'subregion': subregion,
                'confidence': {
                    'human': human_confidence,
                    'gender': demo_confidence.get('gender'),
                    'subregion': demo_confidence.get('subregion')
                }
            }
        
        # Handle list of names
        if not isinstance(names, list):
            raise ValueError("names must be either a string or list of strings")
        
        if not names:
            return []
        
        # Get human detection results for all names
        human_results = self.human_detector.predict(names, batch_size=batch_size)
        
        # Separate human and non-human names
        human_names = []
        human_indices = []
        
        for i, (is_human, _) in enumerate(human_results):
            if is_human:
                human_names.append(names[i])
                human_indices.append(i)
        
        # Get demographics for human names only
        if human_names:
            demo_results = self.demographics_predictor.predict(
                human_names, topk=topk, batch_size=batch_size
            )
        else:
            demo_results = []
        
        # Build final results
        results = []
        demo_idx = 0
        
        for i, (is_human, human_confidence) in enumerate(human_results):
            if not is_human:
                results.append({
                    'is_human': False,
                    'gender': None,
                    'subregion': None,
                    'confidence': {
                        'human': human_confidence,
                        'gender': None,
                        'subregion': None
                    }
                })
            else:
                # Get demographics result
                gender, subregion, demo_confidence = demo_results[demo_idx]
                demo_idx += 1
                
                results.append({
                    'is_human': True,
                    'gender': gender,
                    'subregion': subregion,
                    'confidence': {
                        'human': human_confidence,
                        'gender': demo_confidence.get('gender'),
                        'subregion': demo_confidence.get('subregion')
                    }
                })
        
        return results 