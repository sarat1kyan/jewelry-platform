#!/usr/bin/env python3
"""
Jewelry Customization Platform - Flask Backend
Main application file with all API endpoints
"""

import os
import glob
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import pandas as pd
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
import configparser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Configuration with defaults
BASE_DIR = config.get('PATHS', 'base_dir', fallback='/jewelry/cad_files')
CSV_DIR = config.get('PATHS', 'csv_dir', fallback='./config_files')
MONDAY_API_KEY = config.get('MONDAY', 'api_key', fallback='')
MONDAY_BOARD_ID = config.get('MONDAY', 'board_id', fallback='')
MONDAY_API_URL = "https://api.monday.com/v2"

# Cache for CSV data
cache = {}


class JewelryPlatform:
    """Main class for jewelry customization platform logic"""
    
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        """Load all CSV and Excel data into memory"""
        try:
            # Load abbreviation mappings
            self.abbreviation_map = pd.read_csv(
                os.path.join(CSV_DIR, 'Abbreviation Map.csv')
            ).set_index('Term')['Abbreviation'].to_dict()
            
            self.reverse_map = pd.read_csv(
                os.path.join(CSV_DIR, 'Reverse Mapping.csv')
            ).set_index('Abbreviation')['Full Term'].to_dict()
            
            # Load filenames database
            self.filenames_df = pd.read_csv(
                os.path.join(CSV_DIR, 'Filenames.csv')
            )
            
            # Load jewelry types from Excel
            self.jewelry_types_df = pd.read_excel(
                os.path.join(CSV_DIR, 'SLS-final-nam-lab 3.xlsx'),
                sheet_name='Jewelry Type'
            )
            
            # Extract unique values for each parameter
            self.parameters = self._extract_parameters()
            
            logger.info("Data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            # Use default parameters if files not found
            self.parameters = self._get_default_parameters()
            self.abbreviation_map = {}
            self.reverse_map = {}
            self.filenames_df = pd.DataFrame(columns=['Directory', 'Filename'])
    
    def _get_default_parameters(self) -> Dict[str, List[str]]:
        """Get default parameters"""
        return {
            'Jewelry Type': ['ER', 'WB', 'Earring', 'Necklace', 'Bracelet'],
            'Ring Type': ['Solitaire', 'Halo', 'Bezel', 'Three Stone', 'Vintage'],
            'Shank Type': ['Classic', 'Knife-Edge', 'Cathedral', 'Split', 'Twisted'],
            'Stone Shape': ['Round', 'Princess', 'Oval', 'Emerald', 'Cushion', 'Pear'],
            'Metal Type': ['10k', '14k', '18k', 'Platinum', 'Silver'],
            'Design Details': ['Milgrain', 'Engraved', 'Hammered', 'Pavé', 'Plain']
        }
    
    def _extract_parameters(self) -> Dict[str, List[str]]:
        """Extract unique parameter values from jewelry types data"""
        parameters = self._get_default_parameters()
        
        # Try to extract from Excel if available
        try:
            for col in self.jewelry_types_df.columns:
                unique_vals = self.jewelry_types_df[col].dropna().unique().tolist()
                if unique_vals and col in parameters:
                    parameters[col] = unique_vals
        except:
            logger.warning("Could not extract parameters from Excel, using defaults")
        
        return parameters
    
    def generate_filename(self, selections: Dict[str, str]) -> str:
        """Generate CAD filename from user selections"""
        parts = []
        
        # Order matters for filename generation
        param_order = ['Jewelry Type', 'Ring Type', 'Stone Shape', 'Metal Type', 'Design Details']
        
        for param in param_order:
            if param in selections and selections[param]:
                value = selections[param]
                # Get abbreviation
                abbrev = self.abbreviation_map.get(value, value[:3].lower())
                parts.append(abbrev.lower())
        
        filename = '_'.join(parts) + '.3dm'
        logger.info(f"Generated filename: {filename}")
        return filename
    
    def find_matching_files(self, target_filename: str) -> List[Dict]:
        """Find matching CAD files with scoring"""
        matches = []
        target_parts = target_filename.replace('.3dm', '').split('_')
        
        for _, row in self.filenames_df.iterrows():
            filename = row['Filename']
            directory = row['Directory']
            full_path = os.path.join(BASE_DIR, directory, filename)
            
            # Calculate match score
            score = self._calculate_match_score(filename, target_parts)
            
            if score > 0:
                matches.append({
                    'filename': filename,
                    'directory': directory,
                    'full_path': full_path,
                    'score': score,
                    'exists': os.path.exists(full_path)
                })
        
        # Sort by score (highest first)
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:10]  # Return top 10 matches
    
    def _calculate_match_score(self, filename: str, target_parts: List[str]) -> int:
        """Calculate match score between filename and target parts"""
        score = 0
        file_parts = filename.replace('.3dm', '').split('_')
        
        # Position-based matching
        for i, part in enumerate(target_parts):
            if i < len(file_parts) and part == file_parts[i]:
                score += 20  # Position match
            elif part in file_parts:
                score += 10  # Parameter exists but different position
        
        # Bonus for exact length match
        if len(file_parts) == len(target_parts):
            score += 5
        
        return score
    
    def create_monday_task(self, selections: Dict, file_path: str) -> Dict:
        """Create a task in Monday.com"""
        if not MONDAY_API_KEY or not MONDAY_BOARD_ID:
            raise ValueError("Monday.com credentials not configured")
        
        # Format description
        description = "Jewelry Order Details:\\n"
        for key, value in selections.items():
            description += f"- {key}: {value}\\n"
        description += f"\\nCAD File: {file_path}"
        
        # GraphQL mutation for creating item
        mutation = """
        mutation ($boardId: Int!, $itemName: String!, $columnValues: JSON!) {
            create_item (
                board_id: $boardId,
                item_name: $itemName,
                column_values: $columnValues
            ) {
                id
                name
            }
        }
        """
        
        # Prepare column values
        column_values = json.dumps({
            "status": "New",
            "text": description
        })
        
        variables = {
            "boardId": int(MONDAY_BOARD_ID),
            "itemName": f"Jewelry Order: {selections.get('Jewelry Type', 'Custom')}",
            "columnValues": column_values
        }
        
        headers = {
            "Authorization": MONDAY_API_KEY,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                MONDAY_API_URL,
                json={"query": mutation, "variables": variables},
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            if 'errors' in result:
                raise Exception(f"Monday.com API error: {result['errors']}")
            
            return result['data']['create_item']
            
        except Exception as e:
            logger.error(f"Error creating Monday.com task: {str(e)}")
            raise


# Initialize platform
platform = JewelryPlatform()


@app.route('/api/parameters', methods=['GET'])
def get_parameters():
    """Get available parameters for selection"""
    try:
        return jsonify({
            'success': True,
            'parameters': platform.parameters
        })
    except Exception as e:
        logger.error(f"Error getting parameters: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-filename', methods=['POST'])
def generate_filename():
    """Generate filename from selections"""
    try:
        selections = request.json.get('selections', {})
        if not selections:
            raise BadRequest("No selections provided")
        
        filename = platform.generate_filename(selections)
        
        return jsonify({
            'success': True,
            'filename': filename
        })
    except Exception as e:
        logger.error(f"Error generating filename: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/find-matches', methods=['POST'])
def find_matches():
    """Find matching CAD files"""
    try:
        selections = request.json.get('selections', {})
        if not selections:
            raise BadRequest("No selections provided")
        
        # Generate target filename
        target_filename = platform.generate_filename(selections)
        
        # Find matches
        matches = platform.find_matching_files(target_filename)
        
        return jsonify({
            'success': True,
            'target_filename': target_filename,
            'matches': matches
        })
    except Exception as e:
        logger.error(f"Error finding matches: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/create-task', methods=['POST'])
def create_task():
    """Create Monday.com task"""
    try:
        data = request.json
        selections = data.get('selections', {})
        file_path = data.get('file_path', '')
        
        if not selections:
            raise BadRequest("No selections provided")
        
        # Create Monday.com task
        task = platform.create_monday_task(selections, file_path)
        
        return jsonify({
            'success': True,
            'task': task
        })
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/reload-data', methods=['POST'])
def reload_data():
    """Reload CSV/Excel data"""
    try:
        platform.load_data()
        return jsonify({
            'success': True,
            'message': 'Data reloaded successfully'
        })
    except Exception as e:
        logger.error(f"Error reloading data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(CSV_DIR, exist_ok=True)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_ENV') == 'development'
    )
