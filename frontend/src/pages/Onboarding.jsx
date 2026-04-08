import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Send, Building2, User, Heart, Monitor, ShoppingCart, Factory, Circle, BarChart3, Globe } from 'lucide-react';
import api from '../services/api';

const STEPS = [
  { id: 'welcome', type: 'message' },
  { id: 'usage_type', type: 'chips', question: 'How do you plan to use Analiyx?', options: [
    { label: 'Personal', value: 'personal', icon: User },
    { label: 'Business', value: 'business', icon: Building2 },
  ]},
  { id: 'company_name', type: 'text', question: 'What is your company name?' },
  { id: 'company_location', type: 'text', question: 'Where is your company based?' },
  { id: 'company_description', type: 'text', question: 'Tell me a little more about what your company does? E.g. We provide SaaS analytics tools' },
  { id: 'industry', type: 'chips', question: 'What industry is your company in?', options: [
    { label: 'Financial Services', value: 'Financial Services', icon: Building2 },
    { label: 'Healthcare', value: 'Healthcare', icon: Heart },
    { label: 'Technology', value: 'Technology', icon: Monitor },
    { label: 'Retail/Ecommerce', value: 'Retail/Ecommerce', icon: ShoppingCart },
    { label: 'Manufacturing', value: 'Manufacturing', icon: Factory },
    { label: 'Other', value: 'Other', icon: Circle },
  ]},
  { id: 'monthly_mrr', type: 'text', question: 'What is your monthly tentative MRR (Monthly Recurring Revenue)?' },
  { id: 'has_data_analyst', type: 'chips', question: 'Do you have a hired Data Analyst?', options: [
    { label: 'Yes', value: 'Yes' },
    { label: 'No', value: 'No' },
    { label: 'Planning to hire', value: 'Planning to hire' },
  ]},
  { id: 'does_digital_marketing', type: 'chips', question: 'Are you doing any Digital Marketing activity?', options: [
    { label: 'Yes', value: 'Yes' },
    { label: 'No', value: 'No' },
    { label: 'Planning to start', value: 'Planning to start' },
  ]},
  { id: 'data_preference', type: 'chips', question: 'One last question — would you like to connect your data now or start exploring with sample data?', options: [
    { label: 'Connect Data', value: 'connect', icon: BarChart3 },
    { label: 'Start Exploring with Sample Data', value: 'synthetic', icon: Globe },
  ]},
];

const TypingIndicator = () => (
  <div className="flex items-start gap-3">
    <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0">
      <Sparkles className="w-4 h-4 text-white" />
    </div>
    <div className="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-sm px-4 py-3">
      <div className="flex gap-1.5">
        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  </div>
);

const BotMessage = ({ children }) => (
  <div className="flex items-start gap-3 animate-fadeIn">
    <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0">
      <Sparkles className="w-4 h-4 text-white" />
    </div>
    <div className="max-w-[75%]">
      <div className="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-sm px-4 py-3">
        <p className="text-gray-200 text-sm leading-relaxed">{children}</p>
      </div>
      <p className="text-gray-600 text-[10px] mt-1 ml-1">Analiyx AI</p>
    </div>
  </div>
);

const UserMessage = ({ children }) => (
  <div className="flex justify-end animate-fadeIn">
    <div className="flex items-start gap-2">
      <div className="bg-purple-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-[75%]">
        <p className="text-sm">{children}</p>
      </div>
      <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
        <User className="w-4 h-4 text-gray-300" />
      </div>
    </div>
  </div>
);

