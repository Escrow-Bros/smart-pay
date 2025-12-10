'use client';

import { createContext, useContext, useState, ReactNode, useEffect, useRef } from 'react';
import { GlobalState, UserMode, JobDict, WorkerStats, UploadedImage } from '@/lib/types';
import { apiClient } from '@/lib/api';
import { initializePriceCache, getGasUsdPrice } from '@/lib/currency';
import toast from 'react-hot-toast';

const CLIENT_ADDR = process.env.NEXT_PUBLIC_CLIENT_ADDR || '';
const WORKER_ADDR = process.env.NEXT_PUBLIC_WORKER_ADDR || '';

const initialState: GlobalState = {
    userMode: null,
    currentUser: null,
    walletAddress: '',
    walletBalance: 0,
    isLoadingBalance: false,
    availableJobs: [],
    clientJobs: [],
    workerJobs: [],
    currentJobs: [], // Changed from currentJob: null
    workerStats: { total_jobs: 0, completed_jobs: 0, total_earned: 0 },
    isLoadingJobs: false,
    jobDescription: '',
    jobLocation: '',
    jobLatitude: 0,
    jobLongitude: 0,
    clientUploadedImages: [],
    clientIpfsUrls: [],
    isCreatingJob: false,
    creationLog: [],
    creationTxHash: '',
    creationJobId: '',
    creationProgress: 0,
    isDrafting: false,
    draftCriteria: '',
    draftMessage: '',
    draftPrice: 0,
    uploadedImage: '',
};

interface AppContextType {
    state: GlobalState;
    selectRole: (isClient: boolean) => void;
    setJobDescription: (desc: string) => void;
    setJobLocation: (loc: string, lat: number, lng: number) => void;
    addUploadedImage: (image: UploadedImage) => void;
    removeUploadedImage: (index: number) => void;
    clearUploadedImages: () => void;
    createJob: () => Promise<void>;
    claimJob: (jobId: number) => Promise<void>;
    fetchData: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
    const [state, setState] = useState<GlobalState>(initialState);
    const [isInitialized, setIsInitialized] = useState(false);

    // Restore state from localStorage on mount
    useEffect(() => {
        const savedState = localStorage.getItem('gigsmartpay_state');
        if (savedState) {
            try {
                const parsed = JSON.parse(savedState);
                setState(prev => ({
                    ...prev,
                    userMode: parsed.userMode,
                    currentUser: parsed.currentUser,
                    walletAddress: parsed.walletAddress,
                }));
            } catch (e) {
                console.error('Failed to restore state:', e);
            }
        }
        setIsInitialized(true);
    }, []);

    // Save critical state to localStorage whenever it changes
    useEffect(() => {
        if (isInitialized && state.walletAddress) {
            localStorage.setItem('gigsmartpay_state', JSON.stringify({
                userMode: state.userMode,
                currentUser: state.currentUser,
                walletAddress: state.walletAddress,
            }));
        }
    }, [state.userMode, state.currentUser, state.walletAddress, isInitialized]);

    const selectRole = (isClient: boolean) => {
        const mode: UserMode = isClient ? 'client' : 'worker';
        const user = isClient ? 'Alice' : 'Bob';
        const address = isClient ? CLIENT_ADDR : WORKER_ADDR;

        setState(prev => ({
            ...prev,
            userMode: mode,
            currentUser: user,
            walletAddress: address,
        }));
    };

    const setJobDescription = (desc: string) => {
        setState(prev => ({ ...prev, jobDescription: desc }));
    };

    const setJobLocation = (loc: string, lat: number, lng: number) => {
        setState(prev => ({
            ...prev,
            jobLocation: loc,
            jobLatitude: lat,
            jobLongitude: lng,
        }));
    };

    const addUploadedImage = (image: UploadedImage) => {
        setState(prev => ({
            ...prev,
            clientUploadedImages: [...prev.clientUploadedImages, image],
        }));
    };

