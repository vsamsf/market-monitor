import { TrendingDown, TrendingUp } from '@mui/icons-material';
import {
    Alert,
    Box,
    Card,
    CardContent,
    Chip,
    CircularProgress,
    Grid,
    Paper,
    Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { marketAPI } from '../services/api';
import type { MarketIndex } from '../types';

export default function Market() {
  const [indices, setIndices] = useState<MarketIndex[]>([]);
  const [summary, setSummary] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMarketData();
    const interval = setInterval(loadMarketData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const loadMarketData = async () => {
    try {
      const [indicesRes, summaryRes] = await Promise.all([
        marketAPI.getIndices(),
        marketAPI.getSummary(),
      ]);
      setIndices(indicesRes.data.indices || []);
      setSummary(summaryRes.data.summary || '');
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load market data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Market Data
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={3} sx={{ mt: 1 }}>
        {indices.map((index) => (
          <Grid item xs={12} sm={6} md={4} key={index.symbol}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {index.name}
                </Typography>
                <Typography variant="h4" gutterBottom>
                  {index.current_price?.toFixed(2) || 'N/A'}
                </Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  {index.change >= 0 ? (
                    <TrendingUp color="success" />
                  ) : (
                    <TrendingDown color="error" />
                  )}
                  <Chip
                    label={`${index.change >= 0 ? '+' : ''}${index.change?.toFixed(2)} (${index.change_percent?.toFixed(2)}%)`}
                    color={index.change >= 0 ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  Prev Close: {index.previous_close?.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {summary && (
        <Paper sx={{ mt: 4, p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Market Summary
          </Typography>
          <Typography
            component="pre"
            sx={{
              whiteSpace: 'pre-wrap',
              fontFamily: 'monospace',
              fontSize: '0.9rem',
            }}
          >
            {summary}
          </Typography>
        </Paper>
      )}

      {indices.length === 0 && !error && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Market data may be unavailable outside trading hours (9:15 AM - 3:30 PM IST).
        </Alert>
      )}
    </Box>
  );
}
