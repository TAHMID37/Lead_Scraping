"""
HubSpot Integration Module
Handles company data sync with HubSpot CRM
"""

import os
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HubSpotIntegration:
    """Handle HubSpot company operations"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('HUBSPOT_API_KEY', '') or None
        if not self.api_key:
            print("Warning: HUBSPOT_API_KEY not found in environment variables")
            self.api_key = None
        
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def is_enabled(self) -> bool:
        """Check if HubSpot integration is enabled"""
        return self.api_key is not None
    
    def search_company_by_name(self, company_name: str) -> Optional[Dict]:
        """
        Search for a company in HubSpot by name
        Returns company data if found, None otherwise
        """
        if not self.is_enabled():
            return None
        
        try:
            # HubSpot search API endpoint
            url = f"{self.base_url}/crm/v3/objects/companies/search"
            
            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "name",
                                "operator": "EQ",
                                "value": company_name
                            }
                        ]
                    }
                ],
                "properties": ["name", "domain", "description", "industry", "hs_object_id"],
                "limit": 1
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('total', 0) > 0 and data.get('results'):
                    return data['results'][0]
            
            return None
            
        except Exception as e:
            print(f"  ⚠️  Error searching HubSpot for {company_name}: {str(e)}")
            return None
    
    def create_company(self, company_name: str, company_description: str = "", 
                      industry: str = "", website: str = "", 
                      anzsco_eligible: bool = False) -> Optional[Dict]:
        """
        Create a new company in HubSpot
        Returns created company data if successful, None otherwise
        """
        if not self.is_enabled():
            return None
        
        try:
            url = f"{self.base_url}/crm/v3/objects/companies"
            
            # Clean and prepare description
            # HubSpot 'description' field has a 65,536 character limit
            # But for better display, we'll use both 'description' and 'about_us'
            clean_description = company_description.strip() if company_description else f"Company discovered from job scraping - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Prepare company properties
            properties = {
                "name": company_name,
                "description": clean_description[:65000],  # Stay within HubSpot limit
                "about_us": clean_description[:65000],  # Also add to about_us for better visibility
            }
            
            # Add optional fields if provided
            if industry:
                properties["industry"] = industry
            if website:
                properties["domain"] = website
            
            # Add custom field for ANZSCO eligibility (you may need to create this custom property in HubSpot)
            # properties["anzsco_eligible"] = "Yes" if anzsco_eligible else "No"
            
            payload = {"properties": properties}
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                print(f"  ✓ Created company in HubSpot: {company_name} (ID: {data.get('id')})")
                print(f"    Description length: {len(clean_description)} chars")
                return data
            else:
                print(f"  ✗ Failed to create company {company_name}: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            print(f"  ✗ Error creating company {company_name} in HubSpot: {str(e)}")
            return None
    
    def update_company(self, company_id: str, properties: Dict) -> Optional[Dict]:
        """
        Update an existing company in HubSpot
        Returns updated company data if successful, None otherwise
        """
        if not self.is_enabled():
            return None
        
        try:
            url = f"{self.base_url}/crm/v3/objects/companies/{company_id}"
            
            # Clean properties and handle long descriptions
            clean_props = {}
            for key, value in properties.items():
                if key in ['description', 'about_us'] and value:
                    clean_props[key] = str(value)[:65000]  # HubSpot limit
                else:
                    clean_props[key] = value
            
            payload = {"properties": clean_props}
            
            response = requests.patch(url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Updated company in HubSpot (ID: {company_id})")
                if 'description' in clean_props:
                    print(f"    Description length: {len(clean_props['description'])} chars")
                return data
            else:
                print(f"  ✗ Failed to update company {company_id}: {response.status_code}")
                return None
            
        except Exception as e:
            print(f"  ✗ Error updating company {company_id} in HubSpot: {str(e)}")
            return None
    
    def sync_company(self, company_name: str, company_description: str = "", 
                    industry: str = "", website: str = "", 
                    anzsco_eligible: bool = False) -> Tuple[bool, str, Optional[str]]:
        """
        Sync a company to HubSpot (create if doesn't exist, update if exists)
        
        Returns:
            Tuple of (success, action, company_id)
            action can be: 'created', 'exists', 'updated', 'skipped', 'failed'
        """
        if not self.is_enabled():
            return (False, 'skipped', None)
        
        if not company_name or company_name == "Not specified":
            return (False, 'skipped', None)
        
        # Clean company name
        company_name = company_name.strip()
        
        # Search for existing company
        existing_company = self.search_company_by_name(company_name)
        
        if existing_company:
            company_id = existing_company.get('id')
            
            # Check if we need to update description
            existing_desc = existing_company.get('properties', {}).get('description', '')
            
            # Only update if we have a better description
            if company_description and len(company_description) > len(existing_desc):
                update_props = {
                    "description": company_description,
                    "about_us": company_description
                }
                if industry:
                    update_props["industry"] = industry
                if website:
                    update_props["domain"] = website
                
                self.update_company(company_id, update_props)
                return (True, 'updated', company_id)
            else:
                return (True, 'exists', company_id)
        else:
            # Create new company
            created_company = self.create_company(
                company_name, 
                company_description, 
                industry, 
                website, 
                anzsco_eligible
            )
            
            if created_company:
                return (True, 'created', created_company.get('id'))
            else:
                return (False, 'failed', None)
    
    def batch_sync_companies(self, companies: List[Dict]) -> Dict:
        """
        Sync multiple companies to HubSpot
        
        Args:
            companies: List of dicts with keys: name, description, industry, website, anzsco_eligible
        
        Returns:
            Dictionary with sync statistics
        """
        if not self.is_enabled():
            return {
                'total': len(companies),
                'created': 0,
                'updated': 0,
                'exists': 0,
                'skipped': len(companies),
                'failed': 0,
                'enabled': False
            }
        
        stats = {
            'total': len(companies),
            'created': 0,
            'updated': 0,
            'exists': 0,
            'skipped': 0,
            'failed': 0,
            'enabled': True
        }
        
        print(f"\n{'='*60}")
        print(f"Syncing {len(companies)} companies to HubSpot...")
        print(f"{'='*60}")
        
        for i, company in enumerate(companies, 1):
            company_name = company.get('name', '')
            
            if not company_name or company_name == "Not specified":
                stats['skipped'] += 1
                continue
            
            print(f"\n[{i}/{len(companies)}] Processing: {company_name}")
            
            success, action, company_id = self.sync_company(
                company_name=company_name,
                company_description=company.get('description', ''),
                industry=company.get('industry', ''),
                website=company.get('website', ''),
                anzsco_eligible=company.get('anzsco_eligible', False)
            )
            
            stats[action] += 1
        
        print(f"\n{'='*60}")
        print(f"HubSpot Sync Complete")
        print(f"{'='*60}")
        print(f"Created: {stats['created']}")
        print(f"Updated: {stats['updated']}")
        print(f"Already Exists: {stats['exists']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Failed: {stats['failed']}")
        print(f"{'='*60}")
        
        return stats


# Convenience function for quick testing
def test_hubspot_connection():
    """Test HubSpot connection and API key"""
    hs = HubSpotIntegration()
    
    if not hs.is_enabled():
        print("❌ HubSpot integration is not enabled (missing API key)")
        print("\n💡 To enable HubSpot integration:")
        print("   1. Go to HubSpot → Settings → Integrations → Private Apps")
        print("   2. Create a new private app or use existing")
        print("   3. Grant scopes: crm.objects.companies.read & crm.objects.companies.write")
        print("   4. Copy the access token (starts with 'pat-')")
        print("   5. Add to .env file: HUBSPOT_API_KEY=your_token_here")
        return False
    
    print(f"📋 Testing HubSpot API key: {hs.api_key[:10]}...{hs.api_key[-4:]}")
    
    try:
        # Try to search for any company
        url = f"{hs.base_url}/crm/v3/objects/companies/search"
        payload = {
            "filterGroups": [],
            "properties": ["name"],
            "limit": 1
        }
        
        response = requests.post(url, headers=hs.headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ HubSpot connection successful!")
            print(f"   API endpoint: {url}")
            return True
        elif response.status_code == 401:
            print(f"❌ HubSpot connection failed: 401 Unauthorized")
            print("\n🔍 Common causes:")
            print("   1. Invalid API key format")
            print("   2. Expired or revoked token")
            print("   3. Wrong token type (need Private App token, not API key)")
            print("\n💡 Your API key format:")
            if hs.api_key.startswith('pat-'):
                print("   ✓ Starts with 'pat-' (correct format)")
            else:
                print("   ✗ Does NOT start with 'pat-' (may be wrong type)")
                print("   ⚠️  Make sure you're using a Private App access token, not an API key")
            print(f"   Length: {len(hs.api_key)} characters")
            print("\n📖 To get correct token:")
            print("   1. Go to: https://app.hubspot.com/private-apps/YOUR_ACCOUNT")
            print("   2. Create/select a Private App")
            print("   3. Copy the 'Access token' (NOT the API key)")
            return False
        else:
            print(f"❌ HubSpot connection failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing HubSpot connection: {str(e)}")
        return False


if __name__ == "__main__":
    # Test the connection
    test_hubspot_connection()
