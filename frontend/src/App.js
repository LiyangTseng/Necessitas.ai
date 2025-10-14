import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Container, AppBar, Toolbar, Typography, Button, Chip } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter, BarChart, Bar } from 'recharts';

// Components
import CompanyRadar from './components/CompanyRadar';
import SimilarityGraph from './components/SimilarityGraph';
import MarketInsights from './components/MarketInsights';
import AgentStatus from './components/AgentStatus';
import Navigation from './components/Navigation';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

function App() {
  const [agentStatus, setAgentStatus] = useState({
    isRunning: true,
    lastUpdate: new Date().toISOString(),
    companiesMonitored: 10,
    dataPoints: 1250,
    insightsGenerated: 45
  });

  const [marketData, setMarketData] = useState({
    companies: [
      { name: 'Amazon', cluster: 0, similarity: 0.85, technologies: ['AWS', 'AI', 'ML'] },
      { name: 'Google', cluster: 0, similarity: 0.82, technologies: ['AI', 'ML', 'Cloud'] },
      { name: 'Microsoft', cluster: 0, similarity: 0.78, technologies: ['Azure', 'AI', 'Cloud'] },
      { name: 'OpenAI', cluster: 1, similarity: 0.91, technologies: ['AI', 'LLM', 'GPT'] },
      { name: 'Anthropic', cluster: 1, similarity: 0.89, technologies: ['AI', 'LLM', 'Claude'] },
      { name: 'Nvidia', cluster: 2, similarity: 0.76, technologies: ['GPU', 'AI', 'Hardware'] },
      { name: 'Tesla', cluster: 3, similarity: 0.65, technologies: ['EV', 'AI', 'Autonomous'] },
      { name: 'Netflix', cluster: 4, similarity: 0.58, technologies: ['Streaming', 'Content', 'AI'] }
    ],
    similarities: [
      { company1: 'Amazon', company2: 'Google', similarity: 0.85 },
      { company1: 'Google', company2: 'Microsoft', similarity: 0.82 },
      { company1: 'OpenAI', company2: 'Anthropic', similarity: 0.91 },
      { company1: 'Amazon', company2: 'Microsoft', similarity: 0.78 },
      { company1: 'Nvidia', company2: 'OpenAI', similarity: 0.76 }
    ],
    trends: [
      { name: 'AI Infrastructure', companies: 8, growth: 25, confidence: 0.9 },
      { name: 'Cloud Computing', companies: 6, growth: 18, confidence: 0.85 },
      { name: 'Machine Learning', companies: 7, growth: 22, confidence: 0.88 },
      { name: 'Autonomous Systems', companies: 3, growth: 15, confidence: 0.75 }
    ]
  });

  const [selectedCompany, setSelectedCompany] = useState(null);
  const [viewMode, setViewMode] = useState('graph'); // 'graph', 'table', 'insights'

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setAgentStatus(prev => ({
        ...prev,
        lastUpdate: new Date().toISOString(),
        dataPoints: prev.dataPoints + Math.floor(Math.random() * 10)
      }));
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          {/* Header */}
          <AppBar position="static" elevation={2}>
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
                🚀 CompanyRadar
              </Typography>
              <Chip
                label={agentStatus.isRunning ? "Agent Active" : "Agent Inactive"}
                color={agentStatus.isRunning ? "success" : "error"}
                size="small"
                sx={{ mr: 2 }}
              />
              <Typography variant="body2" sx={{ mr: 2 }}>
                Last Update: {new Date(agentStatus.lastUpdate).toLocaleTimeString()}
              </Typography>
            </Toolbar>
          </AppBar>

          {/* Navigation */}
          <Navigation
            viewMode={viewMode}
            setViewMode={setViewMode}
            selectedCompany={selectedCompany}
            setSelectedCompany={setSelectedCompany}
            companies={marketData.companies}
          />

          {/* Main Content */}
          <Container maxWidth="xl" sx={{ flexGrow: 1, py: 3 }}>
            <Routes>
              <Route path="/" element={
                <CompanyRadar
                  marketData={marketData}
                  selectedCompany={selectedCompany}
                  setSelectedCompany={setSelectedCompany}
                  viewMode={viewMode}
                />
              } />
              <Route path="/similarity" element={
                <SimilarityGraph
                  marketData={marketData}
                  selectedCompany={selectedCompany}
                  setSelectedCompany={setSelectedCompany}
                />
              } />
              <Route path="/insights" element={
                <MarketInsights
                  marketData={marketData}
                  agentStatus={agentStatus}
                />
              } />
              <Route path="/agent" element={
                <AgentStatus
                  agentStatus={agentStatus}
                  setAgentStatus={setAgentStatus}
                />
              } />
            </Routes>
          </Container>

          {/* Footer */}
          <Box component="footer" sx={{ py: 2, px: 2, bgcolor: 'grey.100' }}>
            <Typography variant="body2" color="text.secondary" align="center">
              CompanyRadar - Autonomous Market Intelligence Agent |
              Built for AWS AI Agent Global Hackathon 2025
            </Typography>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;

