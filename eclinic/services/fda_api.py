import requests
import json
from typing import List, Dict, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FDADrugAPI:
    """Service class for interacting with OpenFDA Drug API"""
    
    BASE_URL = "https://api.fda.gov/drug"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Sushrusa-Healthcare-Platform/1.0'
        })
    
    def search_drugs(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for drugs using OpenFDA API
        
        Args:
            query: Search query (drug name, generic name, etc.)
            limit: Maximum number of results to return
            
        Returns:
            List of drug information dictionaries
        """
        try:
            # Search in multiple fields - use simpler search syntax
            search_params = {
                'search': query,
                'limit': limit
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/label.json",
                params=search_params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for drug in data.get('results', []):
                drug_info = self._parse_drug_label(drug)
                if drug_info:
                    results.append(drug_info)
            
            return results
            
        except requests.RequestException as e:
            logger.error(f"FDA API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing FDA API response: {e}")
            return []
    
    def get_drug_details(self, drug_name: str) -> Optional[Dict]:
        """
        Get detailed information about a specific drug
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            Detailed drug information dictionary or None
        """
        try:
            search_params = {
                'search': drug_name,
                'limit': 1
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/label.json",
                params=search_params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('results'):
                return self._parse_drug_label(data['results'][0])
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"FDA API request failed for {drug_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing FDA API response for {drug_name}: {e}")
            return None
    
    def _parse_drug_label(self, drug_label: Dict) -> Optional[Dict]:
        """
        Parse FDA drug label data into our format
        
        Args:
            drug_label: Raw FDA drug label data
            
        Returns:
            Parsed drug information dictionary
        """
        try:
            openfda = drug_label.get('openfda', {})
            
            # Extract basic information
            generic_name = openfda.get('generic_name', [''])[0] if openfda.get('generic_name') else ''
            brand_name = openfda.get('brand_name', [''])[0] if openfda.get('brand_name') else ''
            substance_name = openfda.get('substance_name', [''])[0] if openfda.get('substance_name') else ''
            
            # Determine the primary name
            if generic_name:
                primary_name = generic_name
            elif brand_name:
                primary_name = brand_name
            elif substance_name:
                primary_name = substance_name
            else:
                return None
            
            # Extract dosage form
            dosage_form = self._extract_dosage_form(drug_label)
            
            # Extract strength
            strength = self._extract_strength(drug_label)
            
            # Extract therapeutic class
            therapeutic_class = self._extract_therapeutic_class(drug_label)
            
            # Extract indications
            indication = self._extract_indications(drug_label)
            
            # Extract contraindications
            contraindications = self._extract_contraindications(drug_label)
            
            # Extract side effects
            side_effects = self._extract_side_effects(drug_label)
            
            # Extract dosage instructions
            dosage_instructions = self._extract_dosage_instructions(drug_label)
            
            return {
                'id': f"fda_{openfda.get('product_ndc', [''])[0] if openfda.get('product_ndc') else ''}",
                'name': primary_name,
                'generic_name': generic_name,
                'brand_name': brand_name,
                'composition': substance_name,
                'dosage_form': dosage_form,
                'strength': strength,
                'medication_type': 'generic' if generic_name else 'branded',
                'therapeutic_class': therapeutic_class,
                'indication': indication,
                'contraindications': contraindications,
                'side_effects': side_effects,
                'dosage_instructions': dosage_instructions,
                'frequency_options': ['once_daily', 'twice_daily', 'thrice_daily'],
                'timing_options': ['before_breakfast', 'after_breakfast', 'before_lunch', 'after_lunch', 'before_dinner', 'after_dinner', 'at_bedtime'],
                'manufacturer': openfda.get('manufacturer_name', [''])[0] if openfda.get('manufacturer_name') else '',
                'license_number': openfda.get('product_ndc', [''])[0] if openfda.get('product_ndc') else '',
                'is_prescription_required': True,
                'source': 'fda_api',
                'is_verified': True,
                'fda_data': {
                    'product_ndc': openfda.get('product_ndc', []),
                    'package_ndc': openfda.get('package_ndc', []),
                    'pharm_class_cs': openfda.get('pharm_class_cs', []),
                    'pharm_class_moa': openfda.get('pharm_class_moa', []),
                    'pharm_class_pe': openfda.get('pharm_class_pe', []),
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing FDA drug label: {e}")
            return None
    
    def _extract_dosage_form(self, drug_label: Dict) -> str:
        """Extract dosage form from FDA label"""
        openfda = drug_label.get('openfda', {})
        
        # Check dosage form in openfda
        dosage_forms = openfda.get('dosage_form', [])
        if dosage_forms:
            form = dosage_forms[0].lower()
            # Map FDA dosage forms to our forms
            form_mapping = {
                'tablet': 'tablet',
                'capsule': 'capsule',
                'solution': 'syrup',
                'suspension': 'syrup',
                'injection': 'injection',
                'cream': 'cream',
                'ointment': 'ointment',
                'gel': 'cream',
                'drops': 'drops',
                'inhaler': 'inhaler',
                'suppository': 'suppository'
            }
            
            for fda_form, our_form in form_mapping.items():
                if fda_form in form:
                    return our_form
        
        # Default to tablet
        return 'tablet'
    
    def _extract_strength(self, drug_label: Dict) -> str:
        """Extract strength from FDA label"""
        openfda = drug_label.get('openfda', {})
        
        # Check active ingredients
        active_ingredients = drug_label.get('active_ingredient', [])
        if active_ingredients:
            for ingredient in active_ingredients:
                if isinstance(ingredient, dict) and 'strength' in ingredient:
                    return ingredient['strength']
        
        # Check openfda strength
        strengths = openfda.get('strength', [])
        if strengths:
            return strengths[0]
        
        return ''
    
    def _extract_therapeutic_class(self, drug_label: Dict) -> str:
        """Extract therapeutic class from FDA label"""
        openfda = drug_label.get('openfda', {})
        
        # Check pharmacologic class
        pharm_classes = openfda.get('pharm_class_cs', [])
        if pharm_classes:
            return pharm_classes[0]
        
        # Check mechanism of action
        moa_classes = openfda.get('pharm_class_moa', [])
        if moa_classes:
            return moa_classes[0]
        
        return ''
    
    def _extract_indications(self, drug_label: Dict) -> str:
        """Extract indications from FDA label"""
        indications = drug_label.get('indications_and_usage', [])
        if indications:
            return ' '.join(indications)
        
        return ''
    
    def _extract_contraindications(self, drug_label: Dict) -> str:
        """Extract contraindications from FDA label"""
        contraindications = drug_label.get('contraindications', [])
        if contraindications:
            return ' '.join(contraindications)
        
        return ''
    
    def _extract_side_effects(self, drug_label: Dict) -> str:
        """Extract side effects from FDA label"""
        side_effects = drug_label.get('adverse_reactions', [])
        if side_effects:
            return ' '.join(side_effects)
        
        return ''
    
    def _extract_dosage_instructions(self, drug_label: Dict) -> str:
        """Extract dosage instructions from FDA label"""
        dosage = drug_label.get('dosage_and_administration', [])
        if dosage:
            return ' '.join(dosage)
        
        return ''


# Global instance
fda_api = FDADrugAPI()


def search_fda_medications(query: str, limit: int = 10) -> List[Dict]:
    """
    Convenience function to search FDA medications
    
    Args:
        query: Search query
        limit: Maximum number of results
        
    Returns:
        List of medication dictionaries
    """
    return fda_api.search_drugs(query, limit)


def get_fda_medication_details(drug_name: str) -> Optional[Dict]:
    """
    Convenience function to get FDA medication details
    
    Args:
        drug_name: Name of the drug
        
    Returns:
        Medication details dictionary or None
    """
    return fda_api.get_drug_details(drug_name)
