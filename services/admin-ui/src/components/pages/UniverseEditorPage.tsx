import React from 'react';
import UniverseEditor from '../universe/UniverseEditor';
import './pages.css';

const UniverseEditorPage: React.FC = () => {
  return (
    <>
      <div className="page-header">
        <h2>Universe Editor</h2>
        <p className="page-description">
          Interactive editor for visualizing and modifying the game universe.
        </p>
      </div>
      
      <div className="universe-editor-wrapper">
        <UniverseEditor />
      </div>
    </>
  );
};

export default UniverseEditorPage;