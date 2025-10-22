# app/advanced_retrieval.py
import asyncio
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import re
from collections import defaultdict

# Advanced retrieval imports
try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    from rank_bm25 import BM25Okapi
    import faiss
    ADVANCED_RETRIEVAL_AVAILABLE = True
except ImportError:
    print("⚠️  Advanced retrieval libraries not installed. Install with:")
    print("pip install sentence-transformers rank-bm25 faiss-cpu")
    ADVANCED_RETRIEVAL_AVAILABLE = False

from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

class RetrievalStrategy(Enum):
    """Different retrieval strategies to test"""
    BASIC="basic"
    HYBRID_SEARCH = "hybrid_search"
    MULTI_VECTOR = "multi_vector"
    QUERY_EXPANSION = "query_expansion"
    RERANKING = "reranking"
    HIERARCHICAL = "hierarchical"
    TEMPORAL = "temporal"
    METADATA_FILTERED = "metadata_filtered"
    CONTEXTUAL_COMPRESSION = "contextual_compression"
    STUDENT_GROUP_AWARE = "student_group_aware"  # New strategy
    EXTERNAL_RESOURCE_FOCUSED = "external_resource_focused"  # New strategy

@dataclass
class RetrievalResult:
    """Structured result from advanced retrieval"""
    content: str
    metadata: Dict[str, Any]
    score: float
    retrieval_method: str
    relevance_explanation: str
    student_group_relevance: Optional[str] = None  # New field
    external_resource_type: Optional[str] = None  # New field

