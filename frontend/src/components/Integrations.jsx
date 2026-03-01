import React from 'react';
import { integrations } from '../mock/mockData';
import { Button } from './ui/button';
import { useNavigate } from 'react-router-dom';
import { Database, Zap, Sheet, FileSpreadsheet, FileText, CreditCard, ShoppingBag, Book, BarChart, Store, Square, Users } from 'lucide-react';

const iconMap = {
  database: Database,
  zap: Zap,
  sheet: Sheet,
  'file-spreadsheet': FileSpreadsheet,
  'file-text': FileText,
  'credit-card': CreditCard,
  'shopping-bag': ShoppingBag,
  book: Book,
  'bar-chart': BarChart,
  store: Store,
  square: Square,
  users: Users
};

const Integrations = () => {
  const navigate = useNavigate();

  return (
    <section id="integrations" className="py-20 bg-gradient-to-b from-gray-900 to-gray-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <p className="text-purple-400 text-sm font-semibold uppercase tracking-wider mb-2">Integrations</p>
          <h2 className="text-4xl font-bold text-white mb-4">Connect any data stack</h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-8">
            Connect Analiyx directly to your data stack or warehouse to build dashboards and query your data in minutes.
          </p>
          <Button 
            size="lg"
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
            onClick={() => navigate('/signup')}
          >
            Connect your data source
          </Button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-6 mt-12">
          {integrations.map((integration, index) => {
            const Icon = iconMap[integration.icon];
            return (
              <div
                key={index}
                className="group relative bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-purple-500/50 transition-all duration-300 transform hover:scale-110 hover:shadow-xl hover:shadow-purple-500/20 cursor-pointer"
              >
                <div className="flex flex-col items-center space-y-3">
                  <div 
                    className="w-12 h-12 rounded-lg flex items-center justify-center transition-colors duration-200"
                    style={{ backgroundColor: `${integration.color}20` }}
                  >
                    <Icon className="w-6 h-6" style={{ color: integration.color }} />
                  </div>
                  <span className="text-xs text-gray-400 text-center group-hover:text-white transition-colors duration-200">
                    {integration.name}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Integrations;