import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TopNav } from '@/components/TopNav';
import { GraphCanvas } from '@/components/GraphCanvas';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Share2, Copy, Download } from 'lucide-react';
import { api, DraftResponse } from '@/lib/api';
import { useStore } from '@/lib/store';
import { toast } from 'sonner';

const DraftPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { setCurrentGraph } = useStore();
  const [draft, setDraft] = useState<DraftResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    if (!id) return;
    
    const loadDraft = async () => {
      try {
        const response = await api.getDraft(id);
        setDraft(response);
        setCurrentGraph({ mermaid: response.mermaid });
      } catch (error) {
        toast.error('Failed to load draft');
        console.error('Load draft error:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadDraft();
  }, [id, setCurrentGraph]);
  
  const handleShare = async () => {
    if (!id) return;
    try {
      const response = await api.shareDraft(id);
      await navigator.clipboard.writeText(response.url);
      toast.success('Share link copied to clipboard');
    } catch (error) {
      toast.error('Failed to generate share link');
    }
  };
  
  const handleCopyMermaid = () => {
    if (draft?.mermaid) {
      navigator.clipboard.writeText(draft.mermaid);
      toast.success('Mermaid code copied');
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex flex-col h-screen bg-background">
        <TopNav />
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent animate-spin"></div>
            <p className="text-muted-foreground">Loading draft...</p>
          </div>
        </div>
      </div>
    );
  }
  
  if (!draft) {
    return (
      <div className="flex flex-col h-screen bg-background">
        <TopNav />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-4">
            <p className="text-muted-foreground">Draft not found</p>
            <Button onClick={() => navigate('/library')}>
              Back to Library
            </Button>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />
      
      <div className="flex-1 overflow-hidden">
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="border-b-2 border-border bg-card p-4">
            <div className="container mx-auto flex items-center justify-between gap-4">
              <div className="flex items-center gap-4 min-w-0">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate('/library')}
                  className="flex-shrink-0 hover:bg-muted"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back
                </Button>
                
                <div className="min-w-0">
                  <h1 className="text-xl font-bold truncate">{draft.title}</h1>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {draft.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 text-xs bg-muted border border-border"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="flex gap-2 flex-shrink-0">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleCopyMermaid}
                  className="hover:bg-muted"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  <span className="hidden sm:inline">Copy Code</span>
                </Button>
                
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleShare}
                  className="hover:bg-muted"
                >
                  <Share2 className="w-4 h-4 mr-2" />
                  <span className="hidden sm:inline">Share</span>
                </Button>
              </div>
            </div>
          </div>
          
          {/* Canvas */}
          <div className="flex-1 overflow-hidden p-4">
            <GraphCanvas />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DraftPage;
