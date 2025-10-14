import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  ToggleButton,
  ToggleButtonGroup,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Business,
  Timeline,
  Insights,
  AutoGraph,
  TableView,
  AccountTree
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const CompanyRadar = ({ marketData, selectedCompany, setSelectedCompany, viewMode }) => {
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('7d');
  const [filterCluster, setFilterCluster] = useState('all');

  // Mock data for charts
  const similarityTrendData = [
    { date: '2024-01-01', similarity: 0.75 },
    { date: '2024-01-02', similarity: 0.78 },
    { date: '2024-01-03', similarity: 0.82 },
    { date: '2024-01-04', similarity: 0.85 },
    { date: '2024-01-05', similarity: 0.88 },
    { date: '2024-01-06', similarity: 0.91 },
    { date: '2024-01-07', similarity: 0.89 }
  ];

  const clusterData = [
    { name: 'Cloud & AI', value: 3, color: '#8884d8' },
    { name: 'AI & LLM', value: 2, color: '#82ca9d' },
    { name: 'Hardware & AI', value: 1, color: '#ffc658' },
    { name: 'Autonomous', value: 1, color: '#ff7300' },
    { name: 'Content & Media', value: 1, color: '#00ff00' }
  ];

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00'];

  const handleCompanySelect = (company) => {
    setSelectedCompany(company);
  };

  const getClusterColor = (clusterId) => {
    return COLORS[clusterId % COLORS.length];
  };

  const filteredCompanies = marketData.companies.filter(company => 
    filterCluster === 'all' || company.cluster.toString() === filterCluster
  );

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          🎯 Company Radar Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Autonomous market intelligence showing company similarities and strategic convergence
        </Typography>
        
        {/* Controls */}
        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(e, newMode) => setViewMode(newMode)}
            size="small"
          >
            <ToggleButton value="graph">
              <AutoGraph sx={{ mr: 1 }} />
              Graph View
            </ToggleButton>
            <ToggleButton value="table">
              <TableView sx={{ mr: 1 }} />
              Table View
            </ToggleButton>
            <ToggleButton value="insights">
              <Insights sx={{ mr: 1 }} />
              Insights
            </ToggleButton>
          </ToggleButtonGroup>

          <ToggleButtonGroup
            value={timeRange}
            exclusive
            onChange={(e, newRange) => setTimeRange(newRange)}
            size="small"
          >
            <ToggleButton value="24h">24h</ToggleButton>
            <ToggleButton value="7d">7d</ToggleButton>
            <ToggleButton value="30d">30d</ToggleButton>
          </ToggleButtonGroup>

          <ToggleButtonGroup
            value={filterCluster}
            exclusive
            onChange={(e, newCluster) => setFilterCluster(newCluster)}
            size="small"
          >
            <ToggleButton value="all">All Clusters</ToggleButton>
            <ToggleButton value="0">Cloud & AI</ToggleButton>
            <ToggleButton value="1">AI & LLM</ToggleButton>
            <ToggleButton value="2">Hardware</ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Company Overview */}
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Business sx={{ mr: 1 }} />
                Company Similarity Analysis
              </Typography>
              
              {viewMode === 'graph' && (
                <Box sx={{ height: 400, mt: 2 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart data={filteredCompanies}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Scatter 
                        dataKey="similarity" 
                        fill="#1976d2"
                        onClick={(data) => handleCompanySelect(data.name)}
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                </Box>
              )}

              {viewMode === 'table' && (
                <Box sx={{ mt: 2 }}>
                  <List>
                    {filteredCompanies.map((company, index) => (
                      <React.Fragment key={company.name}>
                        <ListItem 
                          button 
                          onClick={() => handleCompanySelect(company)}
                          sx={{ 
                            bgcolor: selectedCompany?.name === company.name ? 'primary.light' : 'transparent',
                            borderRadius: 1,
                            mb: 1
                          }}
                        >
                          <ListItemIcon>
                            <Box
                              sx={{
                                width: 12,
                                height: 12,
                                borderRadius: '50%',
                                bgcolor: getClusterColor(company.cluster)
                              }}
                            />
                          </ListItemIcon>
                          <ListItemText
                            primary={company.name}
                            secondary={
                              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                                <Chip 
                                  label={`Cluster ${company.cluster}`} 
                                  size="small" 
                                  color="primary" 
                                  variant="outlined"
                                />
                                <Chip 
                                  label={`${(company.similarity * 100).toFixed(1)}% similar`} 
                                  size="small" 
                                  color="secondary"
                                />
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < filteredCompanies.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                </Box>
              )}

              {viewMode === 'insights' && (
                <Box sx={{ mt: 2 }}>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      <strong>AI Agent Insights:</strong> The system has identified 3 strategic clusters 
                      with high convergence patterns. Companies in Cluster 0 (Cloud & AI) show 85% 
                      average similarity, indicating strong market convergence.
                    </Typography>
                  </Alert>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Paper sx={{ p: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
                        <Typography variant="h6">High Convergence</Typography>
                        <Typography variant="body2">
                          OpenAI and Anthropic show 91% similarity - both focused on LLM development
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Paper sx={{ p: 2, bgcolor: 'secondary.light', color: 'secondary.contrastText' }}>
                        <Typography variant="h6">Emerging Trends</Typography>
                        <Typography variant="body2">
                          AI infrastructure investments increasing 25% across monitored companies
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={2}>
            {/* Cluster Distribution */}
            <Grid item xs={12}>
              <Card elevation={2}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cluster Distribution
                  </Typography>
                  <Box sx={{ height: 200 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={clusterData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {clusterData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Similarity Trends */}
            <Grid item xs={12}>
              <Card elevation={2}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Similarity Trends
                  </Typography>
                  <Box sx={{ height: 200 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={similarityTrendData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis domain={[0, 1]} />
                        <Tooltip />
                        <Line 
                          type="monotone" 
                          dataKey="similarity" 
                          stroke="#1976d2" 
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Top Similarities */}
            <Grid item xs={12}>
              <Card elevation={2}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Top Similarities
                  </Typography>
                  <List dense>
                    {marketData.similarities.slice(0, 5).map((similarity, index) => (
                      <ListItem key={index}>
                        <ListItemText
                          primary={`${similarity.company1} ↔ ${similarity.company2}`}
                          secondary={`${(similarity.similarity * 100).toFixed(1)}% similar`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>

      {/* Selected Company Details */}
      {selectedCompany && (
        <Card elevation={3} sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📊 {selectedCompany.name} Analysis
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  <strong>Cluster:</strong> {selectedCompany.cluster}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Similarity Score:</strong> {(selectedCompany.similarity * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Technologies:</strong> {selectedCompany.technologies.join(', ')}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {selectedCompany.technologies.map((tech, index) => (
                    <Chip key={index} label={tech} size="small" color="primary" />
                  ))}
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default CompanyRadar;

