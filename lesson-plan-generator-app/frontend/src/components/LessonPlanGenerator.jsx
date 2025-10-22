import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const LessonPlanGenerator = ({ onLessonPlanGenerated }) => {
  const [formData, setFormData] = useState({
    subject: '',
    grade_level: '',
    topic: '',
    duration_minutes: 45,
    teaching_style: 'mixed',
    student_group_info: ''
  });
  const [isGenerating, setIsGenerating] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsGenerating(true);

    try {
      const response = await axios.post('http://localhost:8001/api/generate-lesson-plan', formData);
      console.log('Generated lesson plan:', response.data);
      onLessonPlanGenerated(response.data);
      toast.success('🎉 Lesson plan generated successfully!');
    } catch (error) {
      console.error('Error generating lesson plan:', error);
      toast.error('❌ Failed to generate lesson plan. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const subjects = [
    { value: 'Mathematics', emoji: '🔢', color: '#2563eb', bgColor: '#dbeafe' },
    { value: 'English Language Arts', emoji: '📚', color: '#059669', bgColor: '#d1fae5' },
    { value: 'Science', emoji: '🔬', color: '#ea580c', bgColor: '#fed7aa' },
    { value: 'Social Studies', emoji: '🌍', color: '#7c3aed', bgColor: '#e9d5ff' },
    { value: 'Arts', emoji: '🎨', color: '#dc2626', bgColor: '#fecaca' },
    { value: 'Physical Education', emoji: '🏃', color: '#0891b2', bgColor: '#cffafe' }
  ];

  const grades = [
    '3rd Grade', '4th Grade', '5th Grade', '6th Grade', 
    '7th Grade', '8th Grade', '9th Grade', '10th Grade', 
    '11th Grade', '12th Grade'
  ];

  const teachingStyles = [
    { value: 'mixed', label: 'Mixed Approach', emoji: '🎯' },
    { value: 'hands-on', label: 'Hands-on Learning', emoji: '✋' },
    { value: 'interactive', label: 'Interactive', emoji: '🤝' },
    { value: 'traditional', label: 'Traditional', emoji: '📖' },
    { value: 'project-based', label: 'Project-based', emoji: '📋' }
  ];

  return (
    <div 
      style={{
        background: 'white',
        borderRadius: '16px',
        border: '1px solid #cbd5e1',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        padding: '2rem',
        height: 'fit-content'
      }}
    >
      {/* Header Section */}
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <div 
          style={{
            width: '4rem',
            height: '4rem',
            background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.5rem auto'
          }}
        >
          <span style={{ color: 'white', fontSize: '2rem' }}>✨</span>
        </div>
        
        <h1 style={{ fontSize: '1.75rem', fontWeight: 'bold', color: '#1e293b', marginBottom: '0.75rem' }}>
          Create Your <span style={{ color: '#2563eb' }}>Lesson Plan</span>
        </h1>
        
        <p style={{ fontSize: '1rem', color: '#475569', lineHeight: '1.5' }}>
          Tell us about your lesson and we'll create a comprehensive plan tailored to your needs!
        </p>
      </div>
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Subject Selection */}
        <div>
          <label style={{ display: 'block', fontSize: '0.95rem', fontWeight: '600', color: '#374151', marginBottom: '0.75rem' }}>
            📚 What subject are you teaching?
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
            {subjects.map((subject) => (
              <button
                key={subject.value}
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, subject: subject.value }))}
                style={{
                  padding: '1rem',
                  borderRadius: '10px',
                  border: formData.subject === subject.value ? `2px solid ${subject.color}` : '2px solid #e2e8f0',
                  background: formData.subject === subject.value ? subject.bgColor : 'white',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  textAlign: 'left',
                  boxShadow: formData.subject === subject.value ? '0 2px 4px rgba(0, 0, 0, 0.1)' : 'none'
                }}
                onMouseEnter={(e) => {
                  if (formData.subject !== subject.value) {
                    e.target.style.borderColor = '#cbd5e1';
                    e.target.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (formData.subject !== subject.value) {
                    e.target.style.borderColor = '#e2e8f0';
                    e.target.style.boxShadow = 'none';
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '1.25rem' }}>{subject.emoji}</span>
                  <span style={{ fontWeight: '500', color: '#1e293b', fontSize: '0.9rem' }}>{subject.value}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Grade Level */}
        <div>
          <label style={{ display: 'block', fontSize: '0.95rem', fontWeight: '600', color: '#374151', marginBottom: '0.75rem' }}>
            🎓 What grade level?
          </label>
          <select
            name="grade_level"
            value={formData.grade_level}
            onChange={handleInputChange}
            required
            style={{
              width: '100%',
              padding: '0.875rem',
              borderRadius: '8px',
              border: '2px solid #e2e8f0',
              fontSize: '0.95rem',
              background: 'white',
              transition: 'all 0.2s ease',
              boxSizing: 'border-box'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#2563eb';
              e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#e2e8f0';
              e.target.style.boxShadow = 'none';
            }}
          >
            <option value="">Select grade level</option>
            {grades.map(grade => (
              <option key={grade} value={grade}>{grade}</option>
            ))}
          </select>
        </div>

        {/* Topic */}
        <div>
          <label style={{ display: 'block', fontSize: '0.95rem', fontWeight: '600', color: '#374151', marginBottom: '0.75rem' }}>
            💡 What's the main topic?
          </label>
          <input
            type="text"
            name="topic"
            value={formData.topic}
            onChange={handleInputChange}
            required
            placeholder="e.g., Fractions, Photosynthesis, World War II..."
            style={{
              width: '100%',
              padding: '0.875rem',
              borderRadius: '8px',
              border: '2px solid #e2e8f0',
              fontSize: '0.95rem',
              background: 'white',
              transition: 'all 0.2s ease',
              boxSizing: 'border-box'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#2563eb';
              e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#e2e8f0';
              e.target.style.boxShadow = 'none';
            }}
          />
        </div>

        {/* Duration and Teaching Style */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.95rem', fontWeight: '600', color: '#374151', marginBottom: '0.75rem' }}>
              ⏰ Duration (min)
            </label>
            <input
              type="number"
              name="duration_minutes"
              value={formData.duration_minutes}
              onChange={handleInputChange}
              min="15"
              max="120"
              style={{
                width: '100%',
                padding: '0.875rem',
                borderRadius: '8px',
                border: '2px solid #e2e8f0',
                fontSize: '0.95rem',
                background: 'white',
                transition: 'all 0.2s ease',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#2563eb';
                e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#e2e8f0';
                e.target.style.boxShadow = 'none';
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.95rem', fontWeight: '600', color: '#374151', marginBottom: '0.75rem' }}>
              🎯 Teaching Style
            </label>
            <select
              name="teaching_style"
              value={formData.teaching_style}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '0.875rem',
                borderRadius: '8px',
                border: '2px solid #e2e8f0',
                fontSize: '0.95rem',
                background: 'white',
                transition: 'all 0.2s ease',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#2563eb';
                e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#e2e8f0';
                e.target.style.boxShadow = 'none';
              }}
            >
              {teachingStyles.map(style => (
                <option key={style.value} value={style.value}>
                  {style.emoji} {style.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Student Group Information */}
        <div>
          <label style={{ display: 'block', fontSize: '0.95rem', fontWeight: '600', color: '#374151', marginBottom: '0.75rem' }}>
            👥 Tell us about your students (optional)
          </label>
          <div style={{ marginBottom: '0.5rem' }}>
            <p style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '0.75rem' }}>
              Help us personalize your lesson plan by sharing information about your student group:
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <div style={{ fontSize: '0.8rem', color: '#6b7280', padding: '0.5rem', background: '#f8fafc', borderRadius: '6px' }}>
                💡 Examples: "5 ESL students", "2 students with ADHD", "Mixed ability levels", "Gifted and talented class"
              </div>
            </div>
          </div>
          <textarea
            name="student_group_info"
            value={formData.student_group_info}
            onChange={handleInputChange}
            placeholder="e.g., 8 students total, 3 ESL learners, 2 students with learning disabilities, mixed ability levels..."
            style={{
              width: '100%',
              minHeight: '80px',
              padding: '0.75rem',
              borderRadius: '8px',
              border: '2px solid #e2e8f0',
              fontSize: '0.9rem',
              color: '#374151',
              background: 'white',
              resize: 'vertical',
              fontFamily: 'inherit',
              transition: 'border-color 0.2s ease',
              outline: 'none',
              boxSizing: 'border-box'
            }}
            onFocus={(e) => e.target.style.borderColor = '#2563eb'}
            onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
          />
          <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.5rem' }}>
            This information helps us create more inclusive and personalized lesson plans with appropriate accommodations and modifications.
          </p>
        </div>

        {/* Generate Button */}
        <div style={{ marginTop: '0.5rem' }}>
          <button
            type="submit"
            disabled={isGenerating}
            style={{
              width: '100%',
              padding: '1rem 1.5rem',
              background: isGenerating 
                ? 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)' 
                : 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: isGenerating ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.2)',
              opacity: isGenerating ? 0.7 : 1
            }}
            onMouseEnter={(e) => {
              if (!isGenerating) {
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 6px 12px -2px rgba(37, 99, 235, 0.3)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isGenerating) {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 4px 6px -1px rgba(37, 99, 235, 0.2)';
              }
            }}
          >
            {isGenerating ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                <div 
                  style={{
                    width: '1rem',
                    height: '1rem',
                    border: '2px solid white',
                    borderTop: '2px solid transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }}
                />
                <span>Generating...</span>
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                <span>🚀</span>
                <span>Generate Lesson Plan</span>
              </div>
            )}
          </button>
        </div>
      </form>

      {/* Add CSS for spinner animation */}
      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LessonPlanGenerator;