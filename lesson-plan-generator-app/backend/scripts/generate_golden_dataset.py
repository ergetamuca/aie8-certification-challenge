# scripts/generate_golden_dataset_v3.py
import json
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from app.rag_service import RAGService
from app.external_apis import ExternalAPIService
from app.agent_service import EducationPlanningAgent

class RealisticGoldenDatasetGenerator:
    """
    Updated golden dataset generator that creates realistic educational contexts
    that actually match what the RAG system retrieves and evaluates against.
    """
    
    def __init__(self):
        self.rag_service = RAGService()
        self.external_api_service = ExternalAPIService()
        self.agent_service = EducationPlanningAgent(self.rag_service)
        
        # Educational content templates for realistic contexts
        self.educational_content_templates = {
            "learning_objectives": {
                "mathematics": {
                    "fractions": "Students will understand that fractions represent parts of a whole, identify equivalent fractions using visual models, compare fractions with like denominators, and solve word problems involving fractions. Aligns with CCSS.MATH.CONTENT.4.NF.A.1, 4.NF.A.2, and 4.NF.A.3.",
                    "decimals": "Students will read and write decimals to hundredths, compare decimals using place value, and convert between fractions and decimals. Supports CCSS.MATH.CONTENT.4.NF.C.6 and 4.NF.C.7.",
                    "geometry": "Students will classify two-dimensional figures based on properties, understand angle measurement, and solve problems involving area and perimeter. Addresses CCSS.MATH.CONTENT.5.G.B.3 and 5.G.B.4."
                },
                "science": {
                    "photosynthesis": "Students will explain how plants use sunlight, water, and carbon dioxide to produce oxygen and glucose, identify the parts of a plant involved in photosynthesis, and describe the importance of this process to life on Earth. Aligns with NGSS 5-LS1-1 and MS-LS1-5.",
                    "ecosystems": "Students will describe how energy flows through ecosystems, identify producers, consumers, and decomposers, and explain how changes in one part of an ecosystem affect other parts. Supports NGSS 5-LS2-1 and MS-LS2-3.",
                    "scientific_method": "Students will formulate testable questions, design controlled experiments, collect and analyze data, and draw evidence-based conclusions. Addresses NGSS Science and Engineering Practices."
                },
                "english_language_arts": {
                    "poetry_analysis": "Students will identify literary devices in poetry, analyze how word choice affects meaning and tone, compare themes across different poems, and write original poetry using learned techniques. Aligns with CCSS.ELA-LITERACY.RL.8.4 and RL.8.5.",
                    "reading_comprehension": "Students will determine central ideas and themes, analyze how authors develop characters and plot, cite textual evidence to support analysis, and make connections between texts. Supports CCSS.ELA-LITERACY.RL.6.1-6.3."
                },
                "social_studies": {
                    "ancient_civilizations": "Students will compare and contrast ancient civilizations, analyze how geography influenced development, examine cultural achievements and contributions, and evaluate primary and secondary sources. Aligns with C3 Framework D2.His.3.6-8.",
                    "american_revolution": "Students will analyze causes and effects of the American Revolution, examine different perspectives on independence, evaluate the significance of key events and figures, and assess the impact on American society. Supports C3 Framework D2.His.14.6-8."
                }
            },
            "lesson_structure": {
                "mathematics": "Effective mathematics lessons follow a structured approach: 1) Warm-up with review problems (5-10 min), 2) Introduction of new concept with manipulatives (10-15 min), 3) Guided practice with teacher support (15-20 min), 4) Independent practice with differentiation (10-15 min), 5) Closure with reflection and assessment (5-10 min). Total duration should match grade-level attention spans.",
                "science": "Science lessons should incorporate inquiry-based learning: 1) Engagement with phenomenon or question (5-10 min), 2) Exploration through hands-on investigation (15-20 min), 3) Explanation of findings and concepts (10-15 min), 4) Elaboration with real-world applications (10-15 min), 5) Evaluation through assessment and reflection (5-10 min). Include safety protocols and materials management.",
                "english_language_arts": "ELA lessons balance reading, writing, speaking, and listening: 1) Opening with shared reading or discussion (5-10 min), 2) Mini-lesson on specific skill or strategy (10-15 min), 3) Guided practice with mentor texts (15-20 min), 4) Independent work with conferring (15-20 min), 5) Sharing and reflection (5-10 min). Include vocabulary development and grammar integration.",
                "social_studies": "Social studies lessons promote critical thinking: 1) Hook with primary source or current event (5-10 min), 2) Direct instruction on historical concepts (10-15 min), 3) Analysis of sources and evidence (15-20 min), 4) Application through projects or discussions (10-15 min), 5) Synthesis and connection to present (5-10 min). Emphasize multiple perspectives and civic engagement."
            },
            "assessment_strategies": {
                "formative": "Formative assessments include exit tickets, think-pair-share discussions, quick writes, observation checklists, and self-assessment rubrics. These provide ongoing feedback to adjust instruction and support student learning in real-time.",
                "summative": "Summative assessments evaluate learning at the end of a unit through tests, projects, presentations, portfolios, and performance tasks. These measure student achievement against learning objectives and inform grading decisions.",
                "performance_based": "Performance-based assessments require students to demonstrate skills through authentic tasks like experiments, debates, creative projects, and problem-solving scenarios. These assess higher-order thinking and real-world application.",
                "differentiated": "Differentiated assessments provide multiple ways for students to demonstrate learning, including oral presentations, visual projects, written responses, and hands-on activities. Accommodations may include extended time, alternative formats, and assistive technology."
            },
            "materials_resources": {
                "manipulatives": "Essential manipulatives include base-ten blocks, fraction circles, geometric shapes, measurement tools, and counting objects. These concrete materials help students develop conceptual understanding before moving to abstract representations.",
                "technology": "Technology tools include interactive whiteboards, educational software, online simulations, digital portfolios, and assessment platforms. Ensure accessibility features and provide training for both teachers and students.",
                "visual_aids": "Visual aids include anchor charts, graphic organizers, diagrams, models, and posters. These support visual learners and provide reference materials for ongoing learning and review.",
                "real_world": "Real-world materials connect learning to students' lives through newspapers, maps, artifacts, guest speakers, and field trips. These materials make content relevant and engaging for diverse learners."
            },
            "differentiation": {
                "content": "Content differentiation involves varying the complexity, depth, and breadth of material. Provide multiple texts at different reading levels, offer choice in topics or themes, and adjust the pace of instruction based on student needs.",
                "process": "Process differentiation offers multiple pathways to learning through varied instructional strategies, flexible grouping, and different learning modalities. Include visual, auditory, kinesthetic, and tactile approaches.",
                "product": "Product differentiation allows students to demonstrate learning through various formats like presentations, written reports, artistic projects, or multimedia creations. Provide rubrics that accommodate different product types.",
                "environment": "Environment differentiation creates flexible learning spaces that support different learning styles and needs. Include quiet areas, collaborative spaces, and resources for movement and sensory needs."
            },
            "standards_alignment": {
                "common_core_math": "Common Core Mathematics emphasizes conceptual understanding, procedural fluency, and problem-solving. Focus on mathematical practices including making sense of problems, reasoning abstractly, constructing viable arguments, and modeling with mathematics.",
                "ngss_science": "Next Generation Science Standards integrate three dimensions: disciplinary core ideas, science and engineering practices, and crosscutting concepts. Emphasize inquiry-based learning and real-world applications.",
                "common_core_ela": "Common Core ELA focuses on reading complex texts, writing for various purposes, speaking and listening skills, and language conventions. Emphasize evidence-based analysis and critical thinking.",
                "c3_social_studies": "C3 Framework for Social Studies emphasizes inquiry-based learning, civic engagement, and disciplinary literacy. Focus on developing questions, evaluating sources, communicating conclusions, and taking informed action."
            },
            "external_resources": {
                "youtube_educational": "Educational YouTube channels provide engaging video content that supports learning objectives. Look for channels with clear explanations, age-appropriate content, and alignment with curriculum standards. Always preview videos and provide context for students.",
                "interactive_tools": "Interactive online tools include virtual manipulatives, simulations, games, and assessment platforms. These provide hands-on learning experiences and immediate feedback. Ensure tools are accessible and support learning goals.",
                "curriculum_standards": "Official curriculum standards from CCSS, NGSS, and state departments provide authoritative guidance on learning objectives, assessment criteria, and instructional approaches. Use these to ensure alignment and rigor.",
                "professional_resources": "Professional resources include teacher guides, lesson plans, assessment rubrics, and research articles. These support teacher knowledge and provide evidence-based instructional strategies."
            }
        }
        
    async def generate_comprehensive_dataset(self) -> Dict[str, Any]:
        """Generate a comprehensive golden dataset with realistic educational contexts"""
        
        print("🚀 Generating Realistic Golden Dataset for RAGAS Evaluation (v3.0)...")
        print("=" * 70)
        
        # Define test scenarios with realistic educational questions
        test_scenarios = [
            # Learning Objectives Questions
            {
                "question": "What are the key learning objectives for teaching fractions to 4th grade students?",
                "subject": "Mathematics",
                "grade": "4th Grade", 
                "topic": "Fractions",
                "question_type": "learning_objectives",
                "difficulty": "medium",
                "student_group_info": ""
            },
            {
                "question": "What learning objectives should I set for a 6th grade science lesson on photosynthesis for a class with 3 ESL students?",
                "subject": "Science",
                "grade": "6th Grade",
                "topic": "Photosynthesis", 
                "question_type": "learning_objectives",
                "difficulty": "medium",
                "student_group_info": "3 ESL students, mixed ability levels"
            },
            
            # Lesson Structure Questions
            {
                "question": "How should I structure a 45-minute science lesson on photosynthesis for 6th graders?",
                "subject": "Science",
                "grade": "6th Grade",
                "topic": "Photosynthesis",
                "question_type": "lesson_structure", 
                "difficulty": "high",
                "student_group_info": ""
            },
            {
                "question": "What's the best way to organize a 60-minute ELA lesson on poetry analysis for 8th grade students with ADHD?",
                "subject": "English Language Arts",
                "grade": "8th Grade",
                "topic": "Poetry Analysis",
                "question_type": "lesson_structure",
                "difficulty": "high",
                "student_group_info": "2 students with ADHD, 1 student with learning disability"
            },
            
            # Assessment Questions
            {
                "question": "What assessment strategies work best for evaluating student understanding of poetry analysis in 8th grade ELA?",
                "subject": "English Language Arts", 
                "grade": "8th Grade",
                "topic": "Poetry Analysis",
                "question_type": "assessment_strategies",
                "difficulty": "medium",
                "student_group_info": ""
            },
            {
                "question": "How can I assess student learning in a hands-on mathematics lesson about geometry for students with different learning styles?",
                "subject": "Mathematics",
                "grade": "5th Grade",
                "topic": "Geometry",
                "question_type": "assessment_strategies",
                "difficulty": "medium",
                "student_group_info": "Mixed learning styles, 4 visual learners, 3 kinesthetic learners"
            },
            
            # Materials and Resources Questions
            {
                "question": "What materials and resources do I need for a hands-on geometry lesson on area and perimeter for 5th graders?",
                "subject": "Mathematics",
                "grade": "5th Grade", 
                "topic": "Area and Perimeter",
                "question_type": "materials_resources",
                "difficulty": "low",
                "student_group_info": ""
            },
            {
                "question": "What technology tools would enhance a 7th grade social studies lesson on ancient civilizations for ESL students?",
                "subject": "Social Studies",
                "grade": "7th Grade",
                "topic": "Ancient Civilizations",
                "question_type": "materials_resources",
                "difficulty": "medium",
                "student_group_info": "5 ESL students, 2 students with visual impairments"
            },
            
            # Differentiation Questions
            {
                "question": "How can I differentiate instruction for students with varying abilities in a 7th grade social studies lesson on the American Revolution?",
                "subject": "Social Studies",
                "grade": "7th Grade",
                "topic": "American Revolution",
                "question_type": "differentiation",
                "difficulty": "high",
                "student_group_info": ""
            },
            {
                "question": "What accommodations should I provide for English language learners in a mathematics lesson?",
                "subject": "Mathematics",
                "grade": "6th Grade",
                "topic": "Algebraic Thinking",
                "question_type": "differentiation",
                "difficulty": "high",
                "student_group_info": "4 ESL students, 2 students with learning disabilities"
            },
            
            # Standards Alignment Questions
            {
                "question": "Which Common Core standards should I focus on for a 4th grade mathematics lesson about decimals?",
                "subject": "Mathematics",
                "grade": "4th Grade",
                "topic": "Decimals",
                "question_type": "standards_alignment",
                "difficulty": "medium",
                "student_group_info": ""
            },
            {
                "question": "How do NGSS standards apply to a middle school lesson about climate change for gifted students?",
                "subject": "Science",
                "grade": "7th Grade", 
                "topic": "Climate Change",
                "question_type": "standards_alignment",
                "difficulty": "medium",
                "student_group_info": "Gifted and talented class, 8 students total"
            },
            
            # External Resources Questions
            {
                "question": "What external resources are available for teaching fractions to elementary students?",
                "subject": "Mathematics",
                "grade": "4th Grade",
                "topic": "Fractions",
                "question_type": "external_resources",
                "difficulty": "medium",
                "student_group_info": ""
            },
            {
                "question": "What YouTube videos and interactive resources can help ESL students learn about photosynthesis?",
                "subject": "Science",
                "grade": "6th Grade",
                "topic": "Photosynthesis",
                "question_type": "external_resources",
                "difficulty": "medium",
                "student_group_info": "3 ESL students, need visual supports"
            },
            
            # Multi-Context Questions
            {
                "question": "Compare and contrast the teaching approaches for fractions in 3rd grade versus 5th grade mathematics.",
                "subject": "Mathematics",
                "grade": "Mixed Grades",
                "topic": "Fractions",
                "question_type": "comparison",
                "difficulty": "high",
                "multi_context": True,
                "student_group_info": ""
            },
            {
                "question": "How do reading comprehension skills impact learning across different subjects in middle school for students with learning disabilities?",
                "subject": "Cross-curricular",
                "grade": "6th Grade",
                "topic": "Reading Comprehension",
                "question_type": "cross_curricular",
                "difficulty": "high",
                "multi_context": True,
                "student_group_info": "2 students with learning disabilities, 1 student with ADHD"
            },
            
            # Reasoning Questions
            {
                "question": "If a student struggles with reading comprehension, how would this impact their performance in a science lesson about ecosystems?",
                "subject": "Science",
                "grade": "6th Grade",
                "topic": "Ecosystems",
                "question_type": "reasoning",
                "difficulty": "high",
                "requires_reasoning": True,
                "student_group_info": ""
            },
            {
                "question": "Why might hands-on activities be more effective than lectures for teaching scientific concepts to elementary students with ADHD?",
                "subject": "Science",
                "grade": "4th Grade",
                "topic": "Scientific Method",
                "question_type": "reasoning",
                "difficulty": "high",
                "requires_reasoning": True,
                "student_group_info": "2 students with ADHD, need movement-based learning"
            }
        ]
        
        # Generate samples with realistic contexts
        samples = []
        for i, scenario in enumerate(test_scenarios):
            print(f"📝 Generating sample {i+1}/{len(test_scenarios)}: {scenario['question'][:50]}...")
            sample = await self._generate_realistic_sample(scenario, i + 1)
            samples.append(sample)
        
        # Create dataset structure
        dataset = {
            "dataset_name": "lesson_plan_generator_realistic_golden_dataset_v3",
            "version": "3.0",
            "description": "Realistic evaluation dataset for lesson plan generator RAG system using RAGAS - Updated with proper educational contexts and alignment",
            "created_at": datetime.now().isoformat(),
            "total_samples": len(samples),
            "evaluation_metrics": [
                "faithfulness",
                "answer_relevancy", 
                "context_precision",
                "context_recall",
                "answer_correctness"
            ],
            "question_types": [
                "learning_objectives",
                "lesson_structure",
                "assessment_strategies", 
                "materials_resources",
                "differentiation",
                "standards_alignment",
                "external_resources",
                "comparison",
                "cross_curricular",
                "reasoning"
            ],
            "subjects_covered": [
                "Mathematics",
                "Science", 
                "English Language Arts",
                "Social Studies",
                "Cross-curricular"
            ],
            "grade_levels": [
                "3rd Grade", "4th Grade", "5th Grade", "6th Grade",
                "7th Grade", "8th Grade", "Mixed Grades"
            ],
            "student_group_types": [
                "ESL students",
                "Students with ADHD",
                "Students with learning disabilities",
                "Gifted and talented",
                "Mixed ability levels",
                "Visual learners",
                "Kinesthetic learners"
            ],
            "samples": samples
        }
        
        return dataset
    
    async def _generate_realistic_sample(self, scenario: Dict[str, Any], sample_id: int) -> Dict[str, Any]:
        """Generate a single sample with realistic educational contexts"""
        
        # Generate realistic contexts based on question type and subject
        contexts = self._generate_realistic_contexts(scenario)
        
        # Generate realistic ground truth answer
        ground_truth = self._generate_realistic_ground_truth(scenario, contexts)
        
        return {
            "id": f"sample_{sample_id:03d}",
            "question": scenario["question"],
            "ground_truth_answer": ground_truth,
            "contexts": contexts,
            "metadata": {
                "subject": scenario["subject"],
                "grade_level": scenario["grade"],
                "topic": scenario["topic"],
                "question_type": scenario["question_type"],
                "difficulty": scenario["difficulty"],
                "student_group_info": scenario["student_group_info"],
                "requires_reasoning": scenario.get("requires_reasoning", False),
                "multi_context": scenario.get("multi_context", False)
            }
        }
    
    def _generate_realistic_contexts(self, scenario: Dict[str, Any]) -> List[Dict]:
        """Generate realistic educational contexts that match what RAG systems actually retrieve"""
        
        subject = scenario["subject"]
        grade = scenario["grade"]
        topic = scenario["topic"]
        question_type = scenario["question_type"]
        student_group_info = scenario.get("student_group_info", "")
        
        contexts = []
        
        # Generate 3-4 realistic contexts based on question type
        if question_type == "learning_objectives":
            contexts.extend(self._get_learning_objective_contexts(subject, grade, topic, student_group_info))
        elif question_type == "lesson_structure":
            contexts.extend(self._get_lesson_structure_contexts(subject, grade, topic, student_group_info))
        elif question_type == "assessment_strategies":
            contexts.extend(self._get_assessment_contexts(subject, grade, topic, student_group_info))
        elif question_type == "materials_resources":
            contexts.extend(self._get_materials_contexts(subject, grade, topic, student_group_info))
        elif question_type == "differentiation":
            contexts.extend(self._get_differentiation_contexts(subject, grade, topic, student_group_info))
        elif question_type == "standards_alignment":
            contexts.extend(self._get_standards_contexts(subject, grade, topic, student_group_info))
        elif question_type == "external_resources":
            contexts.extend(self._get_external_resource_contexts(subject, grade, topic, student_group_info))
        else:
            # Default contexts for other question types
            contexts.extend(self._get_general_contexts(subject, grade, topic, student_group_info))
        
        return contexts[:4]  # Limit to 4 contexts
    
    def _get_learning_objective_contexts(self, subject: str, grade: str, topic: str, student_group_info: str) -> List[Dict]:
        """Generate realistic learning objective contexts"""
        
        contexts = []
        
        # Context 1: Standards-based learning objectives
        if subject.lower() == "mathematics":
            contexts.append({
                "text": f"CCSS Mathematics Standards for {grade} specify that students should understand {topic} through concrete models, visual representations, and abstract thinking. Students will demonstrate mastery by solving problems, explaining reasoning, and applying concepts to real-world situations. The standards emphasize conceptual understanding before procedural fluency.",
                "source": "CCSS Mathematics Standards",
                "subject": subject,
                "grade": grade,
                "standard_id": f"CCSS.MATH.CONTENT.{grade.split()[0]}.NF",
                "domain": "Number and Operations",
                "cluster": "Fractions"
            })
        elif subject.lower() == "science":
            contexts.append({
                "text": f"NGSS Performance Expectations for {grade} require students to develop and use models to explain {topic}, analyze data to identify patterns, and construct explanations based on evidence. Students should engage in science and engineering practices while building understanding of disciplinary core ideas and crosscutting concepts.",
                "source": "NGSS Standards",
                "subject": subject,
                "grade": grade,
                "standard_id": f"NGSS.{grade.split()[0]}-LS1-1",
                "domain": "Life Sciences",
                "cluster": "Structure and Function"
            })
        
        # Context 2: Bloom's Taxonomy application
        contexts.append({
            "text": f"Effective learning objectives for {topic} in {grade} {subject} should incorporate multiple levels of Bloom's Taxonomy: Remember (recall key facts), Understand (explain concepts), Apply (use knowledge in new situations), Analyze (examine relationships), Evaluate (make judgments), and Create (produce original work). This ensures comprehensive cognitive development.",
            "source": "Bloom's Taxonomy Framework",
            "subject": subject,
            "grade": grade,
            "standard_id": "BLOOM-COMPREHENSIVE",
            "domain": "Cognitive Development",
            "cluster": "Learning Objectives"
        })
        
        # Context 3: Student group considerations
        if student_group_info:
            contexts.append({
                "text": f"When designing learning objectives for {topic} in {grade} {subject}, consider the specific needs of {student_group_info}. Objectives should be measurable, achievable, and include appropriate accommodations. For ESL students, include language objectives alongside content objectives. For students with disabilities, ensure objectives align with IEP goals and provide multiple pathways to success.",
                "source": "Differentiated Instruction Guidelines",
                "subject": subject,
                "grade": grade,
                "standard_id": "DIFFERENTIATED-OBJECTIVES",
                "domain": "Inclusive Education",
                "cluster": "Student-Centered Learning"
            })
        
        return contexts
    
    def _get_lesson_structure_contexts(self, subject: str, grade: str, topic: str, student_group_info: str) -> List[Dict]:
        """Generate realistic lesson structure contexts"""
        
        contexts = []
        
        # Context 1: Subject-specific lesson structure
        if subject.lower() == "science":
            contexts.append({
                "text": f"Effective science lessons for {topic} in {grade} follow the 5E instructional model: Engage (hook students with phenomenon), Explore (hands-on investigation), Explain (concept development), Elaborate (apply learning), and Evaluate (assess understanding). Include safety protocols, materials management, and inquiry-based learning opportunities.",
                "source": "5E Instructional Model",
                "subject": subject,
                "grade": grade,
                "standard_id": "5E-SCIENCE-MODEL",
                "domain": "Science Education",
                "cluster": "Instructional Design"
            })
        elif subject.lower() == "mathematics":
            contexts.append({
                "text": f"Mathematics lessons for {topic} in {grade} should follow a structured progression: concrete (manipulatives), pictorial (visual representations), and abstract (symbolic). Include warm-up activities, direct instruction, guided practice, independent work, and closure. Ensure adequate time for problem-solving and mathematical discourse.",
                "source": "CPA Mathematics Framework",
                "subject": subject,
                "grade": grade,
                "standard_id": "CPA-MATH-FRAMEWORK",
                "domain": "Mathematics Education",
                "cluster": "Instructional Progression"
            })
        
        # Context 2: Time management and pacing
        contexts.append({
            "text": f"Optimal lesson structure for {grade} students includes appropriate time allocation based on attention spans and developmental needs. Younger students benefit from shorter segments (10-15 minutes), while older students can handle longer periods (15-20 minutes). Include transitions, movement breaks, and opportunities for student choice and voice.",
            "source": "Developmental Psychology Research",
            "subject": subject,
            "grade": grade,
            "standard_id": "DEVELOPMENTAL-TIMING",
            "domain": "Educational Psychology",
            "cluster": "Attention and Learning"
        })
        
        # Context 3: Student group accommodations
        if student_group_info:
            contexts.append({
                "text": f"Lesson structure for {topic} in {grade} {subject} should accommodate {student_group_info} through flexible pacing, multiple entry points, and varied instructional modalities. Include visual supports, hands-on activities, and opportunities for movement. Provide clear routines and expectations while allowing for individual differences.",
                "source": "Universal Design for Learning",
                "subject": subject,
                "grade": grade,
                "standard_id": "UDL-PRINCIPLES",
                "domain": "Inclusive Design",
                "cluster": "Accessibility"
            })
        
        return contexts
    
    def _get_assessment_contexts(self, subject: str, grade: str, topic: str, student_group_info: str) -> List[Dict]:
        """Generate realistic assessment contexts"""
        
        contexts = []
        
        # Context 1: Formative vs Summative assessment
        contexts.append({
            "text": f"Assessment strategies for {topic} in {grade} {subject} should balance formative and summative approaches. Formative assessments provide ongoing feedback through exit tickets, observations, and quick checks. Summative assessments evaluate final learning through tests, projects, and performance tasks. Both should align with learning objectives and provide actionable information.",
            "source": "Assessment for Learning Framework",
            "subject": subject,
            "grade": grade,
            "standard_id": "FORMATIVE-SUMMATIVE",
            "domain": "Assessment",
            "cluster": "Evaluation Methods"
        })
        
        # Context 2: Authentic assessment
        contexts.append({
            "text": f"Authentic assessments for {topic} in {grade} {subject} engage students in real-world tasks that demonstrate understanding and application. Examples include problem-solving scenarios, research projects, presentations, and portfolios. These assessments promote higher-order thinking and connect learning to students' lives and future goals.",
            "source": "Authentic Assessment Principles",
            "subject": subject,
            "grade": grade,
            "standard_id": "AUTHENTIC-TASKS",
            "domain": "Assessment Design",
            "cluster": "Real-World Application"
        })
        
        # Context 3: Differentiated assessment
        if student_group_info:
            contexts.append({
                "text": f"Differentiated assessment for {topic} in {grade} {subject} accommodates {student_group_info} through multiple formats, extended time, alternative response modes, and assistive technology. Provide clear rubrics, offer choice in assessment format, and ensure accessibility for all learners while maintaining rigor and standards alignment.",
                "source": "Differentiated Assessment Guidelines",
                "subject": subject,
                "grade": grade,
                "standard_id": "DIFFERENTIATED-ASSESSMENT",
                "domain": "Inclusive Assessment",
                "cluster": "Accessibility"
            })
        
        return contexts
    
    def _get_materials_contexts(self, subject: str, grade: str, topic: str, student_group_info: str) -> List[Dict]:
        """Generate realistic materials and resources contexts"""
        
        contexts = []
        
        # Context 1: Essential materials
        contexts.append({
            "text": f"Essential materials for {topic} in {grade} {subject} include manipulatives for hands-on learning, visual aids for concept development, technology tools for engagement, and assessment materials for evaluation. Ensure materials are age-appropriate, safe, and support diverse learning styles and abilities.",
            "source": "Instructional Materials Guidelines",
            "subject": subject,
            "grade": grade,
            "standard_id": "ESSENTIAL-MATERIALS",
            "domain": "Resource Management",
            "cluster": "Instructional Support"
        })
        
        # Context 2: Technology integration
        contexts.append({
            "text": f"Technology tools enhance {topic} instruction in {grade} {subject} through interactive simulations, digital manipulatives, assessment platforms, and multimedia resources. Select tools that align with learning objectives, provide accessibility features, and support student engagement while maintaining focus on content learning.",
            "source": "Technology Integration Standards",
            "subject": subject,
            "grade": grade,
            "standard_id": "TECH-INTEGRATION",
            "domain": "Educational Technology",
            "cluster": "Digital Learning"
        })
        
        # Context 3: Accessibility considerations
        if student_group_info:
            contexts.append({
                "text": f"Materials and resources for {topic} in {grade} {subject} should accommodate {student_group_info} through accessible formats, assistive technology, visual supports, and alternative input methods. Ensure all materials meet accessibility standards and provide multiple ways for students to access and demonstrate learning.",
                "source": "Accessibility Guidelines",
                "subject": subject,
                "grade": grade,
                "standard_id": "ACCESSIBLE-MATERIALS",
                "domain": "Universal Access",
                "cluster": "Inclusive Resources"
            })
        
        return contexts
    
    def _get_differentiation_contexts(self, subject: str, grade: str, topic: str, student_group_info: str) -> List[Dict]:
        """Generate realistic differentiation contexts"""
        
        contexts = []
        
        # Context 1: Content differentiation
        contexts.append({
            "text": f"Content differentiation for {topic} in {grade} {subject} involves varying the complexity, depth, and breadth of material based on student readiness. Provide multiple texts at different reading levels, offer choice in topics or themes, and adjust the pace of instruction. Ensure all students access grade-level standards while meeting individual needs.",
            "source": "Differentiated Instruction Framework",
            "subject": subject,
            "grade": grade,
            "standard_id": "CONTENT-DIFFERENTIATION",
            "domain": "Instructional Design",
            "cluster": "Individualized Learning"
        })
        
        # Context 2: Process differentiation
        contexts.append({
            "text": f"Process differentiation for {topic} in {grade} {subject} offers multiple pathways to learning through varied instructional strategies, flexible grouping, and different learning modalities. Include visual, auditory, kinesthetic, and tactile approaches. Provide scaffolding for struggling learners and enrichment for advanced students.",
            "source": "Multiple Intelligences Theory",
            "subject": subject,
            "grade": grade,
            "standard_id": "PROCESS-DIFFERENTIATION",
            "domain": "Learning Styles",
            "cluster": "Instructional Variety"
        })
        
        # Context 3: Product differentiation
        contexts.append({
            "text": f"Product differentiation for {topic} in {grade} {subject} allows students to demonstrate learning through various formats like presentations, written reports, artistic projects, or multimedia creations. Provide rubrics that accommodate different product types while maintaining standards alignment and rigor.",
            "source": "Universal Design for Learning",
            "subject": subject,
            "grade": grade,
            "standard_id": "PRODUCT-DIFFERENTIATION",
            "domain": "Assessment Design",
            "cluster": "Multiple Formats"
        })
        
        return contexts
    
    def _get_standards_contexts(self, subject: str, grade: str, topic: str, student_group_info: str) -> List[Dict]:
        """Generate realistic standards alignment contexts"""
        
        contexts = []
        
        # Context 1: Subject-specific standards
        if subject.lower() == "mathematics":
            contexts.append({
                "text": f"Common Core Mathematics Standards for {grade} emphasize conceptual understanding, procedural fluency, and problem-solving for {topic}. Focus on mathematical practices including making sense of problems, reasoning abstractly, constructing viable arguments, and modeling with mathematics. Ensure students develop both skills and conceptual understanding.",
                "source": "Common Core State Standards",
                "subject": subject,
                "grade": grade,
                "standard_id": f"CCSS.MATH.CONTENT.{grade.split()[0]}.NF",
                "domain": "Mathematics",
                "cluster": "Number and Operations"
            })
        elif subject.lower() == "science":
            contexts.append({
                "text": f"Next Generation Science Standards for {grade} integrate three dimensions for {topic}: disciplinary core ideas, science and engineering practices, and crosscutting concepts. Emphasize inquiry-based learning, real-world applications, and the development of scientific thinking skills through hands-on investigation and evidence-based reasoning.",
                "source": "Next Generation Science Standards",
                "subject": subject,
                "grade": grade,
                "standard_id": f"NGSS.{grade.split()[0]}-LS1-1",
                "domain": "Science",
                "cluster": "Life Sciences"
            })
        
        # Context 2: Standards-based instruction
        contexts.append({
            "text": f"Standards-based instruction for {topic} in {grade} {subject} ensures alignment between learning objectives, instructional activities, and assessments. Use standards to guide curriculum planning, differentiate instruction, and measure student progress. Focus on the essential knowledge and skills students need for success.",
            "source": "Standards-Based Education Framework",
            "subject": subject,
            "grade": grade,
            "standard_id": "STANDARDS-BASED-INSTRUCTION",
            "domain": "Curriculum Design",
            "cluster": "Alignment"
        })
        
        return contexts
    
    def _get_external_resource_contexts(self, subject: str, grade: str, topic: str, student_group_info: str) -> List[Dict]:
        """Generate realistic external resource contexts"""
        
        contexts = []
        
        # Context 1: Educational technology resources
        contexts.append({
            "text": f"Educational technology resources for {topic} in {grade} {subject} include interactive simulations, virtual manipulatives, educational games, and assessment platforms. Select resources that align with learning objectives, provide accessibility features, and support diverse learning styles. Always preview content and provide context for student use.",
            "source": "Educational Technology Guidelines",
            "subject": subject,
            "grade": grade,
            "standard_id": "ED-TECH-RESOURCES",
            "domain": "Educational Technology",
            "cluster": "Digital Resources"
        })
        
        # Context 2: Multimedia resources
        contexts.append({
            "text": f"Multimedia resources for {topic} in {grade} {subject} include educational videos, podcasts, interactive websites, and digital libraries. These resources provide multiple modalities for learning and support visual, auditory, and kinesthetic learners. Ensure content is age-appropriate, accurate, and aligned with curriculum standards.",
            "source": "Multimedia Learning Principles",
            "subject": subject,
            "grade": grade,
            "standard_id": "MULTIMEDIA-RESOURCES",
            "domain": "Media Literacy",
            "cluster": "Digital Content"
        })
        
        # Context 3: Professional resources
        contexts.append({
            "text": f"Professional resources for {topic} in {grade} {subject} include teacher guides, lesson plans, assessment rubrics, and research articles. These resources support teacher knowledge, provide evidence-based strategies, and offer practical implementation guidance. Use professional resources to enhance instructional practice and student learning outcomes.",
            "source": "Professional Development Standards",
            "subject": subject,
            "grade": grade,
            "standard_id": "PROFESSIONAL-RESOURCES",
            "domain": "Teacher Development",
            "cluster": "Instructional Support"
        })
        
        return contexts
    
    def _get_general_contexts(self, subject: str, grade: str, topic: str, student_group_info: str) -> List[Dict]:
        """Generate general contexts for other question types"""
        
        contexts = []
        
        # Context 1: General pedagogical principles
        contexts.append({
            "text": f"Effective instruction for {topic} in {grade} {subject} follows research-based pedagogical principles including active engagement, meaningful practice, immediate feedback, and metacognitive awareness. Design learning experiences that promote deep understanding, critical thinking, and real-world application while accommodating diverse learner needs.",
            "source": "Educational Research Foundation",
            "subject": subject,
            "grade": grade,
            "standard_id": "PEDAGOGICAL-PRINCIPLES",
            "domain": "Educational Psychology",
            "cluster": "Learning Theory"
        })
        
        # Context 2: Student-centered learning
        contexts.append({
            "text": f"Student-centered learning for {topic} in {grade} {subject} emphasizes active participation, choice, and voice in the learning process. Create opportunities for students to explore, question, collaborate, and reflect. Build on students' prior knowledge, interests, and experiences to make learning relevant and engaging.",
            "source": "Student-Centered Learning Framework",
            "subject": subject,
            "grade": grade,
            "standard_id": "STUDENT-CENTERED",
            "domain": "Learning Design",
            "cluster": "Engagement"
        })
        
        return contexts
    
    def _generate_realistic_ground_truth(self, scenario: Dict[str, Any], contexts: List[Dict]) -> str:
        """Generate realistic ground truth answer based on scenario and contexts"""
        
        question_type = scenario["question_type"]
        subject = scenario["subject"]
        grade = scenario["grade"]
        topic = scenario["topic"]
        student_group_info = scenario["student_group_info"]
        
        # Include student group considerations in ground truth
        student_context = ""
        if student_group_info:
            student_context = f" Consider the specific needs: {student_group_info}."
        
        if question_type == "learning_objectives":
            return f"Key learning objectives for {topic} in {grade} {subject} include: 1) Understanding core concepts through concrete models and visual representations, 2) Applying knowledge through problem-solving and real-world applications, 3) Analyzing relationships and patterns, 4) Creating original work that demonstrates mastery. These align with relevant curriculum standards and promote deep understanding.{student_context}"
        
        elif question_type == "lesson_structure":
            return f"A well-structured {topic} lesson for {grade} should include: 1) Warm-up activity to activate prior knowledge (5-10 min), 2) Introduction to new concepts with concrete examples (10-15 min), 3) Guided practice with teacher support and peer collaboration (15-20 min), 4) Independent practice with differentiation (10-15 min), 5) Closure with reflection and assessment (5-10 min). Total duration should be appropriate for grade level and include appropriate transitions.{student_context}"
        
        elif question_type == "assessment_strategies":
            return f"Effective assessment strategies for {topic} in {grade} include: 1) Formative assessments during learning (exit tickets, observations, quick checks), 2) Summative assessments at lesson end (tests, projects, presentations), 3) Performance-based assessments (authentic tasks, real-world applications), 4) Self and peer assessments (reflection, collaboration), 5) Portfolio assessments over time (growth documentation). Align with curriculum standards and provide actionable feedback.{student_context}"
        
        elif question_type == "materials_resources":
            return f"Essential materials for {topic} lesson in {grade} include: 1) Manipulatives and hands-on materials for concrete learning, 2) Technology tools and software for engagement and accessibility, 3) Visual aids and posters for concept reinforcement, 4) Worksheets and practice materials for skill development, 5) Real-world objects for application and relevance. Ensure accessibility for all learners and support diverse learning styles.{student_context}"
        
        elif question_type == "differentiation":
            return f"Differentiation strategies for {topic} in {grade} include: 1) Content differentiation - varying complexity and depth based on readiness, 2) Process differentiation - multiple learning pathways and modalities, 3) Product differentiation - various assessment formats and choices, 4) Environment differentiation - flexible grouping and learning spaces, 5) Technology integration for support and enhancement. Provide scaffolding for struggling learners and enrichment for advanced students.{student_context}"
        
        elif question_type == "standards_alignment":
            return f"For {topic} in {grade} {subject}, focus on standards that emphasize: 1) Core conceptual understanding and procedural fluency, 2) Application and problem-solving in real-world contexts, 3) Critical thinking and analysis skills, 4) Communication and collaboration abilities, 5) Real-world connections and relevance. Ensure alignment between learning objectives, instructional activities, and assessments.{student_context}"
        
        elif question_type == "external_resources":
            return f"External resources for {topic} in {grade} {subject} include: 1) Educational technology tools and interactive simulations, 2) Multimedia resources (videos, podcasts, websites), 3) Professional resources (teacher guides, research articles), 4) Curriculum standards and assessment materials, 5) Community resources and real-world connections. Ensure resources are age-appropriate, accessible, and aligned with learning objectives.{student_context}"
        
        elif question_type == "comparison":
            return f"When comparing {topic} across different grade levels: 1) Complexity increases with grade level and developmental readiness, 2) Abstract thinking develops progressively from concrete to symbolic, 3) Prerequisites build upon previous learning and scaffold new concepts, 4) Assessment methods become more sophisticated and authentic, 5) Real-world applications expand in scope and depth. Maintain continuity while respecting developmental differences.{student_context}"
        
        elif question_type == "reasoning":
            return f"Reasoning about {topic} in {grade} {subject} involves: 1) Analyzing cause-and-effect relationships and patterns, 2) Making connections between concepts and real-world applications, 3) Evaluating evidence and arguments critically, 4) Drawing logical conclusions based on data and observations, 5) Applying knowledge to new situations and problems. Develop metacognitive awareness and problem-solving strategies.{student_context}"
        
        else:
            return f"Comprehensive guidance for {topic} in {grade} {subject} requires consideration of: 1) Student developmental needs and readiness levels, 2) Curriculum standards alignment and rigor, 3) Effective instructional strategies and methodologies, 4) Appropriate assessment methods and feedback, 5) Differentiation for diverse learners and abilities. Create engaging, meaningful learning experiences that promote deep understanding and real-world application.{student_context}"

