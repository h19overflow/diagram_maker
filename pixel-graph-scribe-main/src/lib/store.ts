import { create } from 'zustand';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  graphs?: { type: string; mermaid: string }[];
  timestamp: Date;
}

export interface Draft {
  id?: string;
  title: string;
  tags: string[];
  mermaid: string;
  graphJson?: any;
  updatedAt?: string;
}

export interface DraftSummary {
  id: string;
  title: string;
  tags: string[];
  updatedAt: string;
}

export interface UploadItem {
  id: string;
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error';
  key?: string;
}

interface AppState {
  artistMode: boolean;
  messages: Message[];
  currentGraph: { mermaid: string; svg?: string; meta?: any } | null;
  uploadQueue: UploadItem[];
  currentDraft: Draft | null;
  draftsIndex: DraftSummary[];
  
  setArtistMode: (mode: boolean) => void;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setCurrentGraph: (graph: { mermaid: string; svg?: string; meta?: any } | null) => void;
  addUpload: (file: File) => string;
  updateUpload: (id: string, updates: Partial<UploadItem>) => void;
  removeUpload: (id: string) => void;
  setCurrentDraft: (draft: Draft | null) => void;
  setDraftsIndex: (drafts: DraftSummary[]) => void;
}

export const useStore = create<AppState>((set) => ({
  artistMode: false,
  messages: [],
  currentGraph: null,
  uploadQueue: [],
  currentDraft: null,
  draftsIndex: [],
  
  setArtistMode: (mode) => set({ artistMode: mode }),
  
  addMessage: (message) => 
    set((state) => ({ messages: [...state.messages, message] })),
  
  clearMessages: () => set({ messages: [] }),
  
  setCurrentGraph: (graph) => set({ currentGraph: graph }),
  
  addUpload: (file) => {
    const id = Math.random().toString(36).substr(2, 9);
    set((state) => ({
      uploadQueue: [
        ...state.uploadQueue,
        { id, file, progress: 0, status: 'pending' }
      ]
    }));
    return id;
  },
  
  updateUpload: (id, updates) =>
    set((state) => ({
      uploadQueue: state.uploadQueue.map((item) =>
        item.id === id ? { ...item, ...updates } : item
      )
    })),
  
  removeUpload: (id) =>
    set((state) => ({
      uploadQueue: state.uploadQueue.filter((item) => item.id !== id)
    })),
  
  setCurrentDraft: (draft) => set({ currentDraft: draft }),
  
  setDraftsIndex: (drafts) => set({ draftsIndex: drafts }),
}));
