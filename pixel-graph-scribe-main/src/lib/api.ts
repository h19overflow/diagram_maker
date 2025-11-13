const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:3000';

export interface ChatRequest {
  message: string;
  artist_mode?: boolean;
  context_id?: string;
}

export interface ChatResponse {
  reply: string;
  graphs?: {
    type: 'flowchart' | 'sequence' | 'concept' | 'erd' | 'timeline';
    mermaid: string;
  }[];
  sources?: any[];
}

export interface VariantRequest {
  mermaid?: string;
  draft_id?: string;
  target_type: 'flowchart' | 'sequence' | 'concept' | 'erd' | 'timeline';
  style?: 'compact' | 'spacious' | 'orthogonal';
  complexity?: 'low' | 'med' | 'high';
}

export interface VariantResponse {
  mermaid: string;
}

export interface PresignRequest {
  filename: string;
  mime: string;
}

export interface PresignResponse {
  url: string;
  method: 'PUT';
  headers?: Record<string, string>;
  key: string;
}

export interface GenerateDraftRequest {
  doc_key: string;
  views?: string[];
}

export interface GenerateDraftResponse {
  draft_id: string;
  mermaid: string;
  summary?: string;
  graph_json?: any;
}

export interface SaveDraftRequest {
  draft_id?: string;
  title: string;
  tags?: string[];
  mermaid: string;
  graph_json?: any;
}

export interface SaveDraftResponse {
  draft_id: string;
}

export interface DraftListResponse {
  items: {
    id: string;
    title: string;
    tags: string[];
    updatedAt: string;
  }[];
  total: number;
}

export interface DraftResponse {
  id: string;
  title: string;
  tags: string[];
  mermaid: string;
  graph_json?: any;
  updatedAt: string;
}

export interface ShareResponse {
  url: string;
  expiresAt: string;
}

class ApiClient {
  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async chat(payload: ChatRequest): Promise<ChatResponse> {
    // Mock response for now
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const mockGraphs = payload.artist_mode ? [{
      type: 'flowchart' as const,
      mermaid: `flowchart TD
    A[Start] --> B{Is Artist Mode On?}
    B -->|Yes| C[Generate Diagram]
    B -->|No| D[Text Response Only]
    C --> E[Render in Canvas]
    D --> F[Display in Chat]
    E --> F
    F --> G[End]`
    }] : undefined;

    return {
      reply: payload.artist_mode 
        ? `Here's a visual representation of your question: "${payload.message}"`
        : `You asked: "${payload.message}". This is a mock response. Enable Artist Mode to see diagrams!`,
      graphs: mockGraphs,
    };
  }

  async variant(payload: VariantRequest): Promise<VariantResponse> {
    // Mock response
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const mockVariants = {
      flowchart: `flowchart LR
    A[Input] --> B[Process]
    B --> C[Output]
    C --> D{Valid?}
    D -->|Yes| E[Success]
    D -->|No| F[Error]`,
      sequence: `sequenceDiagram
    participant U as User
    participant S as System
    U->>S: Request
    S->>S: Process
    S-->>U: Response`,
      concept: `graph TD
    A[Core Concept] --> B[Sub-concept 1]
    A --> C[Sub-concept 2]
    B --> D[Detail]
    C --> E[Detail]`,
      erd: `erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    PRODUCT ||--o{ LINE-ITEM : includes`,
      timeline: `timeline
    title Project Timeline
    2024-01 : Planning
    2024-02 : Development
    2024-03 : Testing
    2024-04 : Launch`
    };

    return {
      mermaid: mockVariants[payload.target_type] || mockVariants.flowchart
    };
  }

  async presign(payload: PresignRequest): Promise<PresignResponse> {
    // Mock response
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      url: 'https://mock-upload.example.com/upload',
      method: 'PUT',
      key: `uploads/${Date.now()}-${payload.filename}`,
    };
  }

  async generateDraft(payload: GenerateDraftRequest): Promise<GenerateDraftResponse> {
    // Mock response
    await new Promise(resolve => setTimeout(resolve, 2000));
    return {
      draft_id: Math.random().toString(36).substr(2, 9),
      mermaid: `flowchart TD
    A[Document Overview] --> B[Key Concepts]
    B --> C[Implementation]
    C --> D[Conclusion]
    D --> E[Next Steps]`,
      summary: 'Generated walkthrough from uploaded document',
    };
  }

  async saveDraft(payload: SaveDraftRequest): Promise<SaveDraftResponse> {
    // Mock response
    await new Promise(resolve => setTimeout(resolve, 500));
    return {
      draft_id: payload.draft_id || Math.random().toString(36).substr(2, 9),
    };
  }

  async listDrafts(params?: {
    query?: string;
    page?: number;
    pageSize?: number;
  }): Promise<DraftListResponse> {
    // Mock response
    await new Promise(resolve => setTimeout(resolve, 600));
    
    const mockDrafts = [
      {
        id: '1',
        title: 'System Architecture Overview',
        tags: ['architecture', 'system-design'],
        updatedAt: new Date(Date.now() - 86400000).toISOString(),
      },
      {
        id: '2',
        title: 'API Flow Diagram',
        tags: ['api', 'backend'],
        updatedAt: new Date(Date.now() - 172800000).toISOString(),
      },
      {
        id: '3',
        title: 'Database Schema',
        tags: ['database', 'erd'],
        updatedAt: new Date(Date.now() - 259200000).toISOString(),
      },
    ];

    return {
      items: mockDrafts.filter(d => 
        !params?.query || 
        d.title.toLowerCase().includes(params.query.toLowerCase()) ||
        d.tags.some(t => t.toLowerCase().includes(params.query!.toLowerCase()))
      ),
      total: mockDrafts.length,
    };
  }

  async getDraft(id: string): Promise<DraftResponse> {
    // Mock response
    await new Promise(resolve => setTimeout(resolve, 400));
    return {
      id,
      title: 'System Architecture Overview',
      tags: ['architecture', 'system-design'],
      mermaid: `flowchart TB
    A[Client] --> B[Load Balancer]
    B --> C[Web Server 1]
    B --> D[Web Server 2]
    C --> E[Database]
    D --> E
    E --> F[Cache Layer]`,
      updatedAt: new Date().toISOString(),
    };
  }

  async shareDraft(id: string): Promise<ShareResponse> {
    // Mock response
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      url: `https://share.example.com/draft/${id}`,
      expiresAt: new Date(Date.now() + 86400000).toISOString(),
    };
  }

  async health(): Promise<{ status: string }> {
    return this.request('/api/health');
  }
}

export const api = new ApiClient();