class AdvancedRetriever:
    """
    Advanced retrieval system implementing multiple strategies
    to improve Context Recall and Context Precision
    Updated for v2.0 with student group awareness and external resources
    """
    
    def __init__(self, rag_service):
        self.rag_service = rag_service
        self.qdrant_client = rag_service.qdrant_client
        self.collection_name = rag_service.collection_name
        
        # Initialize advanced models
        if ADVANCED_RETRIEVAL_AVAILABLE:
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            self.bm25_index = None
            self.faiss_index = None
        
        # Retrieval configuration
        self.retrieval_config = {
            "hybrid_alpha": 0.7,  # Weight for semantic vs keyword search
            "expansion_queries": 3,  # Number of query expansions
            "rerank_top_k": 20,  # Top K results to rerank
            "final_top_k": 5,  # Final number of results
            "temporal_weight": 0.1,  # Weight for recency
            "metadata_boost": 0.2,  # Boost for metadata matches
            "student_group_weight": 0.3,  # Weight for student group relevance
            "external_resource_weight": 0.4  # Weight for external resource relevance
        }
    
    async def advanced_retrieve(
        self, 
        query: str, 
        subject: str, 
        grade: str, 
        strategy: RetrievalStrategy = RetrievalStrategy.HYBRID_SEARCH,
        student_group_info: str = "",
        **kwargs
    ) -> List[RetrievalResult]:
        """
        Main advanced retrieval method that routes to specific strategies
        Updated to include student group information
        """
        
        print(f"🔍 Advanced retrieval using {strategy.value}")
        if student_group_info:
            print(f"👥 Student group context: {student_group_info}")
        
        if strategy == RetrievalStrategy.HYBRID_SEARCH:
            return await self._hybrid_search(query, subject, grade, student_group_info)
        
        elif strategy == RetrievalStrategy.MULTI_VECTOR:
            return await self._multi_vector_search(query, subject, grade, student_group_info)
        
        elif strategy == RetrievalStrategy.QUERY_EXPANSION:
            return await self._query_expansion_search(query, subject, grade, student_group_info)
        
        elif strategy == RetrievalStrategy.RERANKING:
            return await self._reranking_search(query, subject, grade, student_group_info)
        
        elif strategy == RetrievalStrategy.HIERARCHICAL:
            return await self._hierarchical_search(query, subject, grade, student_group_info)
        
        elif strategy == RetrievalStrategy.TEMPORAL:
            return await self._temporal_search(query, subject, grade, student_group_info)
        
        elif strategy == RetrievalStrategy.METADATA_FILTERED:
            return await self._metadata_filtered_search(query, subject, grade, student_group_info)
        
        elif strategy == RetrievalStrategy.CONTEXTUAL_COMPRESSION:
            return await self._contextual_compression_search(query, subject, grade, student_group_info)
        
        elif strategy == RetrievalStrategy.STUDENT_GROUP_AWARE:
            return await self._student_group_aware_search(query, subject, grade, student_group_info)
        
        elif strategy == RetrievalStrategy.EXTERNAL_RESOURCE_FOCUSED:
            return await self._external_resource_focused_search(query, subject, grade, student_group_info)
        
        else:
            # Fallback to basic retrieval
            return await self._basic_retrieval(query, subject, grade, student_group_info)
    
    async def _hybrid_search(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """
        HYBRID SEARCH: Combines semantic vector search with keyword-based BM25 search
        Updated to consider student group context
        """
        
        print("🔄 Executing hybrid search (semantic + keyword)")
        
        # Get semantic results
        semantic_results = await self._semantic_search(query, subject, grade, limit=10, student_group_info=student_group_info)
        
        # Get keyword results using BM25
        keyword_results = await self._bm25_search(query, subject, grade, limit=10, student_group_info=student_group_info)
        
        # Combine and deduplicate results
        combined_results = self._combine_results(
            semantic_results, keyword_results, 
            alpha=self.retrieval_config["hybrid_alpha"]
        )
        
        # Convert to RetrievalResult format
        results = []
        for i, (content, metadata, score) in enumerate(combined_results[:self.retrieval_config["final_top_k"]]):
            student_relevance = self._assess_student_group_relevance(content, student_group_info)
            results.append(RetrievalResult(
                content=content,
                metadata=metadata,
                score=score,
                retrieval_method="hybrid_search",
                relevance_explanation=f"Combined semantic similarity ({score:.3f}) with keyword matching",
                student_group_relevance=student_relevance
            ))
        
        return results
    
    async def _student_group_aware_search(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """
        STUDENT GROUP AWARE SEARCH: Prioritizes content relevant to specific student groups
        Why useful: Educational content needs to be accessible and appropriate for diverse learners
        """
        
        print("🔄 Executing student group aware search")
        
        # Get initial results
        initial_results = await self._semantic_search(query, subject, grade, limit=15, student_group_info=student_group_info)
        
        # Apply student group relevance scoring
        student_group_results = []
        
        for content, metadata, score in initial_results:
            # Assess relevance to student group
            student_relevance = self._assess_student_group_relevance(content, student_group_info)
            
            # Boost score based on student group relevance
            if student_relevance:
                if "ESL" in student_group_info or "English language" in student_group_info:
                    if any(term in content.lower() for term in ["visual", "hands-on", "multimodal", "support"]):
                        score *= 1.3
                elif "ADHD" in student_group_info:
                    if any(term in content.lower() for term in ["movement", "kinesthetic", "interactive", "short"]):
                        score *= 1.3
                elif "learning disability" in student_group_info:
                    if any(term in content.lower() for term in ["differentiated", "accommodation", "alternative", "support"]):
                        score *= 1.3
                elif "gifted" in student_group_info:
                    if any(term in content.lower() for term in ["advanced", "challenge", "enrichment", "extension"]):
                        score *= 1.3
            
            student_group_results.append((content, metadata, score))
        
        # Sort by adjusted score
        student_group_results.sort(key=lambda x: x[2], reverse=True)
        
        # Convert to RetrievalResult format
        results = []
        for i, (content, metadata, score) in enumerate(student_group_results[:self.retrieval_config["final_top_k"]]):
            student_relevance = self._assess_student_group_relevance(content, student_group_info)
            results.append(RetrievalResult(
                content=content,
                metadata=metadata,
                score=score,
                retrieval_method="student_group_aware",
                relevance_explanation=f"Student group optimized search for: {student_group_info}",
                student_group_relevance=student_relevance
            ))
        
        return results
    
    async def _external_resource_focused_search(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """
        EXTERNAL RESOURCE FOCUSED SEARCH: Prioritizes external resources (YouTube, Wikipedia, etc.)
        Why useful: External resources provide diverse learning materials and real-world connections
        """
        
        print("🔄 Executing external resource focused search")
        
        # Get initial results
        initial_results = await self._semantic_search(query, subject, grade, limit=15, student_group_info=student_group_info)
        
        # Prioritize external resources
        external_resource_results = []
        
        for content, metadata, score in initial_results:
            # Boost external resources
            resource_type = metadata.get("source", "").lower()
            if resource_type in ["youtube", "wikipedia", "interactive", "assessment"]:
                score *= 1.4
            elif resource_type in ["common core", "ngss", "nasa"]:
                score *= 1.2
            
            # Boost resources with actual URLs
            if metadata.get("resource_url") and not metadata.get("resource_url").startswith("example"):
                score *= 1.3
            
            external_resource_results.append((content, metadata, score))
        
        # Sort by adjusted score
        external_resource_results.sort(key=lambda x: x[2], reverse=True)
        
        # Convert to RetrievalResult format
        results = []
        for i, (content, metadata, score) in enumerate(external_resource_results[:self.retrieval_config["final_top_k"]]):
            resource_type = metadata.get("source", "Unknown")
            results.append(RetrievalResult(
                content=content,
                metadata=metadata,
                score=score,
                retrieval_method="external_resource_focused",
                relevance_explanation=f"External resource prioritized search (type: {resource_type})",
                external_resource_type=resource_type
            ))
        
        return results
    
    async def _multi_vector_search(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """
        MULTI-VECTOR SEARCH: Uses multiple embedding models and combines results
        Updated to include student group context
        """
        
        print("🔄 Executing multi-vector search")
        
        # Use different embedding models
        embeddings = [
            ("openai", self.rag_service.embeddings),
            ("sentence_transformer", self.sentence_transformer if ADVANCED_RETRIEVAL_AVAILABLE else None)
        ]
        
        all_results = []
        
        for model_name, embedding_model in embeddings:
            if embedding_model is None:
                continue
                
            # Generate embeddings and search
            if model_name == "openai":
                query_embedding = embedding_model.embed_query(query)
            else:
                query_embedding = embedding_model.encode([query])[0]
            
            # Search Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=self._build_metadata_filter(subject, grade),
                limit=8
            )
            
            # Process results
            for point in search_result:
                all_results.append({
                    "content": point.payload.get("text", ""),
                    "metadata": {k: v for k, v in point.payload.items() if k != "text"},
                    "score": point.score,
                    "model": model_name
                })
        
        # Combine and deduplicate multi-model results
        combined_results = self._deduplicate_and_rank(all_results)
        
        # Convert to RetrievalResult format
        results = []
        for i, result in enumerate(combined_results[:self.retrieval_config["final_top_k"]]):
            student_relevance = self._assess_student_group_relevance(result["content"], student_group_info)
            results.append(RetrievalResult(
                content=result["content"],
                metadata=result["metadata"],
                score=result["score"],
                retrieval_method="multi_vector",
                relevance_explanation=f"Multi-model consensus from {result.get('models', 1)} embedding models",
                student_group_relevance=student_relevance
            ))
        
        return results
    
    async def _query_expansion_search(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """
        QUERY EXPANSION: Generates related queries and searches with all of them
        Updated to include student group specific expansions
        """
        
        print("🔄 Executing query expansion search")
        
        # Generate expanded queries including student group context
        expanded_queries = await self._generate_query_expansions(query, subject, grade, student_group_info)
        
        all_results = []
        
        # Search with each expanded query
        for expanded_query in expanded_queries:
            results = await self._semantic_search(expanded_query, subject, grade, limit=5, student_group_info=student_group_info)
            all_results.extend(results)
        
        # Combine and deduplicate
        combined_results = self._deduplicate_and_rank(all_results)
        
        # Convert to RetrievalResult format
        results = []
        for i, (content, metadata, score) in enumerate(combined_results[:self.retrieval_config["final_top_k"]]):
            student_relevance = self._assess_student_group_relevance(content, student_group_info)
            results.append(RetrievalResult(
                content=content,
                metadata=metadata,
                score=score,
                retrieval_method="query_expansion",
                relevance_explanation=f"Found via expanded query variations: {len(expanded_queries)} queries",
                student_group_relevance=student_relevance
            ))
        
        return results
    
    async def _reranking_search(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """
        RERANKING: Uses cross-encoder to rerank initial retrieval results
        Updated to consider student group context in reranking
        """
        
        print("🔄 Executing reranking search")
        
        # Get initial results (more than needed)
        initial_results = await self._semantic_search(query, subject, grade, limit=self.retrieval_config["rerank_top_k"], student_group_info=student_group_info)
        
        if not ADVANCED_RETRIEVAL_AVAILABLE or not initial_results:
            return await self._basic_retrieval(query, subject, grade, student_group_info)
        
        # Prepare pairs for cross-encoder
        query_doc_pairs = []
        for content, metadata, score in initial_results:
            # Enhance query with student group context for better reranking
            enhanced_query = query
            if student_group_info:
                enhanced_query = f"{query} for {student_group_info}"
            query_doc_pairs.append([enhanced_query, content])
        
        # Rerank using cross-encoder
        rerank_scores = self.cross_encoder.predict(query_doc_pairs)
        
        # Combine original scores with rerank scores
        reranked_results = []
        for i, (content, metadata, original_score) in enumerate(initial_results):
            combined_score = 0.7 * rerank_scores[i] + 0.3 * original_score
            reranked_results.append((content, metadata, combined_score))
        
        # Sort by combined score
        reranked_results.sort(key=lambda x: x[2], reverse=True)
        
        # Convert to RetrievalResult format
        results = []
        for i, (content, metadata, score) in enumerate(reranked_results[:self.retrieval_config["final_top_k"]]):
            student_relevance = self._assess_student_group_relevance(content, student_group_info)
            results.append(RetrievalResult(
                content=content,
                metadata=metadata,
                score=score,
                retrieval_method="reranking",
                relevance_explanation=f"Reranked using cross-encoder (score: {score:.3f})",
                student_group_relevance=student_relevance
            ))
        
        return results
    
    async def _hierarchical_search(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """
        HIERARCHICAL SEARCH: Multi-stage retrieval with increasingly specific queries
        Updated to include student group context in hierarchical stages
        """
        
        print("🔄 Executing hierarchical search")
        
        # Stage 1: Broad subject-level search
        broad_query = f"{subject} curriculum standards"
        broad_results = await self._semantic_search(broad_query, subject, grade, limit=15, student_group_info=student_group_info)
        
        # Stage 2: Grade-specific search
        grade_query = f"{subject} {grade} learning objectives"
        grade_results = await self._semantic_search(grade_query, subject, grade, limit=10, student_group_info=student_group_info)
        
        # Stage 3: Specific topic search
        topic_query = query
        topic_results = await self._semantic_search(topic_query, subject, grade, limit=8, student_group_info=student_group_info)
        
        # Stage 4: Student group specific search (if applicable)
        student_group_results = []
        if student_group_info:
            student_query = f"{query} {student_group_info}"
            student_group_results = await self._semantic_search(student_query, subject, grade, limit=5, student_group_info=student_group_info)
        
        # Combine with hierarchical weighting
        all_results = []
        
        # Weight broad results lower
        for content, metadata, score in broad_results:
            all_results.append((content, metadata, score * 0.3))
        
        # Weight grade results medium
        for content, metadata, score in grade_results:
            all_results.append((content, metadata, score * 0.6))
        
        # Weight topic results highest
        for content, metadata, score in topic_results:
            all_results.append((content, metadata, score * 1.0))
        
        # Weight student group results highest if available
        for content, metadata, score in student_group_results:
            all_results.append((content, metadata, score * 1.2))
        
        # Deduplicate and rank
        combined_results = self._deduplicate_and_rank(all_results)
        
        # Convert to RetrievalResult format
        results = []
        for i, (content, metadata, score) in enumerate(combined_results[:self.retrieval_config["final_top_k"]]):
            student_relevance = self._assess_student_group_relevance(content, student_group_info)
            results.append(RetrievalResult(
                content=content,
                metadata=metadata,
                score=score,
                retrieval_method="hierarchical",
                relevance_explanation=f"Multi-stage hierarchical search (subject->grade->topic->student_group)",
                student_group_relevance=student_relevance
            ))
        
        return results
    
    async def _temporal_search(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """
        TEMPORAL SEARCH: Prioritizes recent curriculum updates and standards
        Updated to consider student group context in temporal weighting
        """
        
        print("🔄 Executing temporal search")
        
        # Get all results first
        all_results = await self._semantic_search(query, subject, grade, limit=20, student_group_info=student_group_info)
        
        # Apply temporal weighting
        temporal_results = []
        current_time = asyncio.get_event_loop().time()
        
        for content, metadata, score in all_results:
            # Extract temporal information from metadata
            temporal_weight = 1.0
            
            # Boost recent standards
            if "cached_at" in metadata:
                age_hours = (current_time - metadata["cached_at"]) / 3600
                temporal_weight = max(0.5, 1.0 - (age_hours / 8760))  # Decay over year
            
            # Boost current standards
            if metadata.get("source") in ["Common Core", "NGSS"]:
                temporal_weight *= 1.2
            
            # Boost external resources (they're more current)
            if metadata.get("source") in ["YouTube", "Wikipedia"]:
                temporal_weight *= 1.3
            
            # Apply temporal boost
            adjusted_score = score * (1.0 + self.retrieval_config["temporal_weight"] * temporal_weight)
            temporal_results.append((content, metadata, adjusted_score))
        
        # Sort by adjusted score
        temporal_results.sort(key=lambda x: x[2], reverse=True)
        
        # Convert to RetrievalResult format
        results = []
        for i, (content, metadata, score) in enumerate(temporal_results[:self.retrieval_config["final_top_k"]]):
            student_relevance = self._assess_student_group_relevance(content, student_group_info)
            results.append(RetrievalResult(
                content=content,
                metadata=metadata,
                score=score,
                retrieval_method="temporal",
                relevance_explanation=f"Temporal-weighted search (recency boost: {temporal_weight:.2f})",
                student_group_relevance=student_relevance
            ))
        
        return results
    
    async def _metadata_filtered_search(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """
        METADATA FILTERED SEARCH: Uses rich metadata filtering before semantic search
        Updated to include student group metadata filtering
        """
        
        print("🔄 Executing metadata filtered search")
        
        # Build sophisticated metadata filters including student group context
        filters = self._build_advanced_metadata_filter(query, subject, grade, student_group_info)
        
        # Perform filtered search
        query_embedding = self.rag_service.embeddings.embed_query(query)
        
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=filters,
            limit=self.retrieval_config["final_top_k"]
        )
        
        # Convert to RetrievalResult format
        results = []
        for point in search_result:
            student_relevance = self._assess_student_group_relevance(point.payload.get("text", ""), student_group_info)
            results.append(RetrievalResult(
                content=point.payload.get("text", ""),
                metadata={k: v for k, v in point.payload.items() if k != "text"},
                score=point.score,
                retrieval_method="metadata_filtered",
                relevance_explanation=f"Metadata-filtered search with {len(filters.get('must', []))} filters",
                student_group_relevance=student_relevance
            ))
        
        return results
    
    async def _contextual_compression_search(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """
        CONTEXTUAL COMPRESSION: Retrieves longer contexts and compresses them to relevant parts
        Updated to consider student group context in compression
        """
        
        print("🔄 Executing contextual compression search")
        
        # Get more results for compression
        initial_results = await self._semantic_search(query, subject, grade, limit=15, student_group_info=student_group_info)
        
        compressed_results = []
        
        for content, metadata, score in initial_results:
            # Compress content to most relevant parts, considering student group context
            compressed_content = await self._compress_content(query, content, student_group_info)
            
            if compressed_content:
                compressed_results.append((compressed_content, metadata, score))
        
        # Convert to RetrievalResult format
        results = []
        for i, (content, metadata, score) in enumerate(compressed_results[:self.retrieval_config["final_top_k"]]):
            student_relevance = self._assess_student_group_relevance(content, student_group_info)
            results.append(RetrievalResult(
                content=content,
                metadata=metadata,
                score=score,
                retrieval_method="contextual_compression",
                relevance_explanation=f"Compressed from {len(initial_results)} initial results",
                student_group_relevance=student_relevance
            ))
        
        return results
    
    # Helper methods
    
    async def _semantic_search(self, query: str, subject: str, grade: str, limit: int = 5, student_group_info: str = "") -> List[Tuple[str, Dict, float]]:
        """Basic semantic search with student group context"""
        query_embedding = self.rag_service.embeddings.embed_query(query)
        
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=self._build_metadata_filter(subject, grade),
            limit=limit
        )
        
        results = []
        for point in search_result:
            results.append((
                point.payload.get("text", ""),
                {k: v for k, v in point.payload.items() if k != "text"},
                point.score
            ))
        
        return results
    
    async def _bm25_search(self, query: str, subject: str, grade: str, limit: int = 5, student_group_info: str = "") -> List[Tuple[str, Dict, float]]:
        """BM25 keyword search with student group context"""
        # This would require building a BM25 index from your documents
        # For now, return empty results
        return []
    
    def _build_metadata_filter(self, subject: str, grade: str) -> Optional[Filter]:
        """Build basic metadata filter"""
        conditions = []
        
        if subject:
            conditions.append(FieldCondition(key="subject", match=MatchValue(value=subject)))
        if grade:
            conditions.append(FieldCondition(key="grade", match=MatchValue(value=grade)))
        
        if conditions:
            return Filter(must=conditions)
        return None
    
    def _build_advanced_metadata_filter(self, query: str, subject: str, grade: str, student_group_info: str = "") -> Optional[Filter]:
        """Build advanced metadata filter with domain/cluster matching and student group context"""
        conditions = []
        
        # Basic filters
        if subject:
            conditions.append(FieldCondition(key="subject", match=MatchValue(value=subject)))
        if grade:
            conditions.append(FieldCondition(key="grade", match=MatchValue(value=grade)))
        
        # Extract domain/cluster from query for additional filtering
        query_lower = query.lower()
        
        # Domain-specific filtering
        if "fractions" in query_lower or "decimals" in query_lower:
            conditions.append(FieldCondition(key="domain", match=MatchValue(value="Number and Operations")))
        elif "geometry" in query_lower or "area" in query_lower:
            conditions.append(FieldCondition(key="domain", match=MatchValue(value="Geometry")))
        
        # Student group specific filtering
        if student_group_info:
            if "ESL" in student_group_info or "English language" in student_group_info:
                # Prefer visual and hands-on resources
                pass  # Could add specific filters here
            elif "ADHD" in student_group_info:
                # Prefer interactive and movement-based resources
                pass  # Could add specific filters here
        
        if conditions:
            return Filter(must=conditions)
        return None
    
    def _assess_student_group_relevance(self, content: str, student_group_info: str) -> Optional[str]:
        """Assess how relevant content is to specific student group needs"""
        if not student_group_info:
            return None
        
        content_lower = content.lower()
        relevance_factors = []
        
        if "ESL" in student_group_info or "English language" in student_group_info:
            if any(term in content_lower for term in ["visual", "hands-on", "multimodal", "support", "accommodation"]):
                relevance_factors.append("Visual/kinesthetic support")
        
        if "ADHD" in student_group_info:
            if any(term in content_lower for term in ["movement", "kinesthetic", "interactive", "short", "active"]):
                relevance_factors.append("Movement-based learning")
        
        if "learning disability" in student_group_info:
            if any(term in content_lower for term in ["differentiated", "accommodation", "alternative", "support", "modified"]):
                relevance_factors.append("Differentiated instruction")
        
        if "gifted" in student_group_info:
            if any(term in content_lower for term in ["advanced", "challenge", "enrichment", "extension", "complex"]):
                relevance_factors.append("Advanced content")
        
        return "; ".join(relevance_factors) if relevance_factors else None
    
    def _combine_results(self, results1: List, results2: List, alpha: float = 0.7) -> List[Tuple[str, Dict, float]]:
        """Combine results from different retrieval methods"""
        combined = {}
        
        # Add results from first method
        for content, metadata, score in results1:
            key = content[:100]  # Use first 100 chars as key
            combined[key] = (content, metadata, score * alpha)
        
        # Add results from second method
        for content, metadata, score in results2:
            key = content[:100]
            if key in combined:
                # Combine scores
                existing_content, existing_metadata, existing_score = combined[key]
                combined[key] = (content, metadata, existing_score + score * (1 - alpha))
            else:
                combined[key] = (content, metadata, score * (1 - alpha))
        
        # Sort by combined score
        sorted_results = sorted(combined.values(), key=lambda x: x[2], reverse=True)
        return sorted_results
    
    def _deduplicate_and_rank(self, results: List) -> List[Tuple[str, Dict, float]]:
        """Deduplicate results and rank by score"""
        seen = set()
        deduplicated = []
        
        for result in results:
            if isinstance(result, dict):
                content = result["content"]
                metadata = result["metadata"]
                score = result["score"]
            else:
                content, metadata, score = result
            
            key = content[:100]
            if key not in seen:
                seen.add(key)
                deduplicated.append((content, metadata, score))
        
        # Sort by score
        deduplicated.sort(key=lambda x: x[2], reverse=True)
        return deduplicated
    
    async def _generate_query_expansions(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[str]:
        """Generate expanded queries including student group specific expansions"""
        expansions = [query]  # Original query
        
        # Add subject-specific expansions
        if "objectives" in query.lower():
            expansions.extend([
                f"{subject} {grade} learning goals",
                f"{subject} {grade} educational outcomes",
                f"{subject} {grade} student expectations"
            ])
        
        if "assessment" in query.lower():
            expansions.extend([
                f"{subject} {grade} evaluation methods",
                f"{subject} {grade} testing strategies",
                f"{subject} {grade} student assessment"
            ])
        
        if "materials" in query.lower() or "resources" in query.lower():
            expansions.extend([
                f"{subject} {grade} teaching materials",
                f"{subject} {grade} educational resources",
                f"{subject} {grade} classroom supplies"
            ])
        
        # Add student group specific expansions
        if student_group_info:
            if "ESL" in student_group_info:
                expansions.extend([
                    f"{query} visual supports",
                    f"{query} hands-on activities",
                    f"{query} multimodal learning"
                ])
            elif "ADHD" in student_group_info:
                expansions.extend([
                    f"{query} movement activities",
                    f"{query} interactive learning",
                    f"{query} kinesthetic approaches"
                ])
            elif "learning disability" in student_group_info:
                expansions.extend([
                    f"{query} differentiated instruction",
                    f"{query} accommodations",
                    f"{query} alternative methods"
                ])
            elif "gifted" in student_group_info:
                expansions.extend([
                    f"{query} enrichment activities",
                    f"{query} advanced challenges",
                    f"{query} extension projects"
                ])
        
        return expansions[:self.retrieval_config["expansion_queries"]]
    
    async def _compress_content(self, query: str, content: str, student_group_info: str = "") -> str:
        """Compress content to most relevant parts, considering student group context"""
        # Simple compression - extract sentences containing query terms
        query_terms = query.lower().split()
        sentences = content.split('. ')
        
        relevant_sentences = []
        for sentence in sentences:
            if any(term in sentence.lower() for term in query_terms):
                relevant_sentences.append(sentence)
        
        # Also look for student group relevant sentences
        if student_group_info:
            student_terms = []
            if "ESL" in student_group_info:
                student_terms.extend(["visual", "hands-on", "support", "accommodation"])
            elif "ADHD" in student_group_info:
                student_terms.extend(["movement", "interactive", "kinesthetic", "active"])
            elif "learning disability" in student_group_info:
                student_terms.extend(["differentiated", "accommodation", "alternative", "support"])
            elif "gifted" in student_group_info:
                student_terms.extend(["advanced", "challenge", "enrichment", "extension"])
            
            for sentence in sentences:
                if any(term in sentence.lower() for term in student_terms):
                    relevant_sentences.append(sentence)
        
        if relevant_sentences:
            return '. '.join(relevant_sentences[:3])  # Top 3 relevant sentences
        else:
            return content[:200]  # Fallback to first 200 chars
    
    async def _basic_retrieval(self, query: str, subject: str, grade: str, student_group_info: str = "") -> List[RetrievalResult]:
        """Fallback to basic retrieval with student group context"""
        results = await self._semantic_search(query, subject, grade, limit=self.retrieval_config["final_top_k"], student_group_info=student_group_info)
        
        retrieval_results = []
        for content, metadata, score in results:
            student_relevance = self._assess_student_group_relevance(content, student_group_info)
            retrieval_results.append(RetrievalResult(
                content=content,
                metadata=metadata,
                score=score,
                retrieval_method="basic",
                relevance_explanation="Basic semantic search",
                student_group_relevance=student_relevance
            ))
        
        return retrieval_results

# Integration with existing RAG service
class EnhancedRAGService:
    """Enhanced RAG service with advanced retrieval - Updated for v2.0"""
    
    def __init__(self, original_rag_service):
        self.original_rag_service = original_rag_service
        self.advanced_retriever = AdvancedRetriever(original_rag_service)
        
        # Retrieval strategy configuration
        self.strategy_config = {
            "default_strategy": RetrievalStrategy.HYBRID_SEARCH,
            "fallback_strategy": RetrievalStrategy.HYBRID_SEARCH,
            "experimental_strategies": [
                RetrievalStrategy.RERANKING,
                RetrievalStrategy.QUERY_EXPANSION,
                RetrievalStrategy.HIERARCHICAL,
                RetrievalStrategy.STUDENT_GROUP_AWARE,
                RetrievalStrategy.EXTERNAL_RESOURCE_FOCUSED
            ]
        }
    
    async def retrieve_relevant_standards_advanced(
        self, 
        query: str, 
        subject: str, 
        grade: str, 
        strategy: RetrievalStrategy = None,
        student_group_info: str = "",
        **kwargs
    ) -> List[Dict]:
        """
        Enhanced retrieval with advanced strategies
        Updated to include student group information
        """
        
        if strategy is None:
            strategy = self.strategy_config["default_strategy"]
        
        try:
            # Use advanced retrieval
            results = await self.advanced_retriever.advanced_retrieve(
                query, subject, grade, strategy, student_group_info, **kwargs
            )
            
            # Convert to original format for compatibility
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "standard_id": result.metadata.get("standard_id", f"advanced_{result.retrieval_method}"),
                    "description": result.content,
                    "subject": subject,
                    "grade": grade,
                    "source": result.metadata.get("source", "Advanced Retrieval"),
                    "resource_url": result.metadata.get("resource_url", ""),
                    "resource_title": result.metadata.get("resource_title", ""),
                    "resource_type": result.metadata.get("type", "standard"),
                    "score": result.score,
                    "domain": result.metadata.get("domain", ""),
                    "cluster": result.metadata.get("cluster", ""),
                    "retrieval_method": result.retrieval_method,
                    "relevance_explanation": result.relevance_explanation,
                    "student_group_relevance": result.student_group_relevance,
                    "external_resource_type": result.external_resource_type
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Advanced retrieval failed: {e}, falling back to basic retrieval")
            return await self.original_rag_service.retrieve_relevant_standards(query, subject, grade)
    
    async def compare_retrieval_strategies(
        self, 
        query: str, 
        subject: str, 
        grade: str,
        student_group_info: str = ""
    ) -> Dict[str, List[Dict]]:
        """
        Compare different retrieval strategies for analysis
        Updated to include student group context
        """
        
        strategies_to_test = [
            RetrievalStrategy.HYBRID_SEARCH,
            RetrievalStrategy.MULTI_VECTOR,
            RetrievalStrategy.QUERY_EXPANSION,
            RetrievalStrategy.RERANKING,
            RetrievalStrategy.HIERARCHICAL,
            RetrievalStrategy.METADATA_FILTERED,
            RetrievalStrategy.STUDENT_GROUP_AWARE,
            RetrievalStrategy.EXTERNAL_RESOURCE_FOCUSED
        ]
        
        results = {}
        
        for strategy in strategies_to_test:
            try:
                strategy_results = await self.retrieve_relevant_standards_advanced(
                    query, subject, grade, strategy, student_group_info
                )
                results[strategy.value] = strategy_results
                print(f"✅ {strategy.value}: {len(strategy_results)} results")
            except Exception as e:
                print(f"❌ {strategy.value}: {e}")
                results[strategy.value] = []
        
        return results