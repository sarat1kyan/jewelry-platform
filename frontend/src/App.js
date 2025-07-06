import React, { useState, useEffect } from 'react';

const JewelryCustomizationPlatform = () => {
  const [parameters, setParameters] = useState({});
  const [selections, setSelections] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  useEffect(() => {
    loadParameters();
  }, []);

  const loadParameters = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/parameters`);
      const data = await response.json();
      
      if (data.success) {
        setParameters(data.parameters);
        const initialSelections = {};
        Object.keys(data.parameters).forEach(key => {
          initialSelections[key] = '';
        });
        setSelections(initialSelections);
      }
    } catch (err) {
      setError('Error loading parameters');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Jewelry Customization Platform</h1>
      <p>Select jewelry parameters to find matching CAD files</p>
      
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}
      
      <div style={{ marginTop: '20px' }}>
        {Object.entries(parameters).map(([param, options]) => (
          <div key={param} style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>
              {param}:
            </label>
            <select
              value={selections[param] || ''}
              onChange={(e) => setSelections({...selections, [param]: e.target.value})}
              style={{ width: '200px', padding: '5px' }}
            >
              <option value="">Select {param}</option>
              {options.map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
};

export default JewelryCustomizationPlatform;
