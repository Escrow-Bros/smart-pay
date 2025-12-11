'use client';

import { useState, useRef, useEffect } from 'react';
import { useApp } from '@/context/AppContext';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import ImageUpload from '@/components/ImageUpload';
import LocationPicker from '@/components/LocationPicker';
import { apiClient } from '@/lib/api';
import { usdToGas, formatGasWithUSD } from '@/lib/currency';
import type { UploadedImage } from '@/lib/types';

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

  // Prevent hydration errors by only rendering after mount
  const [mounted, setMounted] = useState(false);

  // Get or create session ID from localStorage
  const [sessionId] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('job_creator_session_id');
      if (stored) {
        console.log('[JobCreator] Restoring session:', stored);
        return stored;
      }
    }
    const newId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    if (typeof window !== 'undefined') {
      localStorage.setItem('job_creator_session_id', newId);
      console.log('[JobCreator] Created new session:', newId);
    }
    return newId;
  });

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'initial-1',
      role: 'assistant',
      content: 'Hi! 👋 I\'m here to help you create a job posting. What task do you need help with?',
      timestamp: new Date(0) // Use epoch for SSR consistency
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRestoring, setIsRestoring] = useState(false); // Only show if actually restoring
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

  // Set mounted state after component mounts on client (prevents hydration errors)
  useEffect(() => {
    setMounted(true);
  }, []);

  // Restore session from backend on mount
  useEffect(() => {
    const restoreSession = async () => {
      // Check if we have a stored session that might need restoration
      const hasStoredSession = typeof window !== 'undefined' && localStorage.getItem('job_creator_session_id');

      if (!hasStoredSession) {
        console.log('[JobCreator] No stored session, skipping restoration');
        return;
      }

      setIsRestoring(true);

      try {
        console.log('[JobCreator] Attempting to restore session:', sessionId);
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/session/${sessionId}`);

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.session && data.session.history && data.session.history.length > 0) {
            console.log('[JobCreator] Session restored:', data.session);

            // Restore messages from history
            const restoredMessages: Message[] = data.session.history.map((msg: any, idx: number) => ({
              id: `restored_${idx}`,
              role: msg.role,
              content: msg.content,
              timestamp: new Date(msg.timestamp || 0)
            }));
            setMessages(restoredMessages);
            console.log('[JobCreator] Restored', restoredMessages.length, 'messages');

            // Restore extracted data
            if (data.session.extracted_data) {
              setExtractedData(data.session.extracted_data);
            }

            // Restore completion state
            if (data.session.is_complete !== undefined) {
              setIsComplete(data.session.is_complete);
            }
          } else {
            console.log('[JobCreator] Session exists but has no messages, showing default greeting');
          }
        } else if (response.status === 404) {
          console.log('[JobCreator] No existing session found on server, starting fresh');
        }
      } catch (error) {
        console.error('[JobCreator] Failed to restore session:', error);
      } finally {
        setIsRestoring(false);
      }
    };

    restoreSession();
  }, [sessionId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (userMessage: string, forceImageUploaded: boolean = false) => {
    if (isLoading) return;

    // Use current message count for stable IDs on client
    const msgCount = messages.length;

    // Add user message to chat with stable ID
    const userMsg: Message = {
      id: `user_${msgCount}`,
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
      // Use forceImageUploaded flag if provided, otherwise check state
      const imageUploaded = forceImageUploaded || (state.clientUploadedImages.length > 0 && !extractedData.has_image);
      formData.append('image_uploaded', String(imageUploaded));
      console.log('[JobCreator] Sending image_uploaded:', imageUploaded);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/job-creation`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Chat request failed');
      }

      const data = await response.json();

      // Add AI response to chat with stable ID
      const aiMsg: Message = {
        id: `ai_${msgCount + 1}`,
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
        id: `error_${msgCount + 1}`,
        role: 'assistant',
        content: 'Sorry, I had trouble processing that. Could you try again?',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = (image: UploadedImage) => {
    console.log('[JobCreator] handleImageUpload called with:', image.file.name, 'Size:', (image.file.size / (1024 * 1024)).toFixed(2), 'MB');
    console.log('[JobCreator] Current images count before add:', state.clientUploadedImages.length);
    addUploadedImage(image);
    console.log('[JobCreator] addUploadedImage called, new count should be:', state.clientUploadedImages.length + 1);

    // Update extracted data immediately to reflect image upload
    setExtractedData(prev => ({ ...prev, has_image: true }));

    // Send notification to backend (handleSendMessage will add the chat message)
    console.log('[JobCreator] Sending notification to backend about uploaded image');
    handleSendMessage('[User uploaded reference image]', true); // Pass true to indicate image was just uploaded
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
      // Convert USD to GAS if needed
      let paymentAmount = extractedData.price_amount || 5.0;

      if (extractedData.price_currency?.toUpperCase() === 'USD') {
        // Convert USD to GAS
        paymentAmount = usdToGas(paymentAmount);
        console.log(`Converting ${extractedData.price_amount} USD to ${paymentAmount.toFixed(2)} GAS`);
      }

      // Upload images to IPFS
      console.log('[JobCreator] Starting IPFS upload for', state.clientUploadedImages.length, 'images');
      state.clientUploadedImages.forEach((img, idx) => {
        console.log(`[JobCreator] Image ${idx + 1}:`, img.file.name, 'Size:', (img.file.size / (1024 * 1024)).toFixed(2), 'MB');
      });

      const ipfsUrls = await Promise.all(
        state.clientUploadedImages.map(async (img, idx) => {
          console.log(`[JobCreator] Uploading image ${idx + 1}/${state.clientUploadedImages.length} to IPFS:`, img.file.name);
          try {
            const url = await apiClient.uploadToIpfs(img.file);
            console.log(`[JobCreator] ✅ Image ${idx + 1} uploaded successfully:`, url);
            return url;
          } catch (error) {
            console.error(`[JobCreator] ❌ Failed to upload image ${idx + 1}:`, error);
            throw error;
          }
        })
      );
      console.log('[JobCreator] All IPFS uploads complete:', ipfsUrls);

      // Create job
      const payload = {
        client_address: state.walletAddress,
        description: extractedData.task_description || extractedData.task || '',
        reference_photos: ipfsUrls,
        location: extractedData.location || state.jobLocation,
        latitude: state.jobLatitude,
        longitude: state.jobLongitude,
        amount: paymentAmount, // Always in GAS
        verification_plan: {
          task_category: extractedData.task || 'general',
          verification_checklist: [],
          quality_indicators: []
        },
      };

      const result = await apiClient.createJob(payload);

      if (result.job) {
        const originalAmount = extractedData.price_amount || paymentAmount;
        const currency = extractedData.price_currency?.toUpperCase() || 'GAS';
        const displayAmount = currency === 'USD'
          ? `${originalAmount} USD (~${paymentAmount.toFixed(2)} GAS)`
          : `${paymentAmount.toFixed(2)} GAS`;

        alert(`Job created successfully! ID: ${result.job.job_id}\nPayment: ${displayAmount}`);

        // Clear session
        await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/session/${sessionId}`, {
          method: 'DELETE'
        });

        // Clear localStorage session
        if (typeof window !== 'undefined') {
          localStorage.removeItem('job_creator_session_id');
          console.log('[JobCreator] Session cleared from localStorage');
        }

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
      {/* Header Section */}
      <div className="mb-3 sm:mb-4 px-1">
        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-1 sm:mb-2">
          Create Job (AI Assistant)
        </h2>
        <p className="text-sm sm:text-base text-slate-400">
          Chat with our AI to create your blockchain-secured gig posting.
        </p>
      </div>

      <div className="flex-1 bg-slate-950/50 rounded-2xl sm:rounded-3xl border border-slate-800 flex flex-col overflow-hidden">
        {/* Chat Messages */}
        <div
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6 space-y-3 sm:space-y-4"
        >
          {isRestoring ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="flex gap-1 justify-center mb-3">
                  <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <p className="text-slate-400 text-sm">Restoring conversation...</p>
              </div>
            </div>
          ) : (
            <>
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
            </>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Progress Indicators */}
        {(extractedData.task || extractedData.location || extractedData.price_amount) && (
          <div className="px-3 sm:px-4 md:px-6 py-3 sm:py-4 bg-slate-900/50 border-t border-slate-800">
            <div className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wide">
              Collected Info:
            </div>
            <div className="flex flex-wrap gap-1.5 sm:gap-2">
              {extractedData.task && (
                <span className="px-2.5 sm:px-3 py-1 sm:py-1.5 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30 whitespace-nowrap">
                  ✓ Task: {extractedData.task.length > 20 ? `${extractedData.task.substring(0, 20)}...` : extractedData.task}
                </span>
              )}
              {extractedData.location && (
                <span className="px-2.5 sm:px-3 py-1 sm:py-1.5 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30 whitespace-nowrap">
                  ✓ Location: {extractedData.location.length > 20 ? `${extractedData.location.substring(0, 20)}...` : extractedData.location}
                </span>
              )}
              {extractedData.price_amount && (
                <span className="px-2.5 sm:px-3 py-1 sm:py-1.5 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30 whitespace-nowrap">
                  ✓ Price: {extractedData.price_amount} {extractedData.price_currency || 'GAS'}
                  {extractedData.price_currency?.toUpperCase() === 'USD' &&
                    ` (~${usdToGas(extractedData.price_amount).toFixed(2)} GAS)`}
                  {extractedData.price_currency?.toUpperCase() === 'GAS' &&
                    ` (~${formatGasWithUSD(extractedData.price_amount).usd})`}
                </span>
              )}
              {state.clientUploadedImages.length > 0 && (
                <span className="px-2.5 sm:px-3 py-1 sm:py-1.5 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30 whitespace-nowrap">
                  ✓ Image uploaded
                </span>
              )}
            </div>

            {/* Manual completion trigger if AI hasn't detected it yet */}
            {!isComplete && extractedData.task && extractedData.location && extractedData.price_amount && state.clientUploadedImages.length > 0 && (
              <div className="mt-3">
                <button
                  onClick={() => setIsComplete(true)}
                  className="w-full bg-gradient-to-r from-green-500 to-cyan-600 text-white font-semibold py-2.5 px-4 rounded-lg text-sm hover:shadow-lg hover:shadow-green-500/20 transition-all active:scale-95"
                >
                  ✓ All Info Collected - Proceed to Create Job
                </button>
              </div>
            )}
          </div>
        )}

        {/* Quick Actions */}
        {!isComplete && (
          <div className="px-3 sm:px-4 md:px-6 lg:px-12 xl:px-20 py-4 sm:py-5 bg-slate-900/30 border-t border-slate-800">
            <div className="max-w-3xl mx-auto flex flex-col gap-4 sm:gap-5">
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
          <div className="px-3 sm:px-4 md:px-6 py-3 sm:py-4 bg-gradient-to-r from-green-500/10 to-cyan-500/10 border-t border-green-500/30">
            <button
              onClick={handleCreateJob}
              disabled={isCreating}
              className="w-full bg-gradient-to-r from-green-500 to-cyan-600 text-white font-semibold py-3 sm:py-3.5 px-4 sm:px-6 rounded-xl text-sm sm:text-base hover:shadow-lg hover:shadow-green-500/20 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed min-h-[48px] touch-manipulation"
            >
              {isCreating ? 'Creating Job...' : '✓ Create Job on Blockchain'}
            </button>
          </div>
        )}

        {/* Chat Input */}
        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading || isRestoring}
          placeholder={isRestoring ? "Loading..." : isComplete ? "Need to change something?" : "Type your answer..."}
        />
      </div>
    </div>
  );
}
