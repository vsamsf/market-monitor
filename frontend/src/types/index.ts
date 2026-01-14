export interface Task {
  id: number;
  title: string;
  description: string;
  due_date: string | null;
  priority: 'low' | 'medium' | 'high';
  is_completed: boolean;
  created_at: string;
  completed_at: string | null;
}

export interface Reminder {
  id: number;
  title: string;
  description: string;
  datetime: string;
  recurring_type: string | null;
  is_active: boolean;
  created_at: string;
}

export interface MarketIndex {
  symbol: string;
  name: string;
  current_price: number;
  previous_close: number;
  change: number;
  change_percent: number;
  timestamp: string;
}

export interface DashboardStats {
  tasks: {
    total: number;
    today: number;
    overdue: number;
    high_priority: number;
  };
  reminders: {
    active: number;
  };
}
