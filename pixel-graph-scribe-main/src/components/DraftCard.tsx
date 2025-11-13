import { FileText, Share2, Trash2, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { DraftSummary } from '@/lib/store';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/api';
import { toast } from 'sonner';

interface DraftCardProps {
  draft: DraftSummary;
  onUpdate: () => void;
}

export const DraftCard = ({ draft, onUpdate }: DraftCardProps) => {
  const navigate = useNavigate();
  
  const handleShare = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const response = await api.shareDraft(draft.id);
      await navigator.clipboard.writeText(response.url);
      toast.success('Share link copied to clipboard');
    } catch (error) {
      toast.error('Failed to generate share link');
    }
  };
  
  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this draft?')) return;
    
    // Mock delete
    toast.success('Draft deleted');
    onUpdate();
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };
  
  return (
    <div
      onClick={() => navigate(`/draft/${draft.id}`)}
      className="group p-4 bg-card border-2 border-border hover:border-primary transition-all cursor-pointer pixel-shadow hover:translate-x-0.5 hover:translate-y-0.5"
    >
      <div className="flex items-start gap-3 mb-3">
        <div className="w-10 h-10 bg-primary/10 border-2 border-primary flex items-center justify-center flex-shrink-0 pixel-corners">
          <FileText className="w-5 h-5 text-primary" />
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-sm mb-1 truncate group-hover:text-primary transition-colors">
            {draft.title}
          </h3>
          <p className="text-xs text-muted-foreground">
            {formatDate(draft.updatedAt)}
          </p>
        </div>
      </div>
      
      {draft.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {draft.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 text-xs bg-muted border border-border"
            >
              {tag}
            </span>
          ))}
          {draft.tags.length > 3 && (
            <span className="px-2 py-0.5 text-xs text-muted-foreground">
              +{draft.tags.length - 3}
            </span>
          )}
        </div>
      )}
      
      <div className="flex gap-1">
        <Button
          size="sm"
          variant="ghost"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/draft/${draft.id}`);
          }}
          className="flex-1 h-8 hover:bg-muted"
        >
          <ExternalLink className="w-3 h-3 mr-1" />
          Open
        </Button>
        
        <Button
          size="sm"
          variant="ghost"
          onClick={handleShare}
          className="h-8 px-2 hover:bg-muted"
        >
          <Share2 className="w-3 h-3" />
        </Button>
        
        <Button
          size="sm"
          variant="ghost"
          onClick={handleDelete}
          className="h-8 px-2 hover:bg-destructive hover:text-destructive-foreground"
        >
          <Trash2 className="w-3 h-3" />
        </Button>
      </div>
    </div>
  );
};
