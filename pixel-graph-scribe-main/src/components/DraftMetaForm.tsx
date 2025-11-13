import { useState } from 'react';
import { Save, Tag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { toast } from 'sonner';

export const DraftMetaForm = () => {
  const { currentGraph, currentDraft, setCurrentDraft } = useStore();
  const [title, setTitle] = useState(currentDraft?.title || '');
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>(currentDraft?.tags || []);
  const [isSaving, setIsSaving] = useState(false);
  
  const handleAddTag = () => {
    const tag = tagInput.trim().toLowerCase();
    if (tag && !tags.includes(tag)) {
      setTags([...tags, tag]);
      setTagInput('');
    }
  };
  
  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(t => t !== tagToRemove));
  };
  
  const handleSave = async () => {
    if (!title.trim()) {
      toast.error('Please enter a title');
      return;
    }
    
    if (!currentGraph?.mermaid) {
      toast.error('No diagram to save');
      return;
    }
    
    setIsSaving(true);
    
    try {
      const response = await api.saveDraft({
        draft_id: currentDraft?.id,
        title: title.trim(),
        tags,
        mermaid: currentGraph.mermaid,
      });
      
      setCurrentDraft({
        id: response.draft_id,
        title: title.trim(),
        tags,
        mermaid: currentGraph.mermaid,
      });
      
      toast.success(currentDraft?.id ? 'Draft updated' : 'Draft saved');
    } catch (error) {
      console.error('Save draft error:', error);
      toast.error('Failed to save draft');
    } finally {
      setIsSaving(false);
    }
  };
  
  if (!currentGraph) {
    return null;
  }
  
  return (
    <div className="p-4 bg-card border-2 border-border space-y-4">
      <div className="flex items-center gap-2">
        <Save className="w-5 h-5 text-primary" />
        <h3 className="font-bold">Save Draft</h3>
      </div>
      
      <div className="space-y-3">
        <div className="space-y-2">
          <Label htmlFor="title" className="text-xs">Title *</Label>
          <Input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter draft title..."
            className="border-2 focus:border-primary"
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="tags" className="text-xs">Tags</Label>
          <div className="flex gap-2">
            <Input
              id="tags"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddTag();
                }
              }}
              placeholder="Add tag..."
              className="border-2 focus:border-primary"
            />
            <Button
              type="button"
              size="sm"
              onClick={handleAddTag}
              className="px-3 bg-muted hover:bg-muted/80 border-2 border-border"
            >
              <Tag className="w-4 h-4" />
            </Button>
          </div>
          
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {tags.map((tag) => (
                <button
                  key={tag}
                  onClick={() => handleRemoveTag(tag)}
                  className="px-2 py-1 text-xs bg-primary/20 border border-primary hover:bg-destructive/20 hover:border-destructive transition-colors"
                >
                  {tag} ×
                </button>
              ))}
            </div>
          )}
        </div>
        
        <Button
          onClick={handleSave}
          disabled={isSaving || !title.trim()}
          className="w-full bg-primary hover:bg-primary/90 border-2 border-primary pixel-shadow"
        >
          {isSaving ? (
            <span className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
              Saving...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Save className="w-4 h-4" />
              {currentDraft?.id ? 'Update' : 'Save'} Draft
            </span>
          )}
        </Button>
      </div>
    </div>
  );
};
