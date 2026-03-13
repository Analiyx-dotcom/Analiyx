// Mock data for Analiyx clone

export const testimonials = [
  {
    id: 1,
    quote: "Analiyx AI has completely transformed how we handle data across our retail chain.",
    description: "Before Analiyx, our team spent days manually pulling reports from different systems. Now, we connect our Zoho Books and Google Sheets, ask questions in plain English, and get instant insights. The AI-powered dashboards have helped us reduce inventory waste by 30% in just three months.",
    name: "Priya Sharma",
    role: "COO at FreshBasket India",
    avatar: "PS"
  },
  {
    id: 2,
    quote: "From reactive guessing to proactive decision-making — Analiyx made it possible.",
    description: "Managing ad spend across Google and Meta was a nightmare for our small marketing team. Analiyx unified all our campaign data into one dashboard with real-time metrics. We identified underperforming campaigns instantly and reallocated budgets, resulting in a 45% improvement in ROAS within the first quarter.",
    name: "Rajesh Menon",
    role: "Founder & CEO at GrowthPulse Digital, Bangalore",
    avatar: "RM"
  },
  {
    id: 3,
    quote: "The best no-code analytics platform we have used — and we have tried many.",
    description: "As a D2C brand, we needed to track everything from Shopify orders to Meta Ads performance to warehouse data. Analiyx connected all our sources in minutes. The AI visibility feature even showed us how our brand appears across ChatGPT and Gemini searches. Truly next-level for a lean team like ours.",
    name: "Ananya Reddy",
    role: "Head of Growth at StyleKraft, Hyderabad",
    avatar: "AR"
  }
];

export const integrations = [
  { name: 'PostgreSQL', icon: 'database', color: '#336791' },
  { name: 'MySQL', icon: 'database', color: '#4479A1' },
  { name: 'MongoDB', icon: 'database', color: '#47A248' },
  { name: 'AI Visibility', icon: 'brain', color: '#8B5CF6' },
  { name: 'Google Sheets', icon: 'sheet', color: '#0F9D58' },
  { name: 'Excel', icon: 'file-spreadsheet', color: '#217346' },
  { name: 'CSV', icon: 'file-text', color: '#6B7280' },
  { name: 'Meta Ads', icon: 'facebook', color: '#1877F2' },
  { name: 'Shopify', icon: 'shopping-bag', color: '#96BF48' },
  { name: 'Zoho Books', icon: 'book-open', color: '#E42527' },
  { name: 'Google Analytics', icon: 'bar-chart', color: '#E37400' },
  { name: 'Google Ads', icon: 'megaphone', color: '#4285F4' },
  { name: 'HubSpot', icon: 'users', color: '#FF7A59' },
  { name: 'Salesforce', icon: 'cloud', color: '#00A1E0' }
];

export const pricingPlans = [
  {
    id: 1,
    name: 'Starter',
    description: 'Perfect for small businesses getting started with data analytics.',
    price: 1599,
    period: 'month',
    features: [
      'Up to 2 workspaces',
      'No daily requests cap',
      '100 credits monthly',
      'Add up to 2 team members',
      'Email support',
      'Basic analytics dashboard'
    ],
    highlighted: false
  },
  {
    id: 2,
    name: 'Business Pro',
    description: 'Our recommended plan for growing businesses.',
    price: 4999,
    period: 'month',
    features: [
      'Up to 10 workspaces',
      'No daily requests cap',
      '500 credits monthly',
      'Add up to 10 team members',
      'Priority email & chat support',
      'Advanced analytics & reports',
      'API access',
      'Custom integrations'
    ],
    highlighted: true
  },
  {
    id: 3,
    name: 'Enterprise',
    description: 'For large teams with custom requirements.',
    price: 'Custom',
    period: '',
    features: [
      'Unlimited workspaces',
      'Unlimited requests',
      'Custom credits allocation',
      'Unlimited team members',
      '24/7 dedicated support',
      'White-label solution',
      'On-premise deployment option',
      'Custom SLA & contracts',
      'Dedicated account manager'
    ],
    highlighted: false
  }
];

export const trustedBrands = [
  'Zivot', 'Edanra', 'TechCorp', 'DataFlow', '100Sheep', 'Brooklyn', 'Congo Clothing', 'Game7'
];

export const howItWorks = [
  {
    step: '01',
    title: 'Connect Your Data',
    description: 'Plug in your databases and tools you already use—like Excel, Shopify, QuickBooks, or Stripe—with just a few clicks.',
    icon: 'plug'
  },
  {
    step: '02',
    title: 'Clean & Standardize Automatically',
    description: 'Our AI agents instantly clean, unify, and standardize your data across sources—so it all talks to each other.',
    icon: 'sparkles'
  },
  {
    step: '03',
    title: 'Track, Analyze, Act',
    description: 'Get real-time insights, alerts, and automations that help you stay on top of your business and move fast.',
    icon: 'trending-up'
  }
];

