import axios from 'axios';

// Base API URL - uses proxy configured in package.json
const API_BASE_URL = '/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Target Management
export const targetAPI = {
  // Create a new target
  create: async (targetData) => {
    const response = await api.post('/targets', targetData);
    return response.data;
  },

  // Get all targets
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/targets', {
      params: { skip, limit },
    });
    return response.data;
  },

  // Get target by ID
  getById: async (targetId) => {
    const response = await api.get(`/targets/${targetId}`);
    return response.data;
  },

  // Update target
  update: async (targetId, targetData) => {
    const response = await api.put(`/targets/${targetId}`, targetData);
    return response.data;
  },

  // Delete target
  delete: async (targetId) => {
    const response = await api.delete(`/targets/${targetId}`);
    return response.data;
  },
};

// Scan Management
export const scanAPI = {
  // Start a new scan
  start: async (scanConfig) => {
    const response = await api.post('/scans/start', scanConfig);
    return response.data;
  },

  // Get scan progress
  getProgress: async (scanId) => {
    const response = await api.get(`/scans/${scanId}/progress`);
    return response.data;
  },

  // Get scan results
  getResults: async (scanId) => {
    const response = await api.get(`/scans/${scanId}/results`);
    return response.data;
  },

  // Get all scans
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/scans', {
      params: { skip, limit },
    });
    return response.data;
  },

  // Cancel scan
  cancel: async (scanId) => {
    const response = await api.post(`/scans/${scanId}/cancel`);
    return response.data;
  },
};

// Vulnerability Management
export const vulnerabilityAPI = {
  // Get all vulnerabilities
  getAll: async (filters = {}) => {
    const response = await api.get('/vulnerabilities', {
      params: filters,
    });
    return response.data;
  },

  // Get vulnerability by ID
  getById: async (vulnId) => {
    const response = await api.get(`/vulnerabilities/${vulnId}`);
    return response.data;
  },

  // Get vulnerabilities by scan
  getByScan: async (scanId) => {
    const response = await api.get('/vulnerabilities', {
      params: { scan_id: scanId },
    });
    return response.data;
  },

  // Get vulnerabilities by severity
  getBySeverity: async (severity) => {
    const response = await api.get('/vulnerabilities', {
      params: { severity },
    });
    return response.data;
  },
};

// Finding Management
export const findingAPI = {
  // Get all findings
  getAll: async (filters = {}) => {
    const response = await api.get('/findings', {
      params: filters,
    });
    return response.data;
  },

  // Get findings by scan
  getByScan: async (scanId) => {
    const response = await api.get('/findings', {
      params: { scan_id: scanId },
    });
    return response.data;
  },
};

// Enumeration
export const enumerationAPI = {
  // Discover hosts on network
  discoverHosts: async (networkCIDR) => {
    const response = await api.post('/enumerate/discover', {
      network: networkCIDR,
    });
    return response.data;
  },

  // Enumerate ports on a target
  enumeratePorts: async (target, scanType = 'default') => {
    const response = await api.post('/enumerate/ports', {
      target,
      scan_type: scanType,
    });
    return response.data;
  },
};

// Scanner Status
export const scannerAPI = {
  // Get available scanners
  getAvailable: async () => {
    const response = await api.get('/scanners/available');
    return response.data;
  },
};

// WebSocket Connection for Real-time Updates
export const createWebSocket = (onMessage, onError) => {
  const wsURL = window.location.protocol === 'https:' 
    ? `wss://${window.location.host}/ws`
    : `ws://${window.location.host}/ws`;

  const ws = new WebSocket(wsURL);

  ws.onopen = () => {
    console.log('WebSocket connected');
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('WebSocket message parse error:', error);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };

  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };

  return ws;
};

export default api;