    const removeUploadedImage = (index: number) => {
        setState(prev => ({
            ...prev,
            clientUploadedImages: prev.clientUploadedImages.filter((_, i) => i !== index),
        }));
    };

    const clearUploadedImages = () => {
        setState(prev => ({
            ...prev,
            clientUploadedImages: [],
        }));
    };

    const createJob = async () => {
        // Implementation will be in the component
    };

    const claimJob = async (jobId: number) => {
        if (!state.walletAddress) return;

        try {
            await apiClient.assignJob(jobId, state.walletAddress);
            await fetchData();
        } catch (error) {
            console.error('Error claiming job:', error);
        }
    };

    const fetchData = async () => {
        if (!state.walletAddress) return;

        try {
            // Fetch balance
            const balance = await apiClient.getWalletBalance(state.walletAddress);
            setState(prev => ({ ...prev, walletBalance: balance }));

            // Fetch jobs based on mode
            if (state.userMode === 'client') {
                const data = await apiClient.getClientJobs(state.walletAddress);
                setState(prev => ({ ...prev, clientJobs: data.jobs || [] }));
            } else {
                const [availData, activeData, historyData, statsData] = await Promise.all([
                    apiClient.getAvailableJobs(),
                    apiClient.getWorkerCurrentJobs(state.walletAddress),
                    apiClient.getWorkerHistory(state.walletAddress),
                    apiClient.getWorkerStats(state.walletAddress),
                ]);
                setState(prev => ({
                    ...prev,
                    availableJobs: availData.jobs || [],
                    workerJobs: historyData.jobs || [],
                    currentJobs: activeData.jobs || [],
                    workerStats: statsData || prev.workerStats,
                }));
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    // Auto-fetch data when wallet changes or after restoration
    useEffect(() => {
        if (state.walletAddress && state.userMode && isInitialized) {
            fetchData();
        }
    }, [state.walletAddress, state.userMode, isInitialized]);

    // Global WebSocket connection for real-time updates with auto-reconnect
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const reconnectAttemptsRef = useRef(0);
    const maxReconnectAttempts = 10;
    const isIntentionalClose = useRef(false);
    
    useEffect(() => {
        if (!state.walletAddress) return;

        const wsProtocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const wsUrl = apiUrl.replace(/^https?:/, wsProtocol);

        const connectWebSocket = () => {
            // Don't reconnect if intentionally closing or max attempts reached
            if (isIntentionalClose.current || reconnectAttemptsRef.current >= maxReconnectAttempts) {
                return;
            }

            try {
                const ws = new WebSocket(`${wsUrl}/ws/${state.walletAddress}`);
                
                // Set connection timeout (30 seconds)
                const connectionTimeout = setTimeout(() => {
                    if (ws.readyState !== WebSocket.OPEN) {
                        console.warn('⚠️ WebSocket connection timeout');
                        ws.close();
                    }
                }, 30000);
                
                ws.onopen = () => {
                    clearTimeout(connectionTimeout);
                    console.log('🔌 WebSocket connected globally');
                    reconnectAttemptsRef.current = 0; // Reset on successful connection
                };
                
                ws.onmessage = (event) => {
                    let data;
                    try {
                        data = JSON.parse(event.data);
                    } catch (e) {
                        console.error('Failed to parse WebSocket message:', e);
                        return;
                    }
                    console.log('📨 WebSocket message:', data);
                    
                    // Handle different event types
                    if (data.type === 'JOB_COMPLETED') {
                        toast.dismiss(`job-${data.job_id}`);
                        toast.success(`🎉 Job #${data.job_id} completed! Payment confirmed on blockchain.`, {
                            duration: 5000,
                            position: 'top-right',
                        });
                        // Auto-refresh data to update UI
                        fetchData();
                    } else if (data.type === 'PAYMENT_PENDING') {
                        toast.loading(`⏳ Job #${data.job_id} payment pending confirmation...`, {
                            id: `job-${data.job_id}`,
                            duration: 15000,
                        });
                    } else if (data.type === 'PAYMENT_TIMEOUT') {
                        toast.dismiss(`job-${data.job_id}`);
                        toast(`⚠️ Job #${data.job_id}: ${data.message}`, {
                            duration: 8000,
                            icon: '⏱️',
                        });
                    } else if (data.type === 'JOB_STATUS_UPDATE') {
                        toast.dismiss(`job-${data.job_id}`);
                        toast(`📋 Job #${data.job_id}: ${data.message}`, {
                            duration: 4000,
                            icon: 'ℹ️',
                        });
                        // Auto-refresh data to update UI
                        fetchData();
                    } else if (data.type === 'DISPUTE_RAISED') {
                        toast(`⚖️ Dispute raised on Job #${data.job_id}`, {
                            duration: 6000,
                            icon: '⚠️',
                        });
                        fetchData();
                    } else if (data.type === 'DISPUTE_RESOLVED') {
                        toast.success(`✅ Dispute resolved for Job #${data.job_id}`, {
                            duration: 5000,
                        });
                        fetchData();
                    }
                };
                
                ws.onerror = (error) => {
                    clearTimeout(connectionTimeout);
                    console.error('❌ WebSocket error:', error);
                    // Don't show error toast on every reconnect attempt
                    if (reconnectAttemptsRef.current === 0) {
                        toast.error('Connection to real-time updates failed. Retrying...', {
                            duration: 3000,
                        });
                    }
                };
                
                ws.onclose = (event) => {
                    clearTimeout(connectionTimeout);
                    console.log('🔌 WebSocket disconnected', event.code, event.reason);
                    
                    // Don't reconnect if this was an intentional close
                    if (isIntentionalClose.current) {
                        return;
                    }
                    
                    // Attempt reconnection with exponential backoff
                    reconnectAttemptsRef.current += 1;
                    
                    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
                        console.error('❌ Max WebSocket reconnection attempts reached');
                        toast.error('Unable to establish real-time connection. Please refresh the page.', {
                            duration: 8000,
                        });
                        return;
                    }
                    
                    // Exponential backoff: 1s, 2s, 4s, 8s, 16s, max 30s
                    const backoffDelay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current - 1), 30000);
                    console.log(`🔄 Reconnecting in ${backoffDelay / 1000}s... (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
                    
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connectWebSocket();
                    }, backoffDelay);
                };
                
                wsRef.current = ws;
            } catch (error) {
                console.error('Failed to create WebSocket:', error);
                // Graceful degradation - app still works without WebSocket
                toast.error('Real-time updates unavailable. You can still use the app.', {
                    duration: 5000,
                });
            }
        };

        // Initial connection
        isIntentionalClose.current = false;
        connectWebSocket();
        
        // Cleanup on unmount or wallet change
        return () => {
            isIntentionalClose.current = true;
            
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [state.walletAddress]);

    // Initialize GAS/USD price cache on mount and refresh periodically
    useEffect(() => {
        // Initial fetch with error handling
        initializePriceCache().catch(error => {
            console.error('Failed to initialize price cache:', error);
        });
        
        // Refresh price every 5 minutes
        const interval = setInterval(() => {
            getGasUsdPrice().catch(error => {
                console.error('Failed to refresh GAS price:', error);
            });
        }, 5 * 60 * 1000);
        
        return () => clearInterval(interval);
    }, []);

    return (
        <AppContext.Provider
            value={{
                state,
                selectRole,
                setJobDescription,
                setJobLocation,
                addUploadedImage,
                removeUploadedImage,
                clearUploadedImages,
                createJob,
                claimJob,
                fetchData,
            }}
        >
            {children}
        </AppContext.Provider>
    );
}

export function useApp() {
    const context = useContext(AppContext);
    if (!context) throw new Error('useApp must be used within AppProvider');
    return context;
}
