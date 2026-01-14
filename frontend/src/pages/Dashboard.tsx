import {
    Assignment,
    NotificationsActive,
    PriorityHigh,
    TrendingUp,
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Card,
    CardContent,
    CircularProgress,
    Grid,
    Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { systemAPI } from '../services/api';
import type { DashboardStats } from '../types';

function StatCard({ title, value, icon, color }: any) {
  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4">{value}</Typography>
          </Box>
          <Box sx={{ color, fontSize: 48 }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const response = await systemAPI.getDashboardStats();
      setStats(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard stats');
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

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Tasks"
            value={stats?.tasks.total || 0}
            icon={<Assignment />}
            color="#1976d2"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Tasks"
            value={stats?.tasks.today || 0}
            icon={<TrendingUp />}
            color="#2e7d32"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Overdue Tasks"
            value={stats?.tasks.overdue || 0}
            icon={<PriorityHigh />}
            color="#d32f2f"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Reminders"
            value={stats?.reminders.active || 0}
            icon={<NotificationsActive />}
            color="#ed6c02"
          />
        </Grid>

        {stats && stats.tasks.high_priority && stats.tasks.high_priority > 0 && (
          <Grid item xs={12}>
            <Alert severity="warning">
              You have {stats.tasks.high_priority} high-priority task(s) pending.
            </Alert>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
