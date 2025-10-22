import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import LessonPlanGenerator from './components/LessonPlanGenerator';
import LessonPlanDisplay from './components/LessonPlanDisplay';
import LandingPage from './components/LandingPage';

function App() {
  const [lessonPlan, setLessonPlan] = useState(null);
  const [currentView, setCurrentView] = useState('landing');

  const handleLessonPlanGenerated = (generatedPlan) => {
    setLessonPlan(generatedPlan);
    setCurrentView('result');
  };

  const handleStartGenerating = () => {
    setCurrentView('form');
  };

  const handleBackToForm = () => {
    setCurrentView('form');
    setLessonPlan(null);
  };

  const handleBackToLanding = () => {
    setCurrentView('landing');
    setLessonPlan(null);
  };

  return (
    <div style={{ 
      width: '100vw', 
      minHeight: '100vh', 
      backgroundColor: '#f8fafc',
      margin: 0,
      padding: 0,
      boxSizing: 'border-box'
    }}>
      {/* Header */}
      <header style={{ 
        width: '100%',
        backgroundColor: 'white', 
        boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)', 
        borderBottom: '1px solid #e5e7eb',
        padding: '1rem 2rem',
        boxSizing: 'border-box',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{ 
          width: '100%',
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center' 
        }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.75rem' 
          }}>
            <div style={{
              width: '2.5rem',
              height: '2.5rem',
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <span style={{ color: 'white', fontWeight: 'bold', fontSize: '1.125rem' }}>LL</span>
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1e293b', margin: 0 }}>LessonLab</h1>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: 0 }}>AI-powered educational planning</p>
            </div>
          </div>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '1rem' 
          }}>
            {currentView !== 'landing' && (
              <button
                onClick={handleBackToLanding}
                style={{
                  fontSize: '0.875rem',
                  color: '#6b7280',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'color 0.2s'
                }}
                onMouseEnter={(e) => e.target.style.color = '#1e293b'}
                onMouseLeave={(e) => e.target.style.color = '#6b7280'}
              >
                ← Back to Home
              </button>
            )}
            <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
              Welcome, Teacher! 👋
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      {currentView === 'landing' ? (
        <LandingPage onStartGenerating={handleStartGenerating} />
      ) : (
        <main style={{ 
          width: '100%', 
          padding: '2rem',
          boxSizing: 'border-box',
          minHeight: 'calc(100vh - 80px)'
        }}>
          {currentView === 'form' && (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              minHeight: '60vh',
              width: '100%'
            }}>
              <div style={{ width: '100%' }}>
                <LessonPlanGenerator onLessonPlanGenerated={handleLessonPlanGenerated} />
              </div>
            </div>
          )}
          
          {currentView === 'result' && (
            <div style={{ 
              display: 'flex', 
              gap: '2rem',
              width: '100%',
              alignItems: 'flex-start',
              maxWidth: '1600px',
              margin: '0 auto'
            }}>
              {/* Left Panel - Lesson Plan Generator */}
              <div style={{ 
                flex: '0 0 45%',
                minWidth: '400px',
                position: 'sticky',
                top: '6rem'
              }}>
                <div style={{ marginBottom: '1rem' }}>
                  <button
                    onClick={handleBackToForm}
                    style={{
                      fontSize: '0.875rem',
                      color: '#6b7280',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      marginBottom: '1rem',
                      transition: 'color 0.2s',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}
                    onMouseEnter={(e) => e.target.style.color = '#1e293b'}
                    onMouseLeave={(e) => e.target.style.color = '#6b7280'}
                  >
                    ← Back to Form
                  </button>
                </div>
                <LessonPlanGenerator onLessonPlanGenerated={handleLessonPlanGenerated} />
              </div>

              {/* Right Panel - Lesson Plan Display */}
              <div style={{ 
                flex: '0 0 55%',
                minWidth: '400px'
              }}>
                <LessonPlanDisplay lessonPlan={lessonPlan} />
              </div>
            </div>
          )}
        </main>
      )}
      
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: '#404040',
            color: '#fff',
            borderRadius: '8px',
          },
        }}
      />
    </div>
  );
}

export default App;