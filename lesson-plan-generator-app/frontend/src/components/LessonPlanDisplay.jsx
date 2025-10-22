import React from 'react';

const LessonPlanDisplay = ({ lessonPlan }) => {
  if (!lessonPlan) {
    return (
      <div 
        style={{
          background: 'white',
          borderRadius: '16px',
          border: '1px solid #cbd5e1',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          padding: '2rem',
          textAlign: 'center',
          height: 'fit-content'
        }}
      >
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
          <span style={{ color: 'white', fontSize: '2rem' }}>📝</span>
        </div>
        <h3 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1e293b', marginBottom: '1rem' }}>
          Ready to Create?
        </h3>
        <p style={{ fontSize: '1rem', color: '#475569' }}>
          Fill out the form to generate your lesson plan!
        </p>
      </div>
    );
  }

  // Helper function to safely render content
  const renderContent = (content) => {
    if (typeof content === 'string') {
      return content;
    } else if (typeof content === 'object' && content !== null) {
      if (content.description) {
        return content.description;
      } else if (content.title) {
        return content.title;
      } else {
        return JSON.stringify(content, null, 2);
      }
    } else if (Array.isArray(content)) {
      return content.map((item, index) => renderContent(item)).join(', ');
    }
    return String(content);
  };

  // Helper function to format differentiation strategies into readable bullets
  const formatDifferentiation = (content) => {
    const text = renderContent(content);
    // Split by common separators and create bullet points
    const strategies = text
      .split(/[•\-\*\n]/)
      .map(str => str.trim())
      .filter(str => str.length > 10)
      .slice(0, 5); // Limit to 5 strategies max
    
    return strategies;
  };

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
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
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
          <span style={{ color: 'white', fontSize: '2rem' }}>📚</span>
        </div>
        
        <h1 style={{ 
          fontSize: '1.75rem', 
          fontWeight: 'bold', 
          color: '#1e293b', 
          marginBottom: '1rem',
          lineHeight: '1.3'
        }}>
          {lessonPlan.title || `${lessonPlan.subject || 'Lesson'} - ${lessonPlan.topic || 'Plan'}`}
        </h1>
        
        <div style={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          justifyContent: 'center', 
          gap: '0.5rem',
          marginTop: '1rem'
        }}>
          {lessonPlan.subject && (
            <span 
              style={{
                background: '#dbeafe',
                color: '#2563eb',
                padding: '0.375rem 0.75rem',
                borderRadius: '16px',
                fontSize: '0.8rem',
                fontWeight: '500',
                whiteSpace: 'nowrap'
              }}
            >
              <strong>Subject:</strong> {lessonPlan.subject}
            </span>
          )}
          {lessonPlan.grade_level && (
            <span 
              style={{
                background: '#d1fae5',
                color: '#059669',
                padding: '0.375rem 0.75rem',
                borderRadius: '16px',
                fontSize: '0.8rem',
                fontWeight: '500',
                whiteSpace: 'nowrap'
              }}
            >
              <strong>Grade:</strong> {lessonPlan.grade_level}
            </span>
          )}
          {lessonPlan.duration_minutes && (
            <span 
              style={{
                background: '#f3f4f6',
                color: '#374151',
                padding: '0.375rem 0.75rem',
                borderRadius: '16px',
                fontSize: '0.8rem',
                fontWeight: '500',
                whiteSpace: 'nowrap'
              }}
            >
              <strong>Duration:</strong> {lessonPlan.duration_minutes} min
            </span>
          )}
        </div>
      </div>

      {/* Learning Objectives - Succinct with bullets (max 3) */}
      {lessonPlan.objectives && lessonPlan.objectives.length > 0 && (
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
            <div 
              style={{
                width: '2.25rem',
                height: '2.25rem',
                background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '0.75rem',
                flexShrink: 0
              }}
            >
              <span style={{ color: 'white', fontSize: '0.9rem' }}>🎯</span>
            </div>
            <h2 style={{ fontSize: '1.375rem', fontWeight: '600', color: '#1e293b', margin: 0 }}>
              Learning Objectives
            </h2>
          </div>
          <div 
            style={{
              background: '#f8fafc',
              borderRadius: '12px',
              border: '1px solid #e2e8f0',
              padding: '1.25rem'
            }}
          >
            <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
              {lessonPlan.objectives.slice(0, 3).map((objective, index) => (
                <li key={index} style={{ 
                  display: 'flex', 
                  alignItems: 'flex-start', 
                  marginBottom: index < 2 ? '0.75rem' : '0'
                }}>
                  <span 
                    style={{
                      width: '1.5rem',
                      height: '1.5rem',
                      background: '#2563eb',
                      color: 'white',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      marginRight: '0.75rem',
                      marginTop: '0.125rem',
                      flexShrink: 0
                    }}
                  >
                    {index + 1}
                  </span>
                  <span style={{ 
                    color: '#374151', 
                    fontSize: '0.95rem', 
                    lineHeight: '1.5',
                    fontWeight: '500'
                  }}>
                    {renderContent(objective)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Activities - Bullet format */}
      {lessonPlan.activities && lessonPlan.activities.length > 0 && (
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
            <div 
              style={{
                width: '2.25rem',
                height: '2.25rem',
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '0.75rem',
                flexShrink: 0
              }}
            >
              <span style={{ color: 'white', fontSize: '0.9rem' }}>⚡</span>
            </div>
            <h2 style={{ fontSize: '1.375rem', fontWeight: '600', color: '#1e293b', margin: 0 }}>
              Activities
            </h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {lessonPlan.activities.map((activity, index) => (
              <div 
                key={index} 
                style={{
                  background: 'white',
                  border: '1px solid #d1fae5',
                  borderRadius: '10px',
                  padding: '1rem',
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                  transition: 'box-shadow 0.2s ease'
                }}
                onMouseEnter={(e) => e.target.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)'}
                onMouseLeave={(e) => e.target.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)'}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                  <span 
                    style={{
                      width: '1.25rem',
                      height: '1.25rem',
                      background: '#059669',
                      color: 'white',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.7rem',
                      fontWeight: '600',
                      marginRight: '0.75rem',
                      marginTop: '0.125rem',
                      flexShrink: 0
                    }}
                  >
                    •
                  </span>
                  <p style={{ 
                    color: '#374151', 
                    fontSize: '0.95rem', 
                    lineHeight: '1.5', 
                    margin: 0,
                    fontWeight: '500'
                  }}>
                    {renderContent(activity)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Assessments - Succinct with bullets */}
      {lessonPlan.assessments && lessonPlan.assessments.length > 0 && (
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
            <div 
              style={{
                width: '2.25rem',
                height: '2.25rem',
                background: 'linear-gradient(135deg, #ea580c 0%, #dc2626 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '0.75rem',
                flexShrink: 0
              }}
            >
              <span style={{ color: 'white', fontSize: '0.9rem' }}>📊</span>
            </div>
            <h2 style={{ fontSize: '1.375rem', fontWeight: '600', color: '#1e293b', margin: 0 }}>
              Assessment
            </h2>
          </div>
          <div 
            style={{
              background: '#fef7ed',
              borderRadius: '12px',
              border: '1px solid #fed7aa',
              padding: '1.25rem'
            }}
          >
            <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
              {lessonPlan.assessments.map((assessment, index) => (
                <li key={index} style={{ 
                  display: 'flex', 
                  alignItems: 'flex-start', 
                  marginBottom: index < lessonPlan.assessments.length - 1 ? '0.75rem' : '0'
                }}>
                  <span 
                    style={{
                      width: '1.5rem',
                      height: '1.5rem',
                      background: '#ea580c',
                      color: 'white',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      marginRight: '0.75rem',
                      marginTop: '0.125rem',
                      flexShrink: 0
                    }}
                  >
                    •
                  </span>
                  <span style={{ 
                    color: '#374151', 
                    fontSize: '0.95rem', 
                    lineHeight: '1.5',
                    fontWeight: '500'
                  }}>
                    {renderContent(assessment)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Materials */}
      {lessonPlan.materials && lessonPlan.materials.length > 0 && (
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
            <div 
              style={{
                width: '2.25rem',
                height: '2.25rem',
                background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '0.75rem',
                flexShrink: 0
              }}
            >
              <span style={{ color: 'white', fontSize: '0.9rem' }}>📦</span>
            </div>
            <h2 style={{ fontSize: '1.375rem', fontWeight: '600', color: '#1e293b', margin: 0 }}>
              Materials
            </h2>
          </div>
          <div 
            style={{
              background: '#faf5ff',
              borderRadius: '12px',
              border: '1px solid #e9d5ff',
              padding: '1.25rem'
            }}
          >
            <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
              {lessonPlan.materials.map((material, index) => (
                <li key={index} style={{ 
                  display: 'flex', 
                  alignItems: 'flex-start', 
                  marginBottom: index < lessonPlan.materials.length - 1 ? '0.5rem' : '0'
                }}>
                  <span 
                    style={{
                      width: '1.25rem',
                      height: '1.25rem',
                      background: '#7c3aed',
                      color: 'white',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.7rem',
                      fontWeight: '600',
                      marginRight: '0.75rem',
                      marginTop: '0.125rem',
                      flexShrink: 0
                    }}
                  >
                    •
                  </span>
                  <span style={{ 
                    color: '#374151', 
                    fontSize: '0.95rem', 
                    lineHeight: '1.5',
                    fontWeight: '500'
                  }}>
                    {renderContent(material)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* External Resources - Compact */}
      {lessonPlan.external_resources && lessonPlan.external_resources.length > 0 && (
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
            <div 
              style={{
                width: '2.25rem',
                height: '2.25rem',
                background: 'linear-gradient(135deg, #0891b2 0%, #0e7490 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '0.75rem',
                flexShrink: 0
              }}
            >
              <span style={{ color: 'white', fontSize: '0.9rem' }}>🔗</span>
            </div>
            <h2 style={{ fontSize: '1.375rem', fontWeight: '600', color: '#1e293b', margin: 0 }}>
              External Resources
            </h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {lessonPlan.external_resources.map((resource, index) => (
              <div 
                key={index} 
                style={{
                  background: 'white',
                  border: '1px solid #cffafe',
                  borderRadius: '8px',
                  padding: '0.75rem',
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                  transition: 'box-shadow 0.2s ease'
                }}
                onMouseEnter={(e) => e.target.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)'}
                onMouseLeave={(e) => e.target.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.05)'}
              >
                <h3 style={{ 
                  fontSize: '0.875rem', 
                  fontWeight: '600', 
                  color: '#1e293b', 
                  margin: '0 0 0.375rem 0',
                  lineHeight: '1.3'
                }}>
                  {resource.resource_title || resource.title || `Resource ${index + 1}`}
                </h3>
                <p style={{ 
                  fontSize: '0.8rem', 
                  color: '#6b7280', 
                  margin: '0 0 0.5rem 0', 
                  lineHeight: '1.4'
                }}>
                  {resource.description}
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <span 
                    style={{
                      background: '#dbeafe',
                      color: '#2563eb',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '500'
                    }}
                  >
                    {resource.source}
                  </span>
                  {resource.resource_url && (
                    <a 
                      href={resource.resource_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{
                        background: '#0891b2',
                        color: 'white',
                        padding: '0.25rem 0.75rem',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        textDecoration: 'none',
                        transition: 'background-color 0.2s ease'
                      }}
                      onMouseEnter={(e) => e.target.style.background = '#0e7490'}
                      onMouseLeave={(e) => e.target.style.background = '#0891b2'}
                    >
                      View →
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Differentiation Strategies - More understandable with bullets */}
      {lessonPlan.differentiation && (
        <div style={{ marginBottom: '0' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
            <div 
              style={{
                width: '2.25rem',
                height: '2.25rem',
                background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '0.75rem',
                flexShrink: 0
              }}
            >
              <span style={{ color: 'white', fontSize: '0.9rem' }}>🎨</span>
            </div>
            <h2 style={{ fontSize: '1.375rem', fontWeight: '600', color: '#1e293b', margin: 0 }}>
              Differentiation Strategies
            </h2>
          </div>
          <div 
            style={{
              background: '#fef2f2',
              borderRadius: '12px',
              border: '1px solid #fecaca',
              padding: '1.25rem'
            }}
          >
            <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
              {formatDifferentiation(lessonPlan.differentiation).map((strategy, index) => (
                <li key={index} style={{ 
                  display: 'flex', 
                  alignItems: 'flex-start', 
                  marginBottom: index < formatDifferentiation(lessonPlan.differentiation).length - 1 ? '0.75rem' : '0'
                }}>
                  <span 
                    style={{
                      width: '1.5rem',
                      height: '1.5rem',
                      background: '#dc2626',
                      color: 'white',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      marginRight: '0.75rem',
                      marginTop: '0.125rem',
                      flexShrink: 0
                    }}
                  >
                    •
                  </span>
                  <span style={{ 
                    color: '#374151', 
                    fontSize: '0.95rem', 
                    lineHeight: '1.5',
                    fontWeight: '500'
                  }}>
                    {strategy}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default LessonPlanDisplay;