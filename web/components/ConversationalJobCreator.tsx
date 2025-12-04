'use client';

import { useState, useRef, useEffect } from 'react';
import { useApp } from '@/context/AppContext';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import ImageUpload from '@/components/ImageUpload';
import LocationPicker from '@/components/LocationPicker';
import { apiClient } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ExtractedData {
  task: string | null;
  task_description: string | null;
  location: string | null;
  price_amount: number | null;
  price_currency: string | null;
  has_image: boolean;
}

export default function ConversationalJobCreator() {
  const { state, setJobLocation, addUploadedImage, removeUploadedImage, clearUploadedImages } = useApp();
  
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hi! 👋 I\'m here to help you create a job posting. What task do you need help with?',
      timestamp: new Date()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [extractedData, setExtractedData] = useState<ExtractedData>({
    task: null,
    task_description: null,
    location: null,
    price_amount: null,
    price_currency: null,
    has_image: false
  });
  const [isComplete, setIsComplete] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (userMessage: string) => {
    if (isLoading) return;

    // Add user message to chat with unique ID
    const userMsg: Message = {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Send to backend
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('message', userMessage);
      formData.append('image_uploaded', String(state.clientUploadedImages.length > 0 && !extractedData.has_image));

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/job-creation`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Chat request failed');
      }

      const data = await response.json();

      // Add AI response to chat with unique ID
      const aiMsg: Message = {
        id: `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        role: 'assistant',
        content: data.ai_message,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMsg]);

      // Update extracted data
      if (data.session_state) {
        setExtractedData(data.session_state.extracted_data);
        setIsComplete(data.session_state.is_complete);
        
        // Update location in global state if extracted
        if (data.session_state.extracted_data.location && !state.jobLocation) {
          setJobLocation(data.session_state.extracted_data.location, 0, 0);
        }
      }

    } catch (error) {
      console.error('Chat error:', error);
      const errorMsg: Message = {
        id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        role: 'assistant',
        content: 'Sorry, I had trouble processing that. Could you try again?',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = (file: File, preview: string) => {
    addUploadedImage(file, preview);
    
    // Send notification to backend (handleSendMessage will add the chat message)
    handleSendMessage('[User uploaded reference image]');
  };

  const handleLocationChange = (address: string, lat: number, lng: number) => {
    setJobLocation(address, lat, lng);
    
    // Only notify AI if valid coordinates (user selected from dropdown)
    if (lat !== 0 && lng !== 0) {
      handleSendMessage(`Location is ${address}`);
    }
  };

  const handleCreateJob = async () => {
    if (!isComplete || !state.walletAddress) {
      alert('Please complete all fields and connect your wallet');
      return;
    }

    setIsCreating(true);

    try {
      // Upload images to IPFS
      const ipfsUrls = await Promise.all(
        state.clientUploadedImages.map(async (img) => {
          return await apiClient.uploadToIpfs(img.file);
        })
      );

      // Create job
      const payload = {
        client_address: state.walletAddress,
        description: extractedData.task_description || extractedData.task || '',
        reference_photos: ipfsUrls,
        location: extractedData.location || state.jobLocation,
        latitude: state.jobLatitude,
        longitude: state.jobLongitude,
        amount: extractedData.price_amount || 5.0,
        verification_plan: {
          task_category: extractedData.task || 'general',
          verification_checklist: [],
          quality_indicators: []
        },
      };

      const result = await apiClient.createJob(payload);

      if (result.job) {
        alert(`Job created successfully! ID: ${result.job.job_id}`);
        
        // Clear session
        await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/session/${sessionId}`, {
          method: 'DELETE'
        });
        
        // Reset
        clearUploadedImages();
        setMessages([{
          id: '1',
          role: 'assistant',
          content: 'Great! Your job is posted. Need to create another one?',
          timestamp: new Date()
        }]);
        setExtractedData({
          task: null,
          task_description: null,
          location: null,
          price_amount: null,
          price_currency: null,
          has_image: false
        });
        setIsComplete(false);
      }
    } catch (error) {
      console.error('Create error:', error);
      alert('Failed to create job');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="animate-in fade-in duration-500 h-full flex flex-col">
      <div className="mb-4">
        <h2 className="text-3xl font-bold text-white mb-2">Create Job (AI Assistant)</h2>
        <p className="text-slate-400">
          Chat with our AI to create your blockchain-secured gig posting.
        </p>
      </div>

      <div className="flex-1 bg-slate-950/50 rounded-3xl border border-slate-800 flex flex-col overflow-hidden">
        {/* Chat Messages */}
        <div 
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto p-6 space-y-4"
        >
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              role={msg.role}
              content={msg.content}
              timestamp={msg.timestamp}
            />
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 rounded-2xl px-4 py-3 border border-slate-700">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Progress Indicators */}
        {(extractedData.task || extractedData.location || extractedData.price_amount) && (
          <div className="px-6 py-4 bg-slate-900/50 border-t border-slate-800">
            <div className="text-xs font-semibold text-slate-400 mb-2">Collected Info:</div>
            <div className="flex flex-wrap gap-2">
              {extractedData.task && (
                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30">
                  ✓ Task: {extractedData.task}
                </span>
              )}
              {extractedData.location && (
                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30">
                  ✓ Location: {extractedData.location}
                </span>
              )}
              {extractedData.price_amount && (
                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30">
                  ✓ Price: {extractedData.price_amount} {extractedData.price_currency || 'GAS'}
                </span>
              )}
              {state.clientUploadedImages.length > 0 && (
                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30">
                  ✓ Image uploaded
                </span>
              )}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        {!isComplete && (
          <div className="px-6 py-3 bg-slate-900/30 border-t border-slate-800">
            <div className="flex gap-2">
              <ImageUpload
                images={state.clientUploadedImages}
                onAdd={handleImageUpload}
                onRemove={removeUploadedImage}
              />
              
              <LocationPicker
                value={state.jobLocation}
                onChange={handleLocationChange}
              />
            </div>
          </div>
        )}

        {/* Create Button */}
        {isComplete && (
          <div className="px-6 py-4 bg-gradient-to-r from-green-500/10 to-cyan-500/10 border-t border-green-500/30">
            <button
              onClick={handleCreateJob}
              disabled={isCreating}
              className="w-full bg-gradient-to-r from-green-500 to-cyan-600 text-white font-semibold py-3 px-6 rounded-xl hover:shadow-lg hover:shadow-green-500/20 transition-all active:scale-95 disabled:opacity-50"
            >
              {isCreating ? 'Creating Job...' : '✓ Create Job on Blockchain'}
            </button>
          </div>
        )}

        {/* Chat Input */}
        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading}
          placeholder={isComplete ? "Need to change something?" : "Type your answer..."}
        />
      </div>
    </div>
  );
}
