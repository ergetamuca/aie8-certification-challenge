# app/rag_service.py
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import json
import os
import asyncio
import uuid
import hashlib
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .external_apis import ExternalAPIService

class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.qdrant_client = QdrantClient("localhost", port=6333)
        self.collection_name = "lesson_standards"
        self.external_api_service = ExternalAPIService()

    def _generate_document_id(self, prefix: str, subject: str, grade: str, index: int) -> str:
        """Generate a UUID-based document ID for Qdrant compatibility"""
        # Create a deterministic string from the parameters
        id_string = f"{prefix}_{subject.replace(' ', '_').lower()}_{grade.replace(' ', '_').lower()}_{index}"
        # Generate a UUID5 based on the string to ensure consistency
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Standard namespace
        return str(uuid.uuid5(namespace, id_string))
        
    async def initialize_vectorstore(self):
        """Initialize Qdrant with dynamic standards"""
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=3072,  # OpenAI text-embedding-3-large dimension
                        distance=Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection: {self.collection_name}")
                await self._load_dynamic_standards()
            else:
                print(f"Loaded existing Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            print(f"Error initializing Qdrant: {e}")
            # Fallback: create collection without initial data
            try:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=3072,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection: {self.collection_name}")
            except Exception as e2:
                print(f"Failed to create Qdrant collection: {e2}")
    
    async def _load_dynamic_standards(self):
        """Load dynamic standards for common subjects and grades"""
        print("Loading dynamic standards...")
        
        # Common subject/grade combinations to pre-populate
        common_combinations = [
            ("Mathematics", "3rd Grade"),
            ("Mathematics", "4th Grade"),
            ("Mathematics", "5th Grade"),
            ("Mathematics", "6th Grade"),
            ("Mathematics", "7th Grade"),
            ("Mathematics", "8th Grade"),
            ("English Language Arts", "3rd Grade"),
            ("English Language Arts", "4th Grade"),
            ("English Language Arts", "5th Grade"),
            ("English Language Arts", "6th Grade"),
            ("English Language Arts", "7th Grade"),
            ("English Language Arts", "8th Grade"),
            ("Science", "3rd Grade"),
            ("Science", "4th Grade"),
            ("Science", "5th Grade"),
            ("Science", "6th Grade"),
            ("Science", "7th Grade"),
            ("Science", "8th Grade"),
        ]
        
        for subject, grade in common_combinations:
            try:
                # Generate dynamic standards
                ccss_standards = await self.external_api_service.fetch_common_core_standards(subject, grade)
                
                # Add CCSS standards to Qdrant
                for i, standard in enumerate(ccss_standards):
                    doc_id = self._generate_document_id("ccss", subject, grade, i)
                    await self._add_document_to_qdrant(
                        text=standard["description"],
                        metadata={
                            "subject": subject,
                            "grade": grade,
                            "standard_id": standard["standard_id"],
                            "source": "Common Core",
                            "domain": standard.get("domain", ""),
                            "cluster": standard.get("cluster", ""),
                            "type": "standard"
                        },
                        doc_id=doc_id
                    )
                
                # Add NGSS standards for science subjects
                if subject.lower() in ["science", "physics", "chemistry", "biology"]:
                    ngss_standards = await self.external_api_service.fetch_ngss_standards(subject, grade)
                    
                    for i, standard in enumerate(ngss_standards):
                        doc_id = self._generate_document_id("ngss", subject, grade, i)
                        await self._add_document_to_qdrant(
                            text=standard["description"],
                            metadata={
                                "subject": subject,
                                "grade": grade,
                                "standard_id": standard["standard_id"],
                                "source": "NGSS",
                                "domain": standard.get("domain", ""),
                                "performance_expectation": standard.get("performance_expectation", ""),
                                "disciplinary_core_idea": standard.get("disciplinary_core_idea", ""),
                                "type": "standard"
                            },
                            doc_id=doc_id
                        )
                
                print(f"Loaded standards for {subject} - {grade}")
                
            except Exception as e:
                print(f"Error loading standards for {subject} - {grade}: {e}")
    
    async def _add_document_to_qdrant(self, text: str, metadata: Dict, doc_id: str):
        """Add a document to Qdrant"""
        try:
            # Generate embedding
            embedding = self.embeddings.embed_query(text)
            
            # Create point
            point = PointStruct(
                id=doc_id,
                vector=embedding,
                payload={
                    "text": text,
                    **metadata
                }
            )
            
            # Add to collection
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
        except Exception as e:
            print(f"Error adding document to Qdrant: {e}")
    
    
    async def search_documents(self, query: str, subject: str = None, grade: str = None, teacher_id: str = None, limit: int = 5) -> List[Dict]:
        """Search documents in Qdrant"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Build filter
            filter_conditions = []
            if subject:
                filter_conditions.append({
                    "key": "subject",
                    "match": {"value": subject}
                })
            if grade:
                filter_conditions.append({
                    "key": "grade", 
                    "match": {"value": grade}
                })
            if teacher_id:
                filter_conditions.append({
                    "key": "teacher_id",
                    "match": {"value": teacher_id}
                })
            
            # Search
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter={
                    "must": filter_conditions
                } if filter_conditions else None,
                limit=limit
            )
            
            # Format results
            results = []
            for point in search_result:
                results.append({
                    "id": point.id,
                    "text": point.payload.get("text", ""),
                    "metadata": {k: v for k, v in point.payload.items() if k != "text"},
                    "score": point.score
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    async def retrieve_relevant_standards(self, query: str, subject: str, grade: str, n_results: int = 5) -> List[Dict]:
        """Enhanced retrieval with Qdrant and external APIs using dynamic standards"""
        all_standards = []
        
        # 1. Search Qdrant for relevant documents (including dynamic standards)
        try:
            qdrant_results = await self.search_documents(
                query=query,
                subject=subject,
                grade=grade,
                limit=n_results
            )
            
            for result in qdrant_results:
                all_standards.append({
                    "standard_id": result["metadata"].get("standard_id", f"qdrant_{result['id']}"),
                    "description": result["text"],
                    "subject": subject,
                    "grade": grade,
                    "source": result["metadata"].get("source", "Qdrant"),
                    "resource_url": "",
                    "resource_title": result["metadata"].get("file_path", "Standards Database"),
                    "resource_type": result["metadata"].get("type", "standard"),
                    "score": result["score"],
                    "domain": result["metadata"].get("domain", ""),
                    "cluster": result["metadata"].get("cluster", "")
                })
                
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
        
        # 2. Fetch fresh dynamic standards from external APIs
        try:
            external_resources = await self.external_api_service.fetch_all_external_resources(subject, grade, query)
            
            for resource in external_resources:
                all_standards.append({
                    "standard_id": f"{resource.get('source', '')}_{resource.get('title', '')}",
                    "description": resource.get("description", ""),
                    "subject": subject,
                    "grade": grade,
                    "source": resource.get("source", ""),
                    "resource_url": resource.get("url", ""),
                    "resource_title": resource.get("title", ""),
                    "resource_type": resource.get("type", ""),
                    "domain": resource.get("domain", ""),
                    "cluster": resource.get("cluster", "")
                })
                
        except Exception as e:
            print(f"Error fetching external API data: {e}")
        
        # 3. If no results from Qdrant or external APIs, generate dynamic standards on-the-fly
        if not all_standards:
            try:
                print(f"No cached standards found, generating dynamic standards for {subject} - {grade}")
                
                # Generate CCSS standards
                ccss_standards = await self.external_api_service.fetch_common_core_standards(subject, grade)
                for standard in ccss_standards:
                    all_standards.append({
                        "standard_id": standard["standard_id"],
                        "description": standard["description"],
                        "subject": subject,
                        "grade": grade,
                        "source": "Common Core (Dynamic)",
                        "resource_url": "",
                        "resource_title": f"{subject} Standards",
                        "resource_type": "standard",
                        "domain": standard.get("domain", ""),
                        "cluster": standard.get("cluster", "")
                    })
                
                # Generate NGSS standards for science subjects
                if subject.lower() in ["science", "physics", "chemistry", "biology"]:
                    ngss_standards = await self.external_api_service.fetch_ngss_standards(subject, grade)
                    for standard in ngss_standards:
                        all_standards.append({
                            "standard_id": standard["standard_id"],
                            "description": standard["description"],
                            "subject": subject,
                            "grade": grade,
                            "source": "NGSS (Dynamic)",
                            "resource_url": "",
                            "resource_title": f"{subject} Standards",
                            "resource_type": "standard",
                            "domain": standard.get("domain", ""),
                            "performance_expectation": standard.get("performance_expectation", "")
                        })
                
            except Exception as e:
                print(f"Error generating dynamic standards: {e}")
        
        return all_standards[:n_results]

        
    
    async def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "points_count": info.points_count,
                "status": info.status,
                "vectors_count": info.vectors_count
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def cache_dynamic_standards(self, subject: str, grade: str) -> Dict:
        """Cache dynamic standards for a specific subject/grade combination"""
        try:
            print(f"Caching dynamic standards for {subject} - {grade}")
            
            # Generate and cache CCSS standards
            ccss_standards = await self.external_api_service.fetch_common_core_standards(subject, grade)
            cached_count = 0
            
            for i, standard in enumerate(ccss_standards):
                doc_id = self._generate_document_id("cached_ccss", subject, grade, i)
                await self._add_document_to_qdrant(
                    text=standard["description"],
                    metadata={
                        "subject": subject,
                        "grade": grade,
                        "standard_id": standard["standard_id"],
                        "source": "Common Core (Cached)",
                        "domain": standard.get("domain", ""),
                        "cluster": standard.get("cluster", ""),
                        "type": "cached_standard",
                        "cached_at": asyncio.get_event_loop().time()
                    },
                    doc_id=doc_id
                )
                cached_count += 1
            
            # Generate and cache NGSS standards for science subjects
            if subject.lower() in ["science", "physics", "chemistry", "biology"]:
                ngss_standards = await self.external_api_service.fetch_ngss_standards(subject, grade)
                
                for i, standard in enumerate(ngss_standards):
                    doc_id = self._generate_document_id("cached_ngss", subject, grade, i)
                    await self._add_document_to_qdrant(
                        text=standard["description"],
                        metadata={
                            "subject": subject,
                            "grade": grade,
                            "standard_id": standard["standard_id"],
                            "source": "NGSS (Cached)",
                            "domain": standard.get("domain", ""),
                            "performance_expectation": standard.get("performance_expectation", ""),
                            "disciplinary_core_idea": standard.get("disciplinary_core_idea", ""),
                            "type": "cached_standard",
                            "cached_at": asyncio.get_event_loop().time()
                        },
                        doc_id=doc_id
                    )
                    cached_count += 1
            
            return {
                "success": True,
                "subject": subject,
                "grade": grade,
                "cached_standards": cached_count,
                "message": f"Cached {cached_count} standards for {subject} - {grade}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to cache standards: {e}"
            }