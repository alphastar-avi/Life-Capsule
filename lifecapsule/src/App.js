import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [activePage, setActivePage] = useState('diary');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [diaryEntry, setDiaryEntry] = useState('');
  const [query, setQuery] = useState('');
  const [assistantResponse, setAssistantResponse] = useState('');
  const [error, setError] = useState(null);

  const handleHover = () => setSidebarOpen(true);
  const handleLeave = () => setSidebarOpen(false);

  const submitDiaryEntry = async () => {
    try {
      const response = await fetch('http://localhost:5000/save_diary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entry: diaryEntry.trim() }),
      });
      if (response.ok) {
        alert('Diary entry saved!');
        setDiaryEntry('');
      } else {
        setError('Failed to save the diary entry.');
      }
    } catch (error) {
      setError('Error saving diary entry: ' + error.message);
    }
  };

  const askAssistant = async () => {
    try {
      const response = await fetch('http://localhost:5000/analyze_diary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim() }),
      });
      const data = await response.json();
      setAssistantResponse(data.answer || 'No response received.');
    } catch (error) {
      setError('Error querying the assistant: ' + error.message);
      setAssistantResponse('Failed to get a response. Please try again later.');
    }
  };

  useEffect(() => {
    if (error) {
      alert(error);
      setError(null);
    }
  }, [error]);

  return (
    <div className="app">
      <header className="header">
        <h1 className="header-title">LifeCapsule</h1>
      </header>
      <div
        className={`sidebar ${sidebarOpen ? 'open' : ''}`}
        onMouseEnter={handleHover}
        onMouseLeave={handleLeave}
      >
        <ul className="menu-list">
          <li
            onClick={() => setActivePage('diary')}
            className={`menu-item ${activePage === 'diary' ? 'active' : ''}`}
          >
            <span className={`icon ${sidebarOpen ? '' : 'collapsed'}`}>📖</span>
            {sidebarOpen && <span className="menu-text">Diary Entry</span>}
          </li>
          <li
            onClick={() => setActivePage('assistant')}
            className={`menu-item ${activePage === 'assistant' ? 'active' : ''}`}
          >
            <span className={`icon ${sidebarOpen ? '' : 'collapsed'}`}>🤖</span>
            {sidebarOpen && <span className="menu-text">Personal Assistant</span>}
          </li>
        </ul>
      </div>
      <div className="content">
        {activePage === 'diary' ? (
          <div className="diary">
            <h2 className="section-title">Diary Entry</h2>
            <textarea
              placeholder="Write your diary entry here..."
              value={diaryEntry}
              onChange={(e) => setDiaryEntry(e.target.value)}
              className="diary-input"
            />
            <button
              onClick={submitDiaryEntry}
              className="submit-button"
              disabled={!diaryEntry.trim()}
            >
              Save Entry
            </button>
          </div>
        ) : (
          <div className="assistant">
            <h2 className="section-title">Personal Assistant</h2>
            <input
              type="text"
              placeholder="Ask something..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="query-input"
            />
            <button
              onClick={askAssistant}
              className="ask-button"
              disabled={!query.trim()}
            >
              Submit Query
            </button>
            <div className="response-box animated-box">{assistantResponse}</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
