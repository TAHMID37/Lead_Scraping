import React, { useState } from 'react';
import IndeedTab from './components/IndeedTab';
import SeekTab from './components/SeekTab';
import CareerOneTab from './components/CareerOneTab';

function App() {
  const [activeTab, setActiveTab] = useState('indeed');

  return (
    <div className="app">
      <header className="header">
        <h1>Job Scraper - ANZSCO 482 Validation</h1>
      </header>
      
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'indeed' ? 'active' : ''}`}
          onClick={() => setActiveTab('indeed')}
        >
          Indeed
        </button>
        <button 
          className={`tab ${activeTab === 'seek' ? 'active' : ''}`}
          onClick={() => setActiveTab('seek')}
        >
          Seek
        </button>
        <button 
          className={`tab ${activeTab === 'careerone' ? 'active' : ''}`}
          onClick={() => setActiveTab('careerone')}
        >
          CareerOne
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'indeed' && <IndeedTab />}
        {activeTab === 'seek' && <SeekTab />}
        {activeTab === 'careerone' && <CareerOneTab />}
      </div>
    </div>
  );
}

export default App;
