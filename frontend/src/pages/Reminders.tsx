import { Add, Delete } from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Chip,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    IconButton,
    List,
    ListItem,
    ListItemSecondaryAction,
    ListItemText,
    MenuItem,
    Paper,
    TextField,
    Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { reminderAPI } from '../services/api';
import type { Reminder } from '../types';

export default function Reminders() {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    datetime: '',
    recurring_type: '',
  });

  useEffect(() => {
    loadReminders();
  }, []);

  const loadReminders = async () => {
    try {
      const response = await reminderAPI.getAll(true);
      setReminders(response.data.reminders);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load reminders');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReminder = async () => {
    try {
      await reminderAPI.create(formData);
      setDialogOpen(false);
      setFormData({ title: '', description: '', datetime: '', recurring_type: '' });
      loadReminders();
    } catch (err: any) {
      setError(err.message || 'Failed to create reminder');
    }
  };

  const handleDeleteReminder = async (id: number) => {
    if (!confirm('Are you sure you want to delete this reminder?')) return;
    try {
      await reminderAPI.delete(id);
      loadReminders();
    } catch (err: any) {
      setError(err.message || 'Failed to delete reminder');
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Reminders</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setDialogOpen(true)}
        >
          Add Reminder
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Paper>
        <List>
          {reminders.length === 0 ? (
            <ListItem>
              <ListItemText primary="No reminders found. Create one to get started!" />
            </ListItem>
          ) : (
            reminders.map((reminder) => (
              <ListItem key={reminder.id} divider>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="h6">{reminder.title}</Typography>
                      {reminder.recurring_type && (
                        <Chip
                          label={reminder.recurring_type}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" color="textSecondary">
                        {reminder.description || 'No description'}
                      </Typography>
                      <Typography variant="caption" color="primary">
                        {new Date(reminder.datetime).toLocaleString()}
                      </Typography>
                    </>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    color="error"
                    onClick={() => handleDeleteReminder(reminder.id)}
                  >
                    <Delete />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))
          )}
        </List>
      </Paper>

      {/* Create Reminder Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Reminder</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Title"
              fullWidth
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
            <TextField
              label="Date & Time"
              type="datetime-local"
              fullWidth
              required
              InputLabelProps={{ shrink: true }}
              value={formData.datetime}
              onChange={(e) => setFormData({ ...formData, datetime: e.target.value })}
            />
            <TextField
              select
              label="Recurring"
              fullWidth
              value={formData.recurring_type}
              onChange={(e) => setFormData({ ...formData, recurring_type: e.target.value })}
            >
              <MenuItem value="">None</MenuItem>
              <MenuItem value="daily">Daily</MenuItem>
              <MenuItem value="weekly">Weekly</MenuItem>
              <MenuItem value="monthly">Monthly</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateReminder}
            variant="contained"
            disabled={!formData.title || !formData.datetime}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
