// Mock data for Analiyx clone

export const testimonials = [
  {
    id: 1,
    quote: "Analiyx AI has significantly reduced the time it takes to go from a question to an insight.",
    description: "What truly differentiates the platform is its natural language interface, which allows users to simply ask questions in plain English and have Analiyx AI automatically interpret the intent, generate the correct queries, and present the results in meaningful ways. We can not only explore data but also create, refine, and edit interactive dashboard widgets effortlessly—without writing SQL, scripts, or manual configurations.",
    name: "Stephen O.",
    role: "CTO at VDL Fulfilment",
    avatar: "SO"
  },
  {
    id: 2,
    quote: "It transformed our day-to-day decision-making from 'reactive guessing' to 'proactive knowing.'",
    description: "In logistics, data gets messy fast. We have shipping logs, carrier invoices, and tracking updates all living in different raw formats. Before Analiyx, my operations team waited days for analysts to clean that data and build a dashboard just to answer a simple question. Analiyx let us skip the 'cleaning' phase entirely. We connected our raw data sources, and now my team asks questions in plain English and gets diagnostic answers instantly.",
    name: "Amadou D.",
    role: "CEO/CTO at B-HiTech",
    avatar: "AD"
  }
];

export const integrations = [
  { name: 'PostgreSQL', icon: 'database', color: '#336791' },
  { name: 'MySQL', icon: 'database', color: '#4479A1' },
  { name: 'MongoDB', icon: 'database', color: '#47A248' },
  { name: 'Supabase', icon: 'zap', color: '#3ECF8E' },
  { name: 'Google Sheets', icon: 'sheet', color: '#0F9D58' },
  { name: 'Excel', icon: 'file-spreadsheet', color: '#217346' },
  { name: 'CSV', icon: 'file-text', color: '#6B7280' },
  { name: 'Stripe', icon: 'credit-card', color: '#635BFF' },
  { name: 'Shopify', icon: 'shopping-bag', color: '#96BF48' },
  { name: 'QuickBooks', icon: 'book', color: '#2CA01C' },
  { name: 'Google Analytics', icon: 'bar-chart', color: '#E37400' },
  { name: 'Shopline', icon: 'store', color: '#FF6B6B' },
  { name: 'Square', icon: 'square', color: '#000000' },
  { name: 'HubSpot', icon: 'users', color: '#FF7A59' }
];

export const pricingPlans = [
  {
    id: 1,
    name: 'Hobby',
    description: 'Entry level plan to get you started.',
    price: 19,
    period: 'month',
    features: [
      'Add teammates to workspaces',
      'Limited to 2 workspaces',
      'No daily requests cap',
      '100 credits monthly'
    ],
    highlighted: false
  },
  {
    id: 2,
    name: 'Business Essential',
    description: 'Our recommended Plan for small businesses.',
    price: 50,
    period: 'month',
    features: [
      'Create up to 5 workspaces',
      'No daily requests cap',
      '500 credits monthly',
      'Add teammates to workspaces',
      'Extra usage based spending',
      'Includes Up to 3 seats/users'
    ],
    highlighted: true
  },
  {
    id: 3,
    name: 'Business Pro',
    description: 'Our recommended Plan for medium and large businesses.',
    price: 299,
    period: 'month',
    features: [
      'Unlimited workspaces',
      'No daily requests cap',
      '1000 credits monthly',
      'Add teammates to workspaces',
      'Extra usage based spending',
      'Includes up to 5 seats/users',
      'Embed Papermap in your app'
    ],
    highlighted: false
  },
  {
    id: 4,
    name: 'Ultra',
    description: 'Ship client-facing analytics fast without building a BI stack.',
    price: 'Custom',
    period: '',
    features: [
      'Everything in Business Pro for internal use',
      'White-label Papermap on your platform with full multi-tenant support',
      'Unlimited usage with postpaid, usage-based invoicing',
      'Dedicated development support'
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