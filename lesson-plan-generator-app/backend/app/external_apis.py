# app/external_apis.py
import requests
import asyncio
import aiohttp
import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time

class ExternalAPIService:
    def __init__(self):
        # Remove Ed-Fi API key and rate limiting
        self.edfi_api_key = None
        self.edfi_base_url = None
        self.edfi_rate_limit = 0
        self.edfi_requests = []
    
    async def fetch_common_core_standards(self, subject: str, grade: str) -> List[Dict]:
        """Fetch Common Core State Standards using dynamic generation"""
        try:
            # Limit to 3 most relevant standards
            standards = self._generate_common_core_standards(subject, grade)
            return standards[:3]  # Limit to 3 standards
            
        except Exception as e:
            print(f"Error fetching Common Core standards: {e}")
            return []
    
    def _generate_common_core_standards(self, subject: str, grade: str) -> List[Dict]:
        """Generate Common Core standards based on subject and grade"""
        standards = []
        
        # Map subjects to Common Core domains
        if subject.lower() in ["mathematics", "math"]:
            grade_num = self._extract_grade_number(grade)
            
            if grade_num >= 6:
                standards.extend([
                    {
                        "title": f"CCSS.MATH.CONTENT.6.NS.A.1",
                        "description": "Interpret and compute quotients of fractions, and solve word problems involving division of fractions by fractions.",
                        "resource_url": "https://www.corestandards.org/Math/Content/6/NS/A/1/",
                        "type": "Common Core Standard",
                        "subject": subject,
                        "source": "Common Core",
                        "grade_level": grade,
                        "domain": "Number and Operations—Fractions",
                        "fetched_at": datetime.now().isoformat()
                    },
                    {
                        "title": f"CCSS.MATH.CONTENT.6.NS.B.2",
                        "description": "Fluently divide multi-digit numbers using the standard algorithm.",
                        "resource_url": "https://www.corestandards.org/Math/Content/6/NS/B/2/",
                        "type": "Common Core Standard",
                        "subject": subject,
                        "source": "Common Core",
                        "grade_level": grade,
                        "domain": "Number and Operations in Base Ten",
                        "fetched_at": datetime.now().isoformat()
                    },
                    {
                        "title": f"CCSS.MATH.CONTENT.6.RP.A.1",
                        "description": "Understand the concept of a ratio and use ratio language to describe a ratio relationship between two quantities.",
                        "resource_url": "https://www.corestandards.org/Math/Content/6/RP/A/1/",
                        "type": "Common Core Standard",
                        "subject": subject,
                        "source": "Common Core",
                        "grade_level": grade,
                        "domain": "Ratios and Proportional Relationships",
                        "fetched_at": datetime.now().isoformat()
                    },
                    {
                        "title": f"CCSS.MATH.CONTENT.6.EE.A.1",
                        "description": "Write and evaluate numerical expressions involving whole-number exponents.",
                        "resource_url": "https://www.corestandards.org/Math/Content/6/EE/A/1/",
                        "type": "Common Core Standard",
                        "subject": subject,
                        "source": "Common Core",
                        "grade_level": grade,
                        "domain": "Expressions and Equations",
                        "fetched_at": datetime.now().isoformat()
                    },
                    {
                        "title": f"CCSS.MATH.CONTENT.6.G.A.1",
                        "description": "Find the area of right triangles, other triangles, special quadrilaterals, and polygons by composing into rectangles or decomposing into triangles and other shapes.",
                        "resource_url": "https://www.corestandards.org/Math/Content/6/G/A/1/",
                        "type": "Common Core Standard",
                        "subject": subject,
                        "source": "Common Core",
                        "grade_level": grade,
                        "domain": "Geometry",
                        "fetched_at": datetime.now().isoformat()
                    }
                ])
        
        elif subject.lower() in ["english", "language arts", "reading", "writing"]:
            grade_num = self._extract_grade_number(grade)
            
            if grade_num >= 6:
                standards.extend([
                    {
                        "title": f"CCSS.ELA-LITERACY.RL.6.1",
                        "description": "Cite textual evidence to support analysis of what the text says explicitly as well as inferences drawn from the text.",
                        "resource_url": "https://www.corestandards.org/ELA-Literacy/RL/6/1/",
                        "type": "Common Core Standard",
                        "subject": subject,
                        "source": "Common Core",
                        "grade_level": grade,
                        "domain": "Reading Literature",
                        "fetched_at": datetime.now().isoformat()
                    },
                    {
                        "title": f"CCSS.ELA-LITERACY.RI.6.1",
                        "description": "Cite textual evidence to support analysis of what the text says explicitly as well as inferences drawn from the text.",
                        "resource_url": "https://www.corestandards.org/ELA-Literacy/RI/6/1/",
                        "type": "Common Core Standard",
                        "subject": subject,
                        "source": "Common Core",
                        "grade_level": grade,
                        "domain": "Reading Informational Text",
                        "fetched_at": datetime.now().isoformat()
                    },
                    {
                        "title": f"CCSS.ELA-LITERACY.W.6.1",
                        "description": "Write arguments to support claims with clear reasons and relevant evidence.",
                        "resource_url": "https://www.corestandards.org/ELA-Literacy/W/6/1/",
                        "type": "Common Core Standard",
                        "subject": subject,
                        "source": "Common Core",
                        "grade_level": grade,
                        "domain": "Writing",
                        "fetched_at": datetime.now().isoformat()
                    }
                ])
        
        print(f"Generated {len(standards)} Common Core standards for {subject} grade {grade}")
        return standards
    
    async def fetch_ngss_standards(self, subject: str, grade: str) -> List[Dict]:
        """Fetch NGSS standards using dynamic generation"""
        try:
            if subject.lower() not in ['science', 'physics', 'chemistry', 'biology', 'astronomy']:
                return []
            
            standards = self._generate_ngss_standards(subject, grade)
            return standards[:2]  # Limit to 2 standards
            
        except Exception as e:
            print(f"Error fetching NGSS standards: {e}")
            return []
    
    def _generate_ngss_standards(self, subject: str, grade: str) -> List[Dict]:
        """Generate NGSS standards based on subject and grade"""
        standards = []
        grade_num = self._extract_grade_number(grade)
        
        if grade_num >= 6:
            standards.extend([
                {
                    "title": "MS-PS1-1",
                    "description": "Develop models to describe the atomic composition of simple molecules and extended structures.",
                    "resource_url": "https://www.nextgenscience.org/pe/ms-ps1-1-matter-and-its-interactions",
                    "type": "NGSS Standard",
                    "subject": subject,
                    "source": "NGSS",
                    "grade_level": grade,
                    "domain": "Physical Sciences",
                    "fetched_at": datetime.now().isoformat()
                },
                {
                    "title": "MS-LS1-1",
                    "description": "Conduct an investigation to provide evidence that living things are made of cells.",
                    "resource_url": "https://www.nextgenscience.org/pe/ms-ls1-1-from-molecules-organisms-structures-and-processes",
                    "type": "NGSS Standard",
                    "subject": subject,
                    "source": "NGSS",
                    "grade_level": grade,
                    "domain": "Life Sciences",
                    "fetched_at": datetime.now().isoformat()
                },
                {
                    "title": "MS-ESS1-1",
                    "description": "Develop and use a model of the Earth-sun-moon system to describe the cyclic patterns of lunar phases, eclipses of the sun and moon, and seasons.",
                    "resource_url": "https://www.nextgenscience.org/pe/ms-ess1-1-earth-s-place-universe",
                    "type": "NGSS Standard",
                    "subject": subject,
                    "source": "NGSS",
                    "grade_level": grade,
                    "domain": "Earth and Space Sciences",
                    "fetched_at": datetime.now().isoformat()
                }
            ])
        
        print(f"Generated {len(standards)} NGSS standards for {subject} grade {grade}")
        return standards
    
    def _extract_grade_number(self, grade: str) -> int:
        """Extract numeric grade from string like '6th Grade' or 'Grade 6'"""
        import re
        match = re.search(r'\d+', grade)
        return int(match.group()) if match else 6
    
    async def fetch_all_external_resources(self, subject: str, grade_level: str, topic: str) -> List[Dict]:
        """Fetch resources from all available APIs concurrently, limited to 10 diverse resources"""
        all_resources = []
        
        # Define resource priorities for diversity (only real APIs)
        resource_priorities = [
            ("youtube", self.fetch_youtube_educational_resources(subject, topic)),
            ("wikipedia", self.fetch_wikipedia_resources(subject, topic)),
            ("standards", self.fetch_common_core_standards(subject, grade_level)),
        ]
        
        # Add NGSS and NASA for science subjects
        if subject.lower() in ['science', 'physics', 'chemistry', 'biology', 'astronomy']:
            resource_priorities.append(("ngss", self.fetch_ngss_standards(subject, grade_level)))
            resource_priorities.append(("nasa", self.fetch_nasa_education_resources(subject, topic)))
        
        try:
            # Fetch resources concurrently
            results = await asyncio.gather(*[task for _, task in resource_priorities], return_exceptions=True)
            
            # Process results and ensure diversity
            resource_groups = {}
            for i, (source_type, result) in enumerate(zip([name for name, _ in resource_priorities], results)):
                if isinstance(result, list) and result:
                    resource_groups[source_type] = result
                elif isinstance(result, Exception):
                    print(f"API error for {source_type}: {result}")
            
            # Select diverse resources (max 3 per source type, total max 10)
            max_per_source = 3
            max_total = 10
            
            for source_type, resources in resource_groups.items():
                if len(all_resources) >= max_total:
                    break
                    
                # Take up to max_per_source from this source
                remaining_slots = max_total - len(all_resources)
                resources_to_add = min(max_per_source, remaining_slots, len(resources))
                
                all_resources.extend(resources[:resources_to_add])
            
            print(f"Fetched {len(all_resources)} diverse resources from external APIs")
            return all_resources
            
        except Exception as e:
            print(f"Error fetching external resources: {e}")
            return []
    

    async def fetch_youtube_educational_resources(self, subject: str, topic: str) -> List[Dict]:
        """Fetch educational videos from YouTube Data API"""
        try:
            # Get YouTube API key from environment variable
            api_key = os.getenv('YOUTUBE_API_KEY')
            
            if not api_key or api_key == 'your_youtube_api_key_here':
                print("YouTube API key not configured - skipping YouTube resources")
                return []
            
            async with aiohttp.ClientSession() as session:
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": f"{topic} {subject} educational lesson",
                    "type": "video",
                    "maxResults": 3,  # Reduced from 10 to 3
                    "key": api_key,
                    "order": "relevance",
                    "videoDuration": "medium",  # 4-20 minutes
                    "videoDefinition": "high",
                    "relevanceLanguage": "en"
                }
                
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        resources = []
                        
                        for item in data.get("items", []):
                            snippet = item.get("snippet", {})
                            video_id = item.get("id", {}).get("videoId", "")
                            
                            resource = {
                                "title": snippet.get("title", ""),
                                "description": snippet.get("description", "")[:200] + "..." if len(snippet.get("description", "")) > 200 else snippet.get("description", ""),
                                "resource_url": f"https://www.youtube.com/watch?v={video_id}",
                                "type": "Educational Video",
                                "subject": subject,
                                "source": "YouTube",
                                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                                "channel": snippet.get("channelTitle", ""),
                                "published": snippet.get("publishedAt", ""),
                                "fetched_at": datetime.now().isoformat()
                            }
                            resources.append(resource)
                        
                        print(f"Fetched {len(resources)} YouTube educational videos")
                        return resources
                    else:
                        error_text = await response.text()
                        print(f"YouTube API error: {response.status} - {error_text}")
                        return []
                        
        except Exception as e:
            print(f"Error fetching YouTube resources: {e}")
            return []

    async def fetch_interactive_resources(self, subject: str, topic: str) -> List[Dict]:
        """Fetch interactive educational resources - currently disabled due to lack of real APIs"""
        try:
            # Interactive resources disabled until we have real APIs
            # This prevents showing fake placeholder URLs
            print("Interactive resources temporarily disabled - no real APIs available")
            return []
            
        except Exception as e:
            print(f"Error fetching interactive resources: {e}")
            return []

    async def fetch_assessment_resources(self, subject: str, topic: str) -> List[Dict]:
        """Fetch assessment and practice resources - currently disabled due to lack of real APIs"""
        try:
            # Assessment resources disabled until we have real APIs
            # This prevents showing fake placeholder URLs
            print("Assessment resources temporarily disabled - no real APIs available")
            return []
            
        except Exception as e:
            print(f"Error fetching assessment resources: {e}")
            return []
    
    async def fetch_openstax_resources(self, subject: str, topic: str) -> List[Dict]:
        """Fetch resources from OpenStax API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://openstax.org/api/v2/pages"
                params = {
                    "search": f"{topic} {subject}",
                    "per_page": 10
                }
                
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        resources = []
                        
                        for item in data.get("results", []):
                            resource = {
                                "title": item.get("title", ""),
                                "description": item.get("description", ""),
                                "resource_url": item.get("url", ""),
                                "type": "OpenStax Resource",
                                "subject": subject,
                                "source": "OpenStax",
                                "fetched_at": datetime.now().isoformat()
                            }
                            resources.append(resource)
                        
                        return resources
                    else:
                        print(f"OpenStax API error: {response.status}")
                        return []
                        
        except Exception as e:
            print(f"Error fetching OpenStax resources: {e}")
            return []
    
    async def fetch_merlot_resources(self, subject: str, topic: str) -> List[Dict]:
        """Fetch resources from MERLOT API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://www.merlot.org/merlot/materials"
                params = {
                    "search": f"{topic} {subject}",
                    "limit": 10
                }
                
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        resources = []
                        
                        for item in data.get("results", []):
                            resource = {
                                "title": item.get("title", ""),
                                "description": item.get("description", ""),
                                "resource_url": item.get("url", ""),
                                "type": "MERLOT Resource",
                                "subject": subject,
                                "source": "MERLOT",
                                "fetched_at": datetime.now().isoformat()
                            }
                            resources.append(resource)
                        
                        return resources
                    else:
                        print(f"MERLOT API error: {response.status}")
                        return []
                        
        except Exception as e:
            print(f"Error fetching MERLOT resources: {e}")
            return []
    
    async def fetch_nasa_education_resources(self, subject: str, topic: str) -> List[Dict]:
        """Fetch resources from NASA Education API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://api.nasa.gov/planetary/apod"
                params = {
                    "api_key": "DEMO_KEY",
                    "count": 5
                }
                
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        resources = []
                        
                        for item in data:
                            resource = {
                                "title": item.get("title", ""),
                                "description": item.get("explanation", ""),
                                "resource_url": item.get("url", ""),
                                "type": "NASA Educational Resource",
                                "subject": subject,
                                "source": "NASA",
                                "fetched_at": datetime.now().isoformat()
                            }
                            resources.append(resource)
                        
                        return resources
                    else:
                        print(f"NASA API error: {response.status}")
                        return []
                        
        except Exception as e:
            print(f"Error fetching NASA resources: {e}")
            return []
    
    async def fetch_wikipedia_resources(self, subject: str, topic: str) -> List[Dict]:
        """Fetch resources from Wikipedia API with improved error handling"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "LessonPlanGenerator/1.0 (Educational Tool; contact@example.com)"
                }
                
                # Try multiple Wikipedia API endpoints
                endpoints = [
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}",
                    f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro&explaintext&titles={topic}",
                    f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro&titles={topic}"
                ]
                
                for url in endpoints:
                    try:
                        async with session.get(url, headers=headers, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # Handle different API response formats
                                if "rest_v1" in url:
                                    # REST API format
                                    resource = {
                                        "title": data.get("title", topic.title()),
                                        "description": data.get("extract", f"Educational content about {topic}"),
                                        "resource_url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{topic}"),
                                        "type": "Wikipedia Article",
                                        "subject": subject,
                                        "source": "Wikipedia",
                                        "fetched_at": datetime.now().isoformat()
                                    }
                                else:
                                    # Query API format
                                    pages = data.get("query", {}).get("pages", {})
                                    if pages:
                                        page_data = list(pages.values())[0]
                                        resource = {
                                            "title": page_data.get("title", topic.title()),
                                            "description": page_data.get("extract", f"Educational content about {topic}")[:500] + "...",
                                            "resource_url": f"https://en.wikipedia.org/wiki/{topic}",
                                            "type": "Wikipedia Article",
                                            "subject": subject,
                                            "source": "Wikipedia",
                                            "fetched_at": datetime.now().isoformat()
                                        }
                                    else:
                                        continue
                                
                                print(f"Fetched Wikipedia resource for {topic}")
                                return [resource]
                                
                    except Exception as e:
                        print(f"Wikipedia API endpoint failed: {e}")
                        continue
                
                # If all endpoints fail, return a mock Wikipedia resource
                print(f"All Wikipedia API endpoints failed for {topic}, using mock resource")
                return [{
                    "title": f"{topic.title()} - Educational Resource",
                    "description": f"Educational content about {topic} for {subject} students. This resource provides comprehensive information and learning materials.",
                    "resource_url": f"https://en.wikipedia.org/wiki/{topic}",
                    "type": "Wikipedia Article",
                    "subject": subject,
                    "source": "Wikipedia (Mock)",
                    "fetched_at": datetime.now().isoformat()
                }]
                
        except Exception as e:
            print(f"Error fetching Wikipedia resources: {e}")
            return []
            
    def _map_grade_to_edfi_descriptor(self, grade: str) -> str:
        """Map grade level to Ed-Fi grade level descriptor"""
        grade_mapping = {
            "Kindergarten": "uri://ed-fi.org/GradeLevelDescriptor#Kindergarten",
            "1st Grade": "uri://ed-fi.org/GradeLevelDescriptor#First grade",
            "2nd Grade": "uri://ed-fi.org/GradeLevelDescriptor#Second grade",
            "3rd Grade": "uri://ed-fi.org/GradeLevelDescriptor#Third grade",
            "4th Grade": "uri://ed-fi.org/GradeLevelDescriptor#Fourth grade",
            "5th Grade": "uri://ed-fi.org/GradeLevelDescriptor#Fifth grade",
            "6th Grade": "uri://ed-fi.org/GradeLevelDescriptor#Sixth grade",
            "7th Grade": "uri://ed-fi.org/GradeLevelDescriptor#Seventh grade",
            "8th Grade": "uri://ed-fi.org/GradeLevelDescriptor#Eighth grade"
        }
        return grade_mapping.get(grade, "uri://ed-fi.org/GradeLevelDescriptor#Sixth grade")
    