// Admin Dashboard Mock Data
export const adminStats = [
  { label: 'Total Users', value: '2,547', change: '+12.5%', trend: 'up' },
  { label: 'Active Subscriptions', value: '1,234', change: '+8.2%', trend: 'up' },
  { label: 'Monthly Revenue', value: '$45,678', change: '+15.3%', trend: 'up' },
  { label: 'Data Sources', value: '8,901', change: '+22.1%', trend: 'up' }
];

export const recentUsers = [
  { id: 1, name: 'John Doe', email: 'john@example.com', plan: 'Business Pro', status: 'active', joined: '2025-01-15' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', plan: 'Business Essential', status: 'active', joined: '2025-01-14' },
  { id: 3, name: 'Mike Johnson', email: 'mike@example.com', plan: 'Hobby', status: 'active', joined: '2025-01-13' },
  { id: 4, name: 'Sarah Williams', email: 'sarah@example.com', plan: 'Business Pro', status: 'inactive', joined: '2025-01-12' },
  { id: 5, name: 'Tom Brown', email: 'tom@example.com', plan: 'Business Essential', status: 'active', joined: '2025-01-11' }
];

export const chartData = {
  userGrowth: [
    { month: 'Jan', users: 1200 },
    { month: 'Feb', users: 1450 },
    { month: 'Mar', users: 1680 },
    { month: 'Apr', users: 1920 },
    { month: 'May', users: 2150 },
    { month: 'Jun', users: 2390 },
    { month: 'Jul', users: 2547 }
  ],
  revenue: [
    { month: 'Jan', amount: 28000 },
    { month: 'Feb', amount: 32000 },
    { month: 'Mar', amount: 35500 },
    { month: 'Apr', amount: 38900 },
    { month: 'May', amount: 42300 },
    { month: 'Jun', amount: 44100 },
    { month: 'Jul', amount: 45678 }
  ],
  planDistribution: [
    { plan: 'Hobby', count: 456 },
    { plan: 'Business Essential', count: 523 },
    { plan: 'Business Pro', count: 189 },
    { plan: 'Ultra', count: 66 }
  ]
};

// Connected Data Sources Analytics
export const connectedSources = [
  {
    id: 1,
    name: 'AI Visibility',
    icon: 'brain',
    color: '#8B5CF6',
    status: 'connected',
    lastSync: '2 hours ago',
    metrics: {
      aiSearchAppearances: 1247,
      searchRankings: 'Top 3 in 45 queries',
      llmMentions: 342,
      brandVisibility: '89%',
      competitorGap: '+23%'
    }
  },
  {
    id: 2,
    name: 'Meta Ads',
    icon: 'facebook',
    color: '#1877F2',
    status: 'connected',
    lastSync: '1 hour ago',
    metrics: {
      impressions: 45230,
      clicks: 1234,
      conversions: 89,
      ctr: '2.73%',
      spend: '₹12,450'
    }
  },
  {
    id: 3,
    name: 'Google Ads',
    icon: 'megaphone',
    color: '#4285F4',
    status: 'connected',
    lastSync: '30 mins ago',
    metrics: {
      impressions: 67890,
      clicks: 2341,
      conversions: 156,
      ctr: '3.45%',
      spend: '₹23,780'
    }
  },
  {
    id: 4,
    name: 'Google Analytics',
    icon: 'bar-chart',
    color: '#E37400',
    status: 'connected',
    lastSync: '5 mins ago',
    metrics: {
      sessions: 12456,
      users: 8934,
      pageviews: 34567,
      bounceRate: '42.3%',
      avgDuration: '3m 24s'
    }
  },
  {
    id: 5,
    name: 'Zoho Books',
    icon: 'book-open',
    color: '#E42527',
    status: 'connected',
    lastSync: '4 hours ago',
    metrics: {
      revenue: '₹4,56,789',
      invoices: 234,
      paid: 198,
      pending: 36,
      overdueAmount: '₹45,600'
    }
  }
];

// AI Visibility Insights
export const aiVisibilityInsights = [
  {
    platform: 'ChatGPT',
    appearances: 523,
    ranking: 'Top 3',
    trend: 'up'
  },
  {
    platform: 'Google Gemini',
    appearances: 412,
    ranking: 'Top 5',
    trend: 'up'
  },
  {
    platform: 'Claude',
    appearances: 234,
    ranking: 'Top 10',
    trend: 'neutral'
  },
  {
    platform: 'Perplexity',
    appearances: 78,
    ranking: 'Not in Top 10',
    trend: 'down'
  }
];