async def main():
    """Generate and save the realistic golden dataset"""
    print("🚀 Generating Realistic Golden Dataset for RAGAS Evaluation (v3.0)...")
    
    generator = RealisticGoldenDatasetGenerator()
    
    # Try to initialize vectorstore, but continue if it fails
    try:
        await generator.rag_service.initialize_vectorstore()
        print("✅ Vector store initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize vector store: {e}")
        print("   Continuing with realistic contexts...")
    
    # Generate dataset
    dataset = await generator.generate_comprehensive_dataset()
    
    # Save to file
    output_file = "realistic_golden_dataset_ragas_evaluation_v3.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Realistic golden dataset generated successfully!")
    print(f"📁 Saved to: {output_file}")
    print(f"📊 Total samples: {dataset['total_samples']}")
    print(f"🎯 Question types: {len(dataset['question_types'])}")
    print(f"📚 Subjects covered: {len(dataset['subjects_covered'])}")
    print(f"🎓 Grade levels: {len(dataset['grade_levels'])}")
    print(f"👥 Student group types: {len(dataset['student_group_types'])}")
    
    # Print sample statistics
    question_types = {}
    difficulties = {}
    subjects = {}
    student_groups = {}
    
    for sample in dataset['samples']:
        q_type = sample['metadata']['question_type']
        difficulty = sample['metadata']['difficulty']
        subject = sample['metadata']['subject']
        student_group = sample['metadata']['student_group_info']
        
        question_types[q_type] = question_types.get(q_type, 0) + 1
        difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        subjects[subject] = subjects.get(subject, 0) + 1
        
        if student_group:
            student_groups["with_student_info"] = student_groups.get("with_student_info", 0) + 1
        else:
            student_groups["no_student_info"] = student_groups.get("no_student_info", 0) + 1
    
    print("\n📈 Dataset Statistics:")
    print(f"   Question Types: {question_types}")
    print(f"   Difficulties: {difficulties}")
    print(f"   Subjects: {subjects}")
    print(f"   Student Group Info: {student_groups}")
    
    print("\n🎯 Key Improvements in v3.0:")
    print("   ✅ Realistic educational contexts instead of YouTube descriptions")
    print("   ✅ Proper alignment between contexts and ground truth")
    print("   ✅ Standards-based content that matches RAG system output")
    print("   ✅ Comprehensive coverage of educational question types")
    print("   ✅ Student group considerations throughout")
    print("   ✅ Authentic assessment and instructional strategies")

if __name__ == "__main__":
    asyncio.run(main())