const ChipOptions = ({ options, onSelect, selected }) => (
  <div className="flex flex-wrap gap-2 ml-11 animate-fadeIn">
    {options.map(opt => {
      const Icon = opt.icon;
      const isSelected = selected === opt.value;
      return (
        <button
          key={opt.value}
          onClick={() => onSelect(opt.value, opt.label)}
          disabled={!!selected}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-full border text-sm transition-all ${
            isSelected
              ? 'bg-purple-600/20 border-purple-500 text-purple-300'
              : selected
                ? 'bg-gray-800/50 border-gray-700/50 text-gray-600 cursor-not-allowed'
                : 'bg-gray-800 border-gray-700 text-gray-300 hover:border-purple-500/50 hover:bg-gray-700 cursor-pointer'
          }`}
          data-testid={`onboarding-chip-${opt.value}`}
        >
          {Icon && <Icon className="w-4 h-4" />}
          {opt.label}
          {isSelected && <span className="text-green-400 ml-1">&#10003;</span>}
        </button>
      );
    })}
  </div>
);

const Onboarding = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [textInput, setTextInput] = useState('');
  const [isTyping, setIsTyping] = useState(true);
  const [userName, setUserName] = useState('');
  const [saving, setSaving] = useState(false);
  const chatEndRef = useRef(null);

  const advancedSteps = useRef(new Set());

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { navigate('/login'); return; }

    const checkOnboarding = async () => {
      try {
        const res = await api.get('/onboarding/status');
        if (res.data.completed) {
          navigate('/dashboard');
          return;
        }
        setUserName(res.data.name || 'there');
        // Show welcome message after short delay
        setTimeout(() => {
          setIsTyping(false);
          setMessages([{ type: 'bot', content: `Hi ${res.data.name || 'there'}, glad to have you here!\n\nI'm Analiyx AI and I will help you turn your data into easy to understand insights and actions. First, I want to learn more about you to be more useful.` }]);
          // Move to first question after another delay
          setTimeout(() => advanceToStep(1), 1200);
        }, 1500);
      } catch {
        navigate('/login');
      }
    };
    checkOnboarding();
  }, [navigate]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const advanceToStep = (stepIndex) => {
    if (stepIndex >= STEPS.length) return;
    if (advancedSteps.current.has(stepIndex)) return;
    advancedSteps.current.add(stepIndex);
    const step = STEPS[stepIndex];
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setMessages(prev => [...prev, { type: 'bot', content: step.question, stepIndex }]);
      setCurrentStep(stepIndex);
    }, 800);
  };

  const handleChipSelect = async (value, label) => {
    const step = STEPS[currentStep];
    setAnswers(prev => ({ ...prev, [step.id]: value }));
    setMessages(prev => [...prev, { type: 'user', content: label }]);

    // If this is the last step, save and redirect
    if (step.id === 'data_preference') {
      await saveOnboarding({ ...answers, [step.id]: value });
      return;
    }

    // Skip company questions for personal usage
    if (step.id === 'usage_type' && value === 'personal') {
      setAnswers(prev => ({
        ...prev,
        company_name: 'N/A',
        company_location: 'N/A',
        company_description: 'N/A',
        industry: 'N/A',
      }));
      // Jump to MRR question (step 6)
      advanceToStep(6);
    } else {
      advanceToStep(currentStep + 1);
    }
  };

  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (!textInput.trim()) return;

    const step = STEPS[currentStep];
    const value = textInput.trim();
    setAnswers(prev => ({ ...prev, [step.id]: value }));
    setMessages(prev => [...prev, { type: 'user', content: value }]);
    setTextInput('');
    advanceToStep(currentStep + 1);
  };

  const saveOnboarding = async (finalAnswers) => {
    setSaving(true);
    setIsTyping(true);
    try {
      await api.post('/onboarding/save', finalAnswers);
      setTimeout(() => {
        setIsTyping(false);
        setMessages(prev => [...prev, { type: 'bot', content: "You're all set! Let me take you to your dashboard now..." }]);
        setTimeout(() => {
          if (finalAnswers.data_preference === 'connect') {
            navigate('/dashboard?tab=sources');
          } else {
            navigate('/dashboard');
          }
        }, 1500);
      }, 1000);
    } catch {
      setIsTyping(false);
      setMessages(prev => [...prev, { type: 'bot', content: "Something went wrong saving your preferences. Don't worry, you can update them later in Settings." }]);
      setTimeout(() => navigate('/dashboard'), 2000);
    } finally {
      setSaving(false);
    }
  };

  const currentStepData = STEPS[currentStep];
  const isChipStep = currentStepData?.type === 'chips';
  const isTextStep = currentStepData?.type === 'text';
  const stepAnswered = answers[currentStepData?.id] !== undefined;

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col" data-testid="onboarding-page">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-3">
          <img src="/analiyx-logo.jpg" alt="Analiyx" className="h-9 object-contain" />
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
          {messages.map((msg, i) => (
            <div key={i}>
              {msg.type === 'bot' ? (
                <BotMessage>{msg.content}</BotMessage>
              ) : (
                <UserMessage>{msg.content}</UserMessage>
              )}
              {/* Show chips right after their bot question */}
              {msg.type === 'bot' && msg.stepIndex !== undefined && STEPS[msg.stepIndex]?.type === 'chips' && (
                <div className="mt-3">
                  <ChipOptions
                    options={STEPS[msg.stepIndex].options}
                    onSelect={handleChipSelect}
                    selected={answers[STEPS[msg.stepIndex].id]}
                  />
                </div>
              )}
            </div>
          ))}
          {isTyping && <TypingIndicator />}
          <div ref={chatEndRef} />
        </div>
      </main>

      {/* Text Input (only for text steps) */}
      {isTextStep && !stepAnswered && !isTyping && (
        <div className="border-t border-gray-800 bg-gray-950/90 backdrop-blur-sm sticky bottom-0">
          <form onSubmit={handleTextSubmit} className="max-w-3xl mx-auto px-6 py-4 flex gap-3">
            <input
              type="text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Type your answer..."
              autoFocus
              className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white text-sm placeholder-gray-500 outline-none focus:border-purple-500 transition-colors"
              data-testid="onboarding-text-input"
            />
            <button
              type="submit"
              disabled={!textInput.trim()}
              className="bg-purple-600 hover:bg-purple-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-xl px-4 py-3 transition-colors"
              data-testid="onboarding-send-btn"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn { animation: fadeIn 0.4s ease-out; }
      `}</style>
    </div>
  );
};

export default Onboarding;
