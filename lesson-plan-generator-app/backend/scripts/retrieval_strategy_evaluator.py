# scripts/retrieval_strategy_evaluator.py
import asyncio
import json
import pandas as pd
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import advanced retrieval components
try:
    from app.advanced_retrieval import RetrievalStrategy, EnhancedRAGService
    from app.rag_service import RAGService
    ADVANCED_RETRIEVAL_AVAILABLE = True
except ImportError:
    print("⚠️  Advanced retrieval not available. Using mock service.")
    ADVANCED_RETRIEVAL_AVAILABLE = False

class RetrievalStrategyEvaluator:
    """Evaluate different retrieval strategies using RAGAS metrics - Updated for v2.0"""
    
    def __init__(self, enhanced_rag_service):
        self.enhanced_rag_service = enhanced_rag_service
        self.evaluation_results = {}
    
    def load_test_queries(self, dataset_path: str = "realistic_golden_dataset_ragas_evaluation_v3.json") -> List[Dict[str, str]]:
        """Load test queries from golden dataset"""
        
        if os.path.exists(dataset_path):
            print(f"📁 Loading test queries from {dataset_path}")
            with open(dataset_path, 'r') as f:
                dataset = json.load(f)
            
            test_queries = []
            for sample in dataset["samples"][:15]:  # Test with first 15 samples for better evaluation
                test_queries.append({
                    "question": sample["question"],
                    "subject": sample["metadata"]["subject"],
                    "grade": sample["metadata"]["grade_level"],
                    "topic": sample["metadata"]["topic"],
                    "question_type": sample["metadata"]["question_type"],
                    "student_group_info": sample["metadata"].get("student_group_info", ""),
                    "contexts": sample["contexts"]
                })
            
            print(f"✅ Loaded {len(test_queries)} test queries")
            return test_queries
        
        else:
            print(f"❌ {dataset_path} not found!")
            return []
    
    async def evaluate_strategies(self, test_queries: List[Dict[str, str]]) -> Dict[str, Any]:
        """Evaluate all retrieval strategies on test queries"""
        
        print("🔬 Evaluating Retrieval Strategies (v2.0)...")
        print("=" * 60)
        
        strategies = [
            "hybrid_search",
            "multi_vector", 
            "query_expansion",
            "reranking",
            "hierarchical",
            "metadata_filtered",
            "temporal",
            "contextual_compression",
            "student_group_aware",  # New strategy
            "external_resource_focused"  # New strategy
        ]
        
        results = {}
        
        for strategy in strategies:
            print(f"\n📊 Evaluating {strategy}...")
            try:
                strategy_results = await self._evaluate_strategy(strategy, test_queries)
                results[strategy] = strategy_results
                
                # Print summary
                avg_precision = strategy_results.get("avg_context_precision", 0)
                avg_recall = strategy_results.get("avg_context_recall", 0)
                avg_student_relevance = strategy_results.get("avg_student_relevance", 0)
                avg_external_resource_score = strategy_results.get("avg_external_resource_score", 0)
                
                print(f"   Context Precision: {avg_precision:.3f}")
                print(f"   Context Recall: {avg_recall:.3f}")
                if avg_student_relevance > 0:
                    print(f"   Student Group Relevance: {avg_student_relevance:.3f}")
                if avg_external_resource_score > 0:
                    print(f"   External Resource Score: {avg_external_resource_score:.3f}")
                
            except Exception as e:
                print(f"   ❌ Error evaluating {strategy}: {e}")
                results[strategy] = {
                    "avg_context_precision": 0.0,
                    "avg_context_recall": 0.0,
                    "avg_retrieval_time": 0.0,
                    "avg_result_count": 0.0,
                    "avg_student_relevance": 0.0,
                    "avg_external_resource_score": 0.0,
                    "error": str(e)
                }
        
        # Find best strategy
        valid_results = {k: v for k, v in results.items() if "error" not in v}
        if valid_results:
            best_strategy = max(valid_results.keys(), key=lambda k: valid_results[k].get("avg_context_precision", 0))
            print(f"\n🏆 Best Strategy: {best_strategy}")
            print(f"   Context Precision: {valid_results[best_strategy].get('avg_context_precision', 0):.3f}")
        else:
            print(f"\n⚠️  No strategies evaluated successfully")
        
        return results
    
    async def _evaluate_strategy(self, strategy: str, test_queries: List[Dict[str, str]]) -> Dict[str, Any]:
        """Evaluate a single strategy"""
        
        strategy_results = {
            "context_precision_scores": [],
            "context_recall_scores": [],
            "retrieval_times": [],
            "result_counts": [],
            "student_relevance_scores": [],
            "external_resource_scores": []
        }
        
        for i, query_data in enumerate(test_queries):
            query = query_data["question"]
            subject = query_data["subject"]
            grade = query_data["grade"]
            topic = query_data["topic"]
            question_type = query_data.get("question_type", "")
            student_group_info = query_data.get("student_group_info", "")
            ground_truth_contexts = query_data.get("contexts", [])
            
            print(f"   Testing query {i+1}/{len(test_queries)}: {query[:50]}...")
            
            # Measure retrieval time
            start_time = asyncio.get_event_loop().time()
            
            try:
                # Retrieve using strategy
                retrieved_results = await self.enhanced_rag_service.retrieve_relevant_standards_advanced(
                    query, subject, grade, strategy, student_group_info=student_group_info
                )
                
                end_time = asyncio.get_event_loop().time()
                retrieval_time = end_time - start_time
                
                # Calculate precision and recall
                precision, recall = self._calculate_precision_recall(
                    retrieved_results, ground_truth_contexts
                )
                
                # Calculate student group relevance score
                student_relevance = self._calculate_student_group_relevance(
                    retrieved_results, student_group_info, question_type
                )
                
                # Calculate external resource score
                external_resource_score = self._calculate_external_resource_score(
                    retrieved_results, question_type
                )
                
                strategy_results["context_precision_scores"].append(precision)
                strategy_results["context_recall_scores"].append(recall)
                strategy_results["retrieval_times"].append(retrieval_time)
                strategy_results["result_counts"].append(len(retrieved_results))
                strategy_results["student_relevance_scores"].append(student_relevance)
                strategy_results["external_resource_scores"].append(external_resource_score)
                
            except Exception as e:
                print(f"     ❌ Error with query {i+1}: {e}")
                # Use mock values for failed queries
                strategy_results["context_precision_scores"].append(0.0)
                strategy_results["context_recall_scores"].append(0.0)
                strategy_results["retrieval_times"].append(0.0)
                strategy_results["result_counts"].append(0)
                strategy_results["student_relevance_scores"].append(0.0)
                strategy_results["external_resource_scores"].append(0.0)
        
        # Calculate averages
        if strategy_results["context_precision_scores"]:
            strategy_results["avg_context_precision"] = sum(strategy_results["context_precision_scores"]) / len(strategy_results["context_precision_scores"])
            strategy_results["avg_context_recall"] = sum(strategy_results["context_recall_scores"]) / len(strategy_results["context_recall_scores"])
            strategy_results["avg_retrieval_time"] = sum(strategy_results["retrieval_times"]) / len(strategy_results["retrieval_times"])
            strategy_results["avg_result_count"] = sum(strategy_results["result_counts"]) / len(strategy_results["result_counts"])
            strategy_results["avg_student_relevance"] = sum(strategy_results["student_relevance_scores"]) / len(strategy_results["student_relevance_scores"])
            strategy_results["avg_external_resource_score"] = sum(strategy_results["external_resource_scores"]) / len(strategy_results["external_resource_scores"])
        else:
            strategy_results["avg_context_precision"] = 0.0
            strategy_results["avg_context_recall"] = 0.0
            strategy_results["avg_retrieval_time"] = 0.0
            strategy_results["avg_result_count"] = 0.0
            strategy_results["avg_student_relevance"] = 0.0
            strategy_results["avg_external_resource_score"] = 0.0
        
        return strategy_results
    
    def _calculate_precision_recall(self, retrieved_results: List[Dict], ground_truth_contexts: List[Dict]) -> tuple:
        """Calculate precision and recall for retrieved results"""
        
        if not retrieved_results or not ground_truth_contexts:
            return 0.0, 0.0
        
        # Extract text from retrieved results
        retrieved_texts = [result.get("description", "") for result in retrieved_results]
        
        # Extract text from ground truth contexts
        gt_texts = [ctx.get("text", "") for ctx in ground_truth_contexts]
        
        # Simple overlap-based precision and recall
        relevant_retrieved = 0
        for retrieved_text in retrieved_texts:
            if any(self._text_overlap(retrieved_text, gt_text) > 0.3 for gt_text in gt_texts):
                relevant_retrieved += 1
        
        precision = relevant_retrieved / len(retrieved_texts) if retrieved_texts else 0.0
        
        # Recall: how many ground truth contexts were retrieved
        retrieved_gt = 0
        for gt_text in gt_texts:
            if any(self._text_overlap(gt_text, retrieved_text) > 0.3 for retrieved_text in retrieved_texts):
                retrieved_gt += 1
        
        recall = retrieved_gt / len(gt_texts) if gt_texts else 0.0
        
        return precision, recall
    
    def _calculate_student_group_relevance(self, retrieved_results: List[Dict], student_group_info: str, question_type: str) -> float:
        """Calculate how relevant results are to student group needs"""
        
        if not student_group_info or not retrieved_results:
            return 0.0
        
        relevance_scores = []
        
        for result in retrieved_results:
            content = result.get("description", "").lower()
            relevance_score = 0.0
            
            # Check for student group specific relevance
            if "ESL" in student_group_info or "English language" in student_group_info:
                if any(term in content for term in ["visual", "hands-on", "multimodal", "support", "accommodation", "simplified"]):
                    relevance_score += 0.3
            
            if "ADHD" in student_group_info:
                if any(term in content for term in ["movement", "kinesthetic", "interactive", "short", "active", "engaging"]):
                    relevance_score += 0.3
            
            if "learning disability" in student_group_info:
                if any(term in content for term in ["differentiated", "accommodation", "alternative", "support", "modified", "adapted"]):
                    relevance_score += 0.3
            
            if "gifted" in student_group_info:
                if any(term in content for term in ["advanced", "challenge", "enrichment", "extension", "complex", "sophisticated"]):
                    relevance_score += 0.3
            
            # Check for question type relevance
            if question_type == "learning_objectives" and any(term in content for term in ["objective", "goal", "outcome", "expectation"]):
                relevance_score += 0.2
            elif question_type == "assessment_strategies" and any(term in content for term in ["assessment", "evaluation", "test", "measure"]):
                relevance_score += 0.2
            elif question_type == "materials_resources" and any(term in content for term in ["material", "resource", "tool", "supply"]):
                relevance_score += 0.2
            
            relevance_scores.append(min(relevance_score, 1.0))
        
        return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    def _calculate_external_resource_score(self, retrieved_results: List[Dict], question_type: str) -> float:
        """Calculate how well results include external resources"""
        
        if not retrieved_results:
            return 0.0
        
        external_resource_scores = []
        
        for result in retrieved_results:
            score = 0.0
            
            # Check for external resource indicators
            source = result.get("source", "").lower()
            resource_url = result.get("resource_url", "")
            resource_type = result.get("resource_type", "").lower()
            
            # Boost external resources
            if source in ["youtube", "wikipedia", "interactive", "assessment"]:
                score += 0.4
            elif source in ["common core", "ngss", "nasa"]:
                score += 0.3
            
            # Boost resources with actual URLs
            if resource_url and not resource_url.startswith("example"):
                score += 0.3
            
            # Boost specific resource types
            if resource_type in ["educational video", "interactive tool", "assessment material"]:
                score += 0.2
            
            # Boost for question types that benefit from external resources
            if question_type == "external_resources":
                score += 0.3
            elif question_type in ["materials_resources", "assessment_strategies"]:
                score += 0.2
            
            external_resource_scores.append(min(score, 1.0))
        
        return sum(external_resource_scores) / len(external_resource_scores) if external_resource_scores else 0.0
    
    def _text_overlap(self, text1: str, text2: str) -> float:
        """Calculate text overlap between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

# Enhanced Mock RAG Service for testing with realistic results
class MockEnhancedRAGService:
    """Mock enhanced RAG service with realistic performance variations - Updated for v2.0"""
    
    def __init__(self):
        # Different strategies have different performance characteristics
        self.strategy_performance = {
            "hybrid_search": {
                "precision": 0.85,
                "recall": 0.78,
                "variation": 0.05,
                "result_count": 4,
                "student_relevance": 0.3,
                "external_resource_score": 0.4
            },
            "multi_vector": {
                "precision": 0.82,
                "recall": 0.80,
                "variation": 0.04,
                "result_count": 5,
                "student_relevance": 0.2,
                "external_resource_score": 0.3
            },
            "query_expansion": {
                "precision": 0.80,
                "recall": 0.85,
                "variation": 0.06,
                "result_count": 6,
                "student_relevance": 0.4,
                "external_resource_score": 0.5
            },
            "reranking": {
                "precision": 0.90,
                "recall": 0.75,
                "variation": 0.03,
                "result_count": 3,
                "student_relevance": 0.3,
                "external_resource_score": 0.3
            },
            "hierarchical": {
                "precision": 0.87,
                "recall": 0.82,
                "variation": 0.04,
                "result_count": 5,
                "student_relevance": 0.5,
                "external_resource_score": 0.4
            },
            "metadata_filtered": {
                "precision": 0.88,
                "recall": 0.77,
                "variation": 0.03,
                "result_count": 4,
                "student_relevance": 0.4,
                "external_resource_score": 0.3
            },
            "temporal": {
                "precision": 0.83,
                "recall": 0.79,
                "variation": 0.05,
                "result_count": 4,
                "student_relevance": 0.2,
                "external_resource_score": 0.6
            },
            "contextual_compression": {
                "precision": 0.84,
                "recall": 0.81,
                "variation": 0.04,
                "result_count": 4,
                "student_relevance": 0.3,
                "external_resource_score": 0.3
            },
            "student_group_aware": {  # New strategy
                "precision": 0.92,
                "recall": 0.85,
                "variation": 0.02,
                "result_count": 4,
                "student_relevance": 0.8,
                "external_resource_score": 0.4
            },
            "external_resource_focused": {  # New strategy
                "precision": 0.89,
                "recall": 0.83,
                "variation": 0.03,
                "result_count": 5,
                "student_relevance": 0.3,
                "external_resource_score": 0.9
            }
        }
    
    async def retrieve_relevant_standards_advanced(self, query: str, subject: str, grade: str, strategy: str, student_group_info: str = "") -> List[Dict]:
        """Mock retrieval method with realistic performance variations"""
        
        # Simulate retrieval delay
        await asyncio.sleep(0.1)
        
        # Get strategy performance characteristics
        perf = self.strategy_performance.get(strategy, self.strategy_performance["hybrid_search"])
        
        # Generate mock results with realistic variations
        result_count = perf["result_count"]
        mock_results = []
        
        for i in range(result_count):
            # Create realistic mock content based on query
            if "fractions" in query.lower():
                content = f"CCSS.MATH.{grade.split()[0]}.NF.{i+1}: Mathematical concepts related to fractions and number operations."
            elif "photosynthesis" in query.lower():
                content = f"NGSS MS-LS1-{i+1}: Scientific concepts related to photosynthesis and energy flow."
            elif "poetry" in query.lower():
                content = f"CCSS.ELA-LITERACY.RL.{grade.split()[0]}.{i+1}: Literary analysis concepts for poetry interpretation."
            elif "geometry" in query.lower():
                content = f"CCSS.MATH.{grade.split()[0]}.G.{i+1}: Geometric concepts and spatial reasoning."
            elif "assessment" in query.lower():
                content = f"Assessment strategies for {subject} in {grade} focusing on student evaluation methods."
            elif "materials" in query.lower():
                content = f"Essential materials and resources for {subject} instruction in {grade}."
            elif "differentiation" in query.lower():
                content = f"Differentiation strategies for diverse learners in {subject} at {grade} level."
            elif "external" in query.lower() or "resources" in query.lower():
                content = f"External resources including YouTube videos, Wikipedia articles, and interactive tools for {subject} in {grade}."
            else:
                content = f"Educational standards and concepts for {subject} in {grade}."
            
            # Add student group considerations for new strategies
            if strategy == "student_group_aware" and student_group_info:
                if "ESL" in student_group_info:
                    content += f" Includes visual supports and hands-on activities for English language learners."
                elif "ADHD" in student_group_info:
                    content += f" Features movement-based and interactive learning approaches."
                elif "learning disability" in student_group_info:
                    content += f" Provides differentiated instruction and accommodations."
                elif "gifted" in student_group_info:
                    content += f" Offers advanced challenges and enrichment opportunities."
            
            if strategy == "external_resource_focused":
                if i == 0:
                    content += f" YouTube educational video: Interactive lesson on {subject.lower()} concepts."
                elif i == 1:
                    content += f" Wikipedia article: Comprehensive overview of {subject.lower()} topics."
                elif i == 2:
                    content += f" Interactive tool: Hands-on learning experience for students."
            
            # Determine resource type and source
            resource_type = "standard"
            source = "Common Core"
            resource_url = ""
            
            if strategy == "external_resource_focused":
                if i == 0:
                    resource_type = "Educational Video"
                    source = "YouTube"
                    resource_url = "https://www.youtube.com/watch?v=example"
                elif i == 1:
                    resource_type = "Wikipedia Article"
                    source = "Wikipedia"
                    resource_url = f"https://en.wikipedia.org/wiki/{subject.lower()}"
                elif i == 2:
                    resource_type = "Interactive Tool"
                    source = "Interactive"
                    resource_url = "https://interactive-tool.example.com"
            
            mock_results.append({
                "description": content,
                "score": 0.9 - (i * 0.1),  # Decreasing scores
                "subject": subject,
                "grade": grade,
                "source": source,
                "resource_type": resource_type,
                "resource_url": resource_url,
                "retrieval_method": strategy,
                "student_group_aware": strategy == "student_group_aware",
                "external_resource_focused": strategy == "external_resource_focused"
            })
        
        return mock_results

async def main():
    """Main evaluation function"""
    
    print("🚀 Starting Retrieval Strategy Evaluation (v2.0)...")
    print("=" * 60)
    
    # Initialize evaluator with appropriate service
    if ADVANCED_RETRIEVAL_AVAILABLE:
        try:
            # Try to use real RAG service
            rag_service = RAGService()
            await rag_service.initialize_vectorstore()
            enhanced_rag_service = EnhancedRAGService(rag_service)
            print("✅ Using real advanced RAG service")
        except Exception as e:
            print(f"⚠️  Real RAG service failed: {e}")
            print("   Falling back to mock service")
            enhanced_rag_service = MockEnhancedRAGService()
    else:
        print("⚠️  Using mock RAG service (advanced retrieval not available)")
        enhanced_rag_service = MockEnhancedRAGService()
    
    evaluator = RetrievalStrategyEvaluator(enhanced_rag_service)
    
    # Load test queries from your golden dataset
    test_queries = evaluator.load_test_queries()
    
    if not test_queries:
        print("❌ No test queries loaded. Exiting.")
        return
    
    print(f"📊 Testing with {len(test_queries)} queries from golden dataset")
    
    # Count queries with student group info
    student_group_queries = len([q for q in test_queries if q.get("student_group_info")])
    print(f"👥 Queries with student group info: {student_group_queries}")
    
    # Count queries by type
    question_types = {}
    for query in test_queries:
        q_type = query.get("question_type", "unknown")
        question_types[q_type] = question_types.get(q_type, 0) + 1
    print(f"📋 Question types: {question_types}")
    
    # Evaluate strategies
    results = await evaluator.evaluate_strategies(test_queries)
    
    # Create results table
    results_data = []
    for strategy, metrics in results.items():
        if "error" not in metrics:
            results_data.append({
                "Strategy": strategy.replace("_", " ").title(),
                "Context Precision": f"{metrics['avg_context_precision']:.3f}",
                "Context Recall": f"{metrics['avg_context_recall']:.3f}",
                "Student Relevance": f"{metrics['avg_student_relevance']:.3f}",
                "External Resources": f"{metrics['avg_external_resource_score']:.3f}",
                "Avg Retrieval Time (s)": f"{metrics['avg_retrieval_time']:.3f}",
                "Avg Results Count": f"{metrics['avg_result_count']:.1f}"
            })
        else:
            results_data.append({
                "Strategy": strategy.replace("_", " ").title(),
                "Context Precision": "Error",
                "Context Recall": "Error",
                "Student Relevance": "Error",
                "External Resources": "Error",
                "Avg Retrieval Time (s)": "Error",
                "Avg Results Count": "Error"
            })
    
    df = pd.DataFrame(results_data)
    df = df.sort_values("Context Precision", ascending=False)
    
    print("\n📊 RETRIEVAL STRATEGY COMPARISON (v2.0)")
    print("=" * 100)
    print(df.to_string(index=False))
    
    # Save results
    with open("retrieval_strategy_evaluation.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    df.to_csv("retrieval_strategy_comparison.csv", index=False)
    
    print(f"\n✅ Evaluation completed!")
    print(f"📁 Results saved to: retrieval_strategy_evaluation.json")
    print(f"📊 Table saved to: retrieval_strategy_comparison.csv")
    
    # Print analysis and recommendations
    print(f"\n💡 ANALYSIS & RECOMMENDATIONS (v2.0):")
    print("-" * 50)
    
    # Find top performers
    valid_results = {k: v for k, v in results.items() if "error" not in v}
    if valid_results:
        best_precision = max(valid_results.keys(), key=lambda k: valid_results[k].get("avg_context_precision", 0))
        best_recall = max(valid_results.keys(), key=lambda k: valid_results[k].get("avg_context_recall", 0))
        best_student_relevance = max(valid_results.keys(), key=lambda k: valid_results[k].get("avg_student_relevance", 0))
        best_external_resources = max(valid_results.keys(), key=lambda k: valid_results[k].get("avg_external_resource_score", 0))
        
        print(f"🎯 Best Precision: {best_precision.replace('_', ' ').title()} ({valid_results[best_precision]['avg_context_precision']:.3f})")
        print(f"🎯 Best Recall: {best_recall.replace('_', ' ').title()} ({valid_results[best_recall]['avg_context_recall']:.3f})")
        print(f"👥 Best Student Relevance: {best_student_relevance.replace('_', ' ').title()} ({valid_results[best_student_relevance]['avg_student_relevance']:.3f})")
        print(f"🔗 Best External Resources: {best_external_resources.replace('_', ' ').title()} ({valid_results[best_external_resources]['avg_external_resource_score']:.3f})")
        
        # Strategy-specific recommendations
        print(f"\n🔧 STRATEGY-SPECIFIC RECOMMENDATIONS:")
        print(f"1. For highest precision: Use {best_precision.replace('_', ' ').title()}")
        print(f"2. For best recall: Use {best_recall.replace('_', ' ').title()}")
        print(f"3. For inclusive lesson planning: Use {best_student_relevance.replace('_', ' ').title()}")
        print(f"4. For rich resource integration: Use {best_external_resources.replace('_', ' ').title()}")
        
        # Performance thresholds
        print(f"\n📊 PERFORMANCE THRESHOLDS:")
        high_precision_strategies = [k for k, v in valid_results.items() if v.get('avg_context_precision', 0) > 0.85]
        high_recall_strategies = [k for k, v in valid_results.items() if v.get('avg_context_recall', 0) > 0.80]
        high_student_relevance_strategies = [k for k, v in valid_results.items() if v.get('avg_student_relevance', 0) > 0.60]
        high_external_resource_strategies = [k for k, v in valid_results.items() if v.get('avg_external_resource_score', 0) > 0.70]
        
        print(f"   High Precision (>0.85): {len(high_precision_strategies)} strategies")
        print(f"   High Recall (>0.80): {len(high_recall_strategies)} strategies")
        print(f"   High Student Relevance (>0.60): {len(high_student_relevance_strategies)} strategies")
        print(f"   High External Resources (>0.70): {len(high_external_resource_strategies)} strategies")
    
    print(f"\n📈 NEXT STEPS:")
    print(f"1. Install advanced retrieval dependencies: pip install sentence-transformers rank-bm25 faiss-cpu")
    print(f"2. Implement the top-performing strategies in your RAG system")
    print(f"3. Run evaluation with actual RAG system for real metrics")
    print(f"4. Monitor performance improvements in RAGAS evaluation")
    print(f"5. Test student group awareness and external resource integration")
    print(f"6. Consider hybrid approaches combining multiple strategies")

if __name__ == "__main__":
    asyncio.run(main())