'use client';

import { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { GlobalState, UserMode, JobDict, WorkerStats, UploadedImage } from '@/lib/types';
import { apiClient } from '@/lib/api';
import { getGasUsdPrice } from '@/lib/currency';

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

    // Fetch GAS/USD price on mount and periodically
    useEffect(() => {
        // Initial fetch
        getGasUsdPrice();
        
        // Refresh price every 5 minutes
        const interval = setInterval(() => {
            getGasUsdPrice();
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
