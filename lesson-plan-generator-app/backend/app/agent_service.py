# Import necessary libraries
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate  # Updated import
from typing import TypedDict, List, Dict, Any
import json
import asyncio
import re

class LessonPlanState(TypedDict):
    user_input: str
    subject: str
    grade_level: str
    topic: str
    duration_minutes: int
    teaching_style: str
    student_group_info: str
    retrieved_standards: List[Dict]
    external_resources: List[Dict]
    lesson_objectives: List[str]
    activities: List[Dict]
    assessments: List[Dict]
    materials: List[str]
    final_lesson_plan: Dict

class EducationPlanningAgent:
    def __init__(self, rag_service):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        self.rag_service = rag_service
        self.graph = self._create_graph()
    
    def _create_graph(self):
        """Create the LangGraph workflow"""
        workflow = StateGraph(LessonPlanState)
        
        # Add nodes
        workflow.add_node("retrieve_standards", self.retrieve_standards)
        workflow.add_node("fetch_external_resources", self.fetch_external_resources)
        workflow.add_node("generate_objectives", self.generate_objectives)
        workflow.add_node("plan_activities", self.plan_activities)
        workflow.add_node("design_assessments", self.design_assessments)
        workflow.add_node("compile_lesson_plan", self.compile_lesson_plan)
        
        # Add edges
        workflow.set_entry_point("retrieve_standards")
        workflow.add_edge("retrieve_standards", "fetch_external_resources")
        workflow.add_edge("fetch_external_resources", "generate_objectives")
        workflow.add_edge("generate_objectives", "plan_activities")
        workflow.add_edge("plan_activities", "design_assessments")
        workflow.add_edge("design_assessments", "compile_lesson_plan")
        workflow.add_edge("compile_lesson_plan", END)
        
        return workflow.compile()
    
    async def retrieve_standards(self, state: LessonPlanState) -> LessonPlanState:
        """Retrieve relevant curriculum standards"""
        query = f"{state['topic']} {state['subject']} {state['grade_level']}"
        standards = await self.rag_service.retrieve_relevant_standards(
            query, state['subject'], state['grade_level']
        )
        
        state["retrieved_standards"] = standards
        return state
    
    async def fetch_external_resources(self, state: LessonPlanState) -> LessonPlanState:
        """Fetch additional resources from external APIs including dynamic standards"""
        external_resources = []
        try:
            # This will now include dynamic CCSS/NGSS standards
            external_resources = await self.rag_service.external_api_service.fetch_all_external_resources(
                state['subject'], state['grade_level'], state['topic']
            )
        except Exception as e:
            print(f"Error fetching external resources: {e}")
        state["external_resources"] = external_resources
        return state
    
    async def generate_objectives(self, state: LessonPlanState) -> LessonPlanState:
        """Generate learning objectives with external resource context"""
        
        # Create student group context
        student_context = ""
        if state["student_group_info"]:
            student_context = f"""
        
STUDENT GROUP INFORMATION:
{state["student_group_info"]}

IMPORTANT: When creating objectives, consider the specific needs mentioned above. Ensure objectives are:
- Accessible to all learners mentioned
- Include appropriate accommodations for ESL students, students with disabilities, etc.
- Use clear, simple language when ESL students are present
- Consider different ability levels and learning styles
"""
        
        prompt = ChatPromptTemplate.from_template("""
        Based on the following information, generate 3-5 DISTINCT, specific, measurable learning objectives:

        Subject: {subject}
        Grade Level: {grade_level}
        Topic: {topic}
        Duration: {duration_minutes} minutes
        Teaching Style: {teaching_style}

        Relevant Standards: {standards}

        External Resources Available: {external_resources}

        {student_context}

        IMPORTANT: Each objective must be UNIQUE and address different aspects of learning. Do not repeat the same objective.

        Requirements:
        1. Use varied action verbs (describe, analyze, create, apply, evaluate, compare, contrast, etc.)
        2. Focus on different cognitive levels (knowledge, comprehension, application, analysis, synthesis, evaluation)
        3. Make objectives SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
        4. Ensure each objective complements others without overlap
        5. Format as complete sentences starting with "Students will..."
        6. Consider the specific student group needs mentioned above

        Example format:
        1. Students will describe [specific aspect]...
        2. Students will analyze [different aspect]...
        3. Students will create [another aspect]...
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({
            "subject": state["subject"],
            "grade_level": state["grade_level"],
            "topic": state["topic"],
            "duration_minutes": state["duration_minutes"],
            "teaching_style": state["teaching_style"],
            "standards": json.dumps(state["retrieved_standards"]),
            "external_resources": json.dumps(state["external_resources"]),
            "student_context": student_context
        })
        
        # Parse objectives from response
        objectives = self._parse_objectives(response.content)
        state["lesson_objectives"] = objectives
        return state
    
    async def plan_activities(self, state: LessonPlanState) -> LessonPlanState:
        """Plan engaging activities with external resource integration"""
        
        # Create student group context for activities
        student_context = ""
        if state["student_group_info"]:
            student_context = f"""
        
STUDENT GROUP INFORMATION:
{state["student_group_info"]}

IMPORTANT: When creating activities, consider the specific needs mentioned above. Ensure activities:
- Include appropriate accommodations and modifications
- Provide multiple ways for students to engage (visual, auditory, kinesthetic)
- Consider ESL students' language needs (visual supports, simplified language)
- Accommodate students with disabilities (extended time, alternative formats, etc.)
- Provide differentiation for different ability levels
- Include collaborative opportunities when appropriate
"""
        
        prompt = ChatPromptTemplate.from_template("""
        Create a comprehensive activity plan for a {duration_minutes}-minute lesson on {topic} for {grade_level} grade {subject}.

        Teaching Style: {teaching_style}
        Learning Objectives: {objectives}
        Available External Resources: {external_resources}

        {student_context}

        STRUCTURE REQUIREMENTS:
        Create exactly 4 activities in this order:
        1. WARM-UP ACTIVITY (5-10 minutes)
        2. MAIN INSTRUCTIONAL ACTIVITY (20-30 minutes) 
        3. PRACTICE/APPLICATION ACTIVITY (10-15 minutes)
        4. CLOSURE ACTIVITY (5 minutes)

        FOR EACH ACTIVITY, provide:
        - Clear, descriptive title
        - Specific duration (e.g., "8 minutes")
        - Detailed step-by-step instructions
        - Required materials and resources
        - Student engagement strategies
        - Integration of external resources (when applicable)
        - Assessment checkpoints
        - Accommodations for the specific student group needs mentioned above

        FORMATTING REQUIREMENTS:
        Format each activity as follows:
        
        ACTIVITY 1: [Title]
        Duration: [X minutes]
        Materials: [List specific materials]
        Instructions:
        1. [Step 1]
        2. [Step 2]
        3. [Step 3]
        Engagement Strategy: [How to keep students engaged]
        External Resource Integration: [If applicable, reference specific resources]
        Assessment Checkpoint: [How to check understanding]
        Accommodations: [Specific accommodations for student group needs]

        Ensure activities are:
        - Age-appropriate for {grade_level}
        - Aligned with learning objectives
        - Engaging and interactive
        - Properly sequenced for learning progression
        - Inclusive and accessible
        - Accommodate the specific student group needs mentioned above
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({
            "duration_minutes": state["duration_minutes"],
            "topic": state["topic"],
            "grade_level": state["grade_level"],
            "subject": state["subject"],
            "teaching_style": state["teaching_style"],
            "objectives": json.dumps(state["lesson_objectives"]),
            "external_resources": json.dumps(state["external_resources"]),
            "student_context": student_context
        })
        
        activities = self._parse_activities(response.content)
        state["activities"] = activities
        return state
    
    async def design_assessments(self, state: LessonPlanState) -> LessonPlanState:
        """Design formative and summative assessments"""
        
        # Create student group context for assessments
        student_context = ""
        if state["student_group_info"]:
            student_context = f"""
        
STUDENT GROUP INFORMATION:
{state["student_group_info"]}

IMPORTANT: When creating assessments, consider the specific needs mentioned above. Ensure assessments:
- Provide multiple ways for students to demonstrate learning
- Include appropriate accommodations (extended time, alternative formats, etc.)
- Consider ESL students' language needs (visual supports, simplified language)
- Accommodate students with disabilities (assistive technology, modified expectations)
- Provide differentiation for different ability levels
- Include both formal and informal assessment methods
"""
        
        prompt = ChatPromptTemplate.from_template("""
        Design comprehensive assessment strategies for this lesson:

        Topic: {topic}
        Grade Level: {grade_level}
        Subject: {subject}
        Learning Objectives: {objectives}
        External Resources Used: {external_resources}

        {student_context}

        ASSESSMENT REQUIREMENTS:
        Create exactly 3 assessment types:

        1. FORMATIVE ASSESSMENT (During Lesson)
           - Real-time monitoring of student understanding
           - Quick checks for comprehension
           - Immediate feedback opportunities

        2. SUMMATIVE ASSESSMENT (End of Lesson)
           - Final evaluation of learning objectives
           - Comprehensive understanding check
           - Performance-based or knowledge-based

        3. PERFORMANCE-BASED ASSESSMENT
           - Hands-on demonstrations
           - Project-based evaluations
           - Real-world application tasks

        FOR EACH ASSESSMENT, provide:
        - Assessment type and purpose
        - Specific timing (when during lesson)
        - Detailed instructions for implementation
        - Evaluation criteria and rubrics
        - Materials needed
        - Integration of external resources
        - Accommodations for the specific student group needs mentioned above

        FORMATTING REQUIREMENTS:
        Format each assessment as follows:

        ASSESSMENT 1: [Type] - [Purpose]
        Timing: [When during lesson]
        Instructions: [Step-by-step implementation]
        Evaluation Criteria: [How to assess]
        Materials: [What's needed]
        External Resource Integration: [If applicable]
        Accommodations: [Specific accommodations for student group needs]

        Ensure assessments are:
        - Aligned with learning objectives
        - Age-appropriate for {grade_level}
        - Fair and unbiased
        - Clear and measurable
        - Engaging for students
        - Accommodate the specific student group needs mentioned above
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({
            "topic": state["topic"],
            "grade_level": state["grade_level"],
            "subject": state["subject"],
            "objectives": json.dumps(state["lesson_objectives"]),
            "external_resources": json.dumps(state["external_resources"]),
            "student_context": student_context
        })
        
        assessments = self._parse_assessments(response.content)
        state["assessments"] = assessments
        return state
    
    
    async def compile_lesson_plan(self, state: LessonPlanState) -> LessonPlanState:
        """Compile final lesson plan with external resources"""
        lesson_plan = {
            "title": f"{state['topic']} - {state['grade_level']} Grade {state['subject']}",
            "subject": state["subject"],
            "grade_level": state["grade_level"],
            "duration_minutes": state["duration_minutes"],
            "topic": state["topic"],
            "teaching_style": state["teaching_style"],
            "objectives": state["lesson_objectives"],
            "activities": state["activities"],
            "assessments": state["assessments"],
            "materials": self._extract_materials(state["activities"]),
            "standards_aligned": state["retrieved_standards"],
            "external_resources": state["external_resources"],
            "generated_at": state.get("generated_at", ""),
            "api_sources": self._extract_api_sources(state["external_resources"])
        }
        
        state["final_lesson_plan"] = lesson_plan
        return state
    
    async def generate_lesson_plan(self, user_input: Dict) -> Dict:
        """Main method to generate lesson plan with external API integration"""
        initial_state = LessonPlanState(
            user_input=user_input.get("topic", ""),
            subject=user_input.get("subject", ""),
            grade_level=user_input.get("grade_level", ""),
            topic=user_input.get("topic", ""),
            duration_minutes=user_input.get("duration_minutes", 45),
            teaching_style=user_input.get("teaching_style", "mixed"),
            student_group_info=user_input.get("student_group_info", ""),
            retrieved_standards=[],
            external_resources=[],
            lesson_objectives=[],
            activities=[],
            assessments=[],
            materials=[],
            final_lesson_plan={},
            generated_at=user_input.get("generated_at", "")
        )
        
        result = await self.graph.ainvoke(initial_state)
        return result["final_lesson_plan"]
    
    def _extract_api_sources(self, external_resources: List[Dict]) -> List[str]:
        """Extract unique API sources used"""
        sources = set()
        for resource in external_resources:
            sources.add(resource.get("source", "Unknown"))
        return list(sources)
    
    def _parse_objectives(self, content: str) -> List[str]:
        """Parse objectives from LLM response with deduplication"""
        objectives = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            cleaned_line = None
            
            # Handle numbered objectives (1., 2., 3., etc.)
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                cleaned_line = line[2:].strip()
            # Handle bullet points
            elif line.startswith(('-', '•')):
                cleaned_line = line[1:].strip()
            # Handle lines that contain objective keywords
            elif 'objective' in line.lower() or 'students will' in line.lower():
                cleaned_line = line.strip()
            
            # Only add if we have a valid cleaned line and it's substantial
            if cleaned_line and len(cleaned_line) > 15:
                # Check for duplicates before adding
                if cleaned_line not in objectives:
                    objectives.append(cleaned_line)
        
        # If no objectives found with patterns, try to extract from paragraphs
        if not objectives:
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if 'students will' in para.lower() or 'objective' in para.lower():
                    para = para.strip()
                    if para not in objectives and len(para) > 15:
                        objectives.append(para)
        
        # Additional deduplication using similarity check
        objectives = self._deduplicate_objectives(objectives)
        
        return objectives[:5]  # Limit to 5 objectives

    def _deduplicate_objectives(self, objectives: List[str]) -> List[str]:
        """Remove duplicate or highly similar objectives"""
        if len(objectives) <= 1:
            return objectives
        
        unique_objectives = []
        
        for obj in objectives:
            is_duplicate = False
            
            # Check against existing unique objectives
            for unique_obj in unique_objectives:
                # Calculate similarity (simple word overlap check)
                similarity = self._calculate_similarity(obj.lower(), unique_obj.lower())
                
                # If similarity is too high, consider it a duplicate
                if similarity > 0.8:  # 80% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_objectives.append(obj)
        
        return unique_objectives

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple word-based similarity between two texts"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    def _parse_activities(self, content: str) -> List[Dict]:
        """Parse activities from LLM response with improved formatting"""
        activities = []
        
        # Split content into activity sections
        activity_sections = re.split(r'ACTIVITY \d+:', content, flags=re.IGNORECASE)
        
        for i, section in enumerate(activity_sections[1:], 1):  # Skip first empty section
            activity = self._parse_single_activity(section, i)
            if activity:
                activities.append(activity)
        
        # Fallback to old parsing if new method fails
        if not activities:
            activities = self._parse_activities_fallback(content)
        
        return activities

    def _parse_single_activity(self, section: str, activity_num: int) -> Dict:
        """Parse a single activity section"""
        lines = section.strip().split('\n')
        activity = {
            "title": f"Activity {activity_num}",
            "description": "",
            "duration": "10-15 minutes",
            "materials": [],
            "instructions": [],
            "engagement_strategy": "",
            "external_resource_integration": "",
            "assessment_checkpoint": "",
            "type": self._classify_activity_type(section.lower())
        }
        
        current_field = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify field headers
            if line.lower().startswith('duration:'):
                activity["duration"] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('materials:'):
                current_field = 'materials'
                materials_text = line.split(':', 1)[1].strip()
                if materials_text:
                    activity["materials"] = [m.strip() for m in materials_text.split(',')]
            elif line.lower().startswith('instructions:'):
                current_field = 'instructions'
            elif line.lower().startswith('engagement strategy:'):
                current_field = 'engagement_strategy'
                activity["engagement_strategy"] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('external resource integration:'):
                current_field = 'external_resource_integration'
                activity["external_resource_integration"] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('assessment checkpoint:'):
                current_field = 'assessment_checkpoint'
                activity["assessment_checkpoint"] = line.split(':', 1)[1].strip()
            elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                # Instruction steps
                if current_field == 'instructions':
                    activity["instructions"].append(line[2:].strip())
            elif current_field == 'instructions' and line:
                activity["instructions"].append(line)
            elif not activity["title"] or activity["title"] == f"Activity {activity_num}":
                # First non-header line is likely the title
                activity["title"] = line
        
        # Combine instructions into description
        if activity["instructions"]:
            activity["description"] = ' '.join(activity["instructions"])
        
        return activity if activity["description"] or activity["title"] != f"Activity {activity_num}" else None

    def _parse_activities_fallback(self, content: str) -> List[Dict]:
        """Fallback parsing method for activities"""
        activities = []
        sections = content.split('\n\n')
        
        activity_types = ['warm-up', 'warm up', 'opening', 'introduction', 
                        'main activity', 'instruction', 'practice', 
                        'application', 'closure', 'wrap-up', 'wrap up']
        
        for section in sections:
            section_lower = section.lower()
            
            if any(activity_type in section_lower for activity_type in activity_types):
                lines = section.split('\n')
                title = ""
                description = ""
                duration = ""
                materials = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if not title and len(line) > 5:
                        title = line
                    elif 'minute' in line.lower() or 'duration' in line.lower():
                        duration = line
                    elif 'material' in line.lower() or 'supplies' in line.lower():
                        materials.append(line)
                    else:
                        if line and line not in [title, duration]:
                            description += line + " "
                
                if title or description:
                    activities.append({
                        "title": title or "Activity",
                        "description": description.strip(),
                        "duration": duration or "10-15 minutes",
                        "materials": materials,
                        "type": self._classify_activity_type(title.lower() + " " + description.lower())
                    })
        
        return activities

    def _classify_activity_type(self, text: str) -> str:
        """Classify activity type based on content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['warm-up', 'warm up', 'opening', 'introduction']):
            return "Warm-up"
        elif any(word in text_lower for word in ['main', 'instruction', 'teaching', 'lesson']):
            return "Main Activity"
        elif any(word in text_lower for word in ['practice', 'exercise', 'worksheet']):
            return "Practice"
        elif any(word in text_lower for word in ['closure', 'wrap-up', 'wrap up', 'conclusion']):
            return "Closure"
        else:
            return "Activity"

    def _parse_assessments(self, content: str) -> List[Dict]:
        """Parse assessments from LLM response with improved formatting"""
        assessments = []
        
        # Split content into assessment sections
        assessment_sections = re.split(r'ASSESSMENT \d+:', content, flags=re.IGNORECASE)
        
        for i, section in enumerate(assessment_sections[1:], 1):  # Skip first empty section
            assessment = self._parse_single_assessment(section, i)
            if assessment:
                assessments.append(assessment)
        
        # Fallback to old parsing if new method fails
        if not assessments:
            assessments = self._parse_assessments_fallback(content)
        
        return assessments

    def _parse_single_assessment(self, section: str, assessment_num: int) -> Dict:
        """Parse a single assessment section"""
        lines = section.strip().split('\n')
        assessment = {
            "type": "formative",
            "description": "",
            "timing": "during lesson",
            "method": "Multiple Methods",
            "instructions": "",
            "evaluation_criteria": "",
            "materials": [],
            "external_resource_integration": ""
        }
        
        current_field = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify field headers
            if line.lower().startswith('timing:'):
                assessment["timing"] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('instructions:'):
                current_field = 'instructions'
                assessment["instructions"] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('evaluation criteria:'):
                current_field = 'evaluation_criteria'
                assessment["evaluation_criteria"] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('materials:'):
                current_field = 'materials'
                materials_text = line.split(':', 1)[1].strip()
                if materials_text:
                    assessment["materials"] = [m.strip() for m in materials_text.split(',')]
            elif line.lower().startswith('external resource integration:'):
                current_field = 'external_resource_integration'
                assessment["external_resource_integration"] = line.split(':', 1)[1].strip()
            elif current_field == 'instructions' and line:
                assessment["instructions"] += " " + line
            elif current_field == 'evaluation_criteria' and line:
                assessment["evaluation_criteria"] += " " + line
            elif not assessment["description"]:
                # First non-header line is likely the description
                assessment["description"] = line
        
        # Determine assessment type from content
        section_lower = section.lower()
        if 'formative' in section_lower:
            assessment["type"] = "formative"
        elif 'summative' in section_lower:
            assessment["type"] = "summative"
        elif 'differentiated' in section_lower:
            assessment["type"] = "differentiated"
        
        # Extract assessment method
        assessment["method"] = self._extract_assessment_method(assessment["description"])
        
        return assessment if assessment["description"] else None

    def _parse_assessments_fallback(self, content: str) -> List[Dict]:
        """Fallback parsing method for assessments"""
        assessments = []
        sections = content.split('\n\n')
        
        assessment_types = ['formative', 'summative', 'assessment', 'evaluation', 
                        'quiz', 'test', 'check', 'monitor']
        
        for section in sections:
            section_lower = section.lower()
            
            if any(assessment_type in section_lower for assessment_type in assessment_types):
                lines = section.split('\n')
                assessment_type = "formative"  # default
                description = ""
                timing = ""
                
                # Determine assessment type
                if 'formative' in section_lower:
                    assessment_type = "formative"
                elif 'summative' in section_lower:
                    assessment_type = "summative"
                elif 'quiz' in section_lower or 'test' in section_lower:
                    assessment_type = "summative"
                
                # Extract timing information
                for line in lines:
                    if 'during' in line.lower() or 'throughout' in line.lower():
                        timing = "during lesson"
                    elif 'end' in line.lower() or 'after' in line.lower():
                        timing = "end of lesson"
                    elif 'beginning' in line.lower() or 'start' in line.lower():
                        timing = "beginning of lesson"
                
                # Combine all lines for description
                description = ' '.join([line.strip() for line in lines if line.strip()])
                
                if description:
                    assessments.append({
                        "type": assessment_type,
                        "description": description,
                        "timing": timing or "during lesson",
                        "method": self._extract_assessment_method(description)
                    })
        
        return assessments

    def _extract_assessment_method(self, description: str) -> str:
        """Extract assessment method from description"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['observation', 'observe', 'watch']):
            return "Observation"
        elif any(word in desc_lower for word in ['discussion', 'discuss', 'talk']):
            return "Discussion"
        elif any(word in desc_lower for word in ['question', 'ask', 'quiz']):
            return "Questioning"
        elif any(word in desc_lower for word in ['work', 'product', 'artifact']):
            return "Student Work"
        elif any(word in desc_lower for word in ['peer', 'partner', 'group']):
            return "Peer Assessment"
        else:
            return "Multiple Methods"


    def _extract_materials(self, activities: List[Dict]) -> List[str]:
        """Extract materials list from activities with improved categorization"""
        materials = set()
        
        for activity in activities:
            # Extract materials from activity description
            description = activity.get("description", "").lower()
            activity_materials = activity.get("materials", [])
            
            # Add explicit materials
            for material in activity_materials:
                materials.add(material)
            
            # Extract materials from description using common patterns
            material_keywords = ['paper', 'pencil', 'pen', 'marker', 'board', 'chart', 
                            'worksheet', 'handout', 'book', 'textbook', 'computer', 
                            'tablet', 'calculator', 'ruler', 'scissors', 'glue',
                            'manipulatives', 'blocks', 'cards', 'dice', 'notebook',
                            'whiteboard', 'projector', 'screen', 'speakers']
            
            for keyword in material_keywords:
                if keyword in description:
                    materials.add(keyword.title())
            
            # Look for specific material mentions
            if 'manipulatives' in description:
                materials.add("Math Manipulatives")
            if 'technology' in description or 'digital' in description:
                materials.add("Technology/Devices")
            if 'art supplies' in description:
                materials.add("Art Supplies")
            if 'science equipment' in description:
                materials.add("Science Equipment")
            if 'lab materials' in description:
                materials.add("Lab Materials")
            if 'construction materials' in description:
                materials.add("Construction Materials")
        
        return list(materials) if materials else ["Standard classroom materials"]