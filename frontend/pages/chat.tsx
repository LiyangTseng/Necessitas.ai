import { useState, useRef, useEffect, useCallback } from 'react';
import Head from 'next/head';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { useRouter } from 'next/router';
import ReactMarkdown from 'react-markdown';
import {
  Send,
  Bot,
  User,
  Upload,
  FileText,
  ArrowLeft,
  Loader2,
  CheckCircle,
  X,
  Briefcase,
  TrendingUp,
  Target,
  MapPin
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showResumeUpload, setShowResumeUpload] = useState(true);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadedFile(file);
    setIsUploading(true);

    try {
      console.log('Uploading resume:', file.name);

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/resume/parse/file', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const results = await response.json();
        console.log('Resume analysis results:', results);

        // Add welcome message after successful upload
        const welcomeMessage: Message = {
          id: Date.now().toString(),
          type: 'bot',
          content: `Great! I've analyzed your resume for ${results.data?.personal_info?.full_name || 'you'}. I found ${results.data?.skills?.length || 0} skills and ${results.data?.experience?.length || 0} work experiences. How can I help you with your career today?`,
          timestamp: new Date()
        };

        setMessages([welcomeMessage]);
        setShowResumeUpload(false);
        toast.success('Resume analyzed successfully!');
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to analyze resume. Please try again.');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    multiple: false
  });

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      // Call backend chat endpoint
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentInput,
          conversation_history: messages.map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.content
          }))
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          content: data.response || "I'm here to help with your career questions. How can I assist you?",
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      toast.error('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleGoHome = () => {
    if (messages.length > 0 || uploadedFile) {
      const confirmed = window.confirm(
        'Are you sure you want to go back to the homepage? Your chat history and uploaded resume will be lost.'
      );
      if (confirmed) {
        router.push('/');
      }
    } else {
      router.push('/');
    }
  };

  const quickActions = [
    {
      icon: <Upload className="w-4 h-4" />,
      text: "Resume Re-upload",
      action: () => {
        setShowResumeUpload(true);
        setUploadedFile(null);
        setMessages([]);
      }
    },
    {
      icon: <Target className="w-4 h-4" />,
      text: "Job Recommendations",
      action: () => {
        setInputValue("Can you help me find job recommendations based on my skills?");
        handleSendMessage();
      }
    },
    {
      icon: <FileText className="w-4 h-4" />,
      text: "Resume Advice",
      action: () => {
        setInputValue("Can you give me advice on how to improve my resume?");
        handleSendMessage();
      }
    },
    {
      icon: <MapPin className="w-4 h-4" />,
      text: "Career Roadmap",
      action: () => {
        setInputValue("Can you suggest a career roadmap for my professional development?");
        handleSendMessage();
      }
    }
  ];

  return (
    <>
      <Head>
        <title>Necessitas.ai - AI Powered Career consulting</title>
        <meta name="description" content="Chat with your AI career assistant" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between py-4">
              <button
                onClick={handleGoHome}
                className="flex items-center text-gray-900 hover:text-indigo-600 transition-colors group"
              >
                <Briefcase className="w-8 h-8 text-indigo-600 group-hover:text-indigo-700" />
                <span className="ml-2 text-xl font-bold group-hover:text-indigo-600">Necessitas.ai</span>
              </button>
              <button
                onClick={handleGoHome}
                className="flex items-center text-gray-600 hover:text-indigo-600 transition-colors"
              >
                <ArrowLeft className="w-4 h-4 mr-1" />
                Back to Home
              </button>
            </div>
          </div>
        </header>

        {/* Chat Interface */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-xl shadow-lg h-[600px] flex flex-col">
            {/* Resume Upload Section */}
            {showResumeUpload && (
              <div className="flex-1 flex flex-col items-center justify-center p-8">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center mb-8"
                >
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Let's Start with Your Resume</h2>
                  <p className="text-gray-600">Upload your resume to get personalized career guidance</p>
                </motion.div>

                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors w-full max-w-md ${
                    isDragActive
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-300 hover:border-indigo-400'
                  }`}
                >
                  <input {...getInputProps()} />

                  {isUploading ? (
                    <div className="flex flex-col items-center">
                      <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
                      <p className="text-lg text-gray-600">Analyzing your resume...</p>
                    </div>
                  ) : uploadedFile ? (
                    <div className="flex flex-col items-center">
                      <CheckCircle className="w-12 h-12 text-green-600 mb-4" />
                      <p className="text-lg text-gray-900 mb-2">{uploadedFile.name}</p>
                      <p className="text-gray-600">File uploaded successfully</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center">
                      <Upload className="w-12 h-12 text-indigo-600 mb-4" />
                      <p className="text-lg text-gray-900 mb-2">
                        {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume here'}
                      </p>
                      <p className="text-gray-600 mb-4">or click to browse</p>
                      <p className="text-sm text-gray-500">
                        Supports PDF, DOCX, and TXT files (max 10MB)
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Messages */}
            {!showResumeUpload && (
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex items-start space-x-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.type === 'user'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {message.type === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                      </div>
                      <div className={`px-4 py-3 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        <div className="text-sm prose prose-sm max-w-none">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>
                        <p className={`text-xs mt-1 ${
                          message.type === 'user' ? 'text-indigo-100' : 'text-gray-500'
                        }`}>
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Loading indicator */}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div className="bg-gray-100 px-4 py-3 rounded-lg">
                      <div className="flex items-center space-x-1">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm text-gray-600">AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

                {/* Quick Actions */}
                <div className="px-6 pb-4">
                  <p className="text-sm text-gray-600 mb-3">Quick actions:</p>
                  <div className="flex flex-wrap gap-2">
                    {quickActions.map((action, index) => (
                      <button
                        key={index}
                        onClick={action.action}
                        className="flex items-center space-x-2 px-3 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition-colors text-sm"
                      >
                        {action.icon}
                        <span>{action.text}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div ref={messagesEndRef} />
              </div>
            )}

            {/* Input */}
            {!showResumeUpload && (
              <div className="border-t p-4">
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything about your career..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    disabled={isLoading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim() || isLoading}
                    className="px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="flex items-center justify-center mb-4">
                <Briefcase className="w-8 h-8 text-indigo-400" />
                <span className="ml-2 text-2xl font-bold">necessitas.ai</span>
              </div>
              <p className="text-gray-400 mb-4">
                Powered by AWS Bedrock AgentCore • Built for AWS AI Agent Global Hackathon 2025
              </p>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
