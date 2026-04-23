import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { ArrowLeft, Send, Brain, X, Upload, FileSpreadsheet, Loader2, CheckCircle, Database, Download, Trash2, Plus, BarChart, MessageCircle, User, Sparkles, ChevronDown } from 'lucide-react';
import { dataSourceAPI } from '../services/api';
import api from '../services/api';
import { toast } from '../hooks/use-toast';
import { integrations } from '../mock/mockData';
import { exportFilesToExcel } from '../utils/reportExport';
import DOMPurify from 'dompurify';

const WorkspaceView = ({ workspace, onBack, user }) => {
  const [files, setFiles] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showIntegrations, setShowIntegrations] = useState(false);
  const [fileDetails, setFileDetails] = useState(null);
  const [showFileDetails, setShowFileDetails] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const chatEndRef = useRef(null);
  const chatInputRef = useRef(null);

  const fetchFiles = useCallback(async () => {
    try {
      const data = await dataSourceAPI.getUploadedFiles(workspace.id);
      setFiles(data.files || []);
    } catch { }
  }, [workspace.id]);

  // Load chat history
  const loadChatHistory = useCallback(async () => {
    try {
      const res = await api.get(`/ai/chat/history/${workspace.id}`);
      if (res.data.history?.length > 0) {
        setChatMessages(res.data.history.map(message => ({
          ...message,
          content: DOMPurify.sanitize(message.content)
        })));
      }
    } catch { }
  }, [workspace.id]);

  useEffect(() => { fetchFiles(); loadChatHistory(); }, [fetchFiles, loadChatHistory]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (!chatInput.trim() || isSending) return;
    const userMsg = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, { 
      role: 'user', 
      content: DOMPurify.sanitize(userMsg), 
      timestamp: new Date().toISOString() 
    }]);
    setIsSending(true);

    try {
      const res = await api.post('/ai/chat', {
        query: userMsg,
        workspace_id: workspace.id,
        session_id: sessionId
      });
      if (res.data.session_id) setSessionId(res.data.session_id);
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: DOMPurify.sanitize(res.data.answer),
        sources: res.data.sources,
        timestamp: new Date().toISOString()
      }]);
    } catch (error) {
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: DOMPurify.sanitize(error.message),
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    // your JSX code here
  );
};

export default WorkspaceView;