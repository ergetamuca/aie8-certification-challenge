import React from 'react';

const LandingPage = ({ onStartGenerating }) => {
  return (
    <div 
      style={{
        width: '100vw',
        minHeight: 'calc(100vh - 80px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        backgroundColor: '#f8fafc',
        boxSizing: 'border-box',
        margin: 0
      }}
    >
      <div 
        style={{
          textAlign: 'center',
          width: '100%',
          maxWidth: 'none'
        }}
      >
        {/* Hero Section */}
        <div style={{ marginBottom: '3rem' }}>
          <div 
            style={{
              width: '5rem',
              height: '5rem',
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 2rem auto'
            }}
          >
            <span style={{ color: 'white', fontSize: '2.5rem' }}>📚</span>
          </div>
          
          <h1 style={{ fontSize: '3rem', fontWeight: 'bold', color: '#1e293b', marginBottom: '1.5rem' }}>
            Welcome to <span style={{ color: '#2563eb' }}>LessonLab</span>
          </h1>
          
          <p style={{ fontSize: '1.25rem', color: '#475569', marginBottom: '2rem', lineHeight: '1.6' }}>
            Transform your lesson planning with AI-powered tools designed specifically for educators. 
            Create comprehensive, standards-aligned lesson plans in minutes, not hours.
          </p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', justifyContent: 'center', alignItems: 'center', marginBottom: '3rem' }}>
            <button
              onClick={onStartGenerating}
              style={{
                background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                padding: '1rem 2rem',
                fontSize: '1.125rem',
                fontWeight: '600',
                cursor: 'pointer',
                width: '100%',
                maxWidth: '250px'
              }}
            >
              Get Started Free
            </button>
            <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>No signup required • Instant results</p>
          </div>
        </div>

        {/* Features Grid - Three Cards in One Row */}
        <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '4rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <div style={{ 
            background: 'white', 
            borderRadius: '12px', 
            border: '1px solid #cbd5e1', 
            padding: '1.5rem', 
            textAlign: 'center',
            flex: '1',
            minWidth: '300px'
          }}>
            <div style={{ width: '4rem', height: '4rem', backgroundColor: '#dbeafe', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem auto' }}>
              <span style={{ color: '#2563eb', fontSize: '1.5rem' }}>🤖</span>
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1e293b', marginBottom: '0.75rem' }}>AI-Powered Planning</h3>
            <p style={{ color: '#6b7280', fontSize: '1rem', lineHeight: '1.6' }}>
              Advanced artificial intelligence creates personalized lesson plans tailored to your curriculum and teaching style.
            </p>
          </div>
          
          <div style={{ 
            background: 'white', 
            borderRadius: '12px', 
            border: '1px solid #cbd5e1', 
            padding: '1.5rem', 
            textAlign: 'center',
            flex: '1',
            minWidth: '300px'
          }}>
            <div style={{ width: '4rem', height: '4rem', backgroundColor: '#d1fae5', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem auto' }}>
              <span style={{ color: '#059669', fontSize: '1.5rem' }}>⚡</span>
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1e293b', marginBottom: '0.75rem' }}>Lightning Fast</h3>
            <p style={{ color: '#6b7280', fontSize: '1rem', lineHeight: '1.6' }}>
              Generate comprehensive lesson plans in seconds. Spend more time teaching, less time planning.
            </p>
          </div>
          
          <div style={{ 
            background: 'white', 
            borderRadius: '12px', 
            border: '1px solid #cbd5e1', 
            padding: '1.5rem', 
            textAlign: 'center',
            flex: '1',
            minWidth: '300px'
          }}>
            <div style={{ width: '4rem', height: '4rem', backgroundColor: '#fed7aa', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem auto' }}>
              <span style={{ color: '#ea580c', fontSize: '1.5rem' }}>📚</span>
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1e293b', marginBottom: '0.75rem' }}>Standards-Aligned</h3>
            <p style={{ color: '#6b7280', fontSize: '1rem', lineHeight: '1.6' }}>
              Every lesson plan is aligned with educational standards and includes assessment strategies.
            </p>
          </div>
        </div>

        {/* Stats Section */}
        <div style={{ background: 'white', borderRadius: '12px', border: '1px solid #cbd5e1', padding: '2rem', marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1e293b', marginBottom: '1.5rem', textAlign: 'center' }}>
            Trusted by Educators Worldwide
          </h2>
          <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <div style={{ textAlign: 'center', flex: '1', minWidth: '120px' }}>
              <div style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#2563eb', marginBottom: '0.5rem' }}>1000+</div>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Lesson Plans Created</div>
            </div>
            <div style={{ textAlign: 'center', flex: '1', minWidth: '120px' }}>
              <div style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#059669', marginBottom: '0.5rem' }}>50+</div>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Subjects Covered</div>
            </div>
            <div style={{ textAlign: 'center', flex: '1', minWidth: '120px' }}>
              <div style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#ea580c', marginBottom: '0.5rem' }}>K-12</div>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>All Grade Levels</div>
            </div>
            <div style={{ textAlign: 'center', flex: '1', minWidth: '120px' }}>
              <div style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#374151', marginBottom: '0.5rem' }}>24/7</div>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Always Available</div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
          <p style={{ fontSize: '1.125rem', color: '#475569', marginBottom: '1.5rem' }}>
            Ready to streamline your lesson planning?
          </p>
          <button
            onClick={onStartGenerating}
            style={{
              background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '1rem 2rem',
              fontSize: '1.125rem',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Start Creating Lessons
          </button>
        </div>

        {/* Footer */}
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>
            Built for educators, by educators. Supporting teachers worldwide.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;