import { useState, useEffect } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { DraftCard } from './DraftCard';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';

export const DraftList = () => {
  const { draftsIndex, setDraftsIndex } = useStore();
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  useEffect(() => {
    loadDrafts();
  }, [query]);
  
  const loadDrafts = async () => {
    setIsLoading(true);
    try {
      const response = await api.listDrafts({ query, page: 1, pageSize: 20 });
      setDraftsIndex(response.items);
    } catch (error) {
      console.error('Failed to load drafts:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search drafts by title or tags..."
          className="pl-10 border-2 focus:border-primary"
        />
      </div>
      
      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-primary" />
        </div>
      )}
      
      {/* Empty state */}
      {!isLoading && draftsIndex.length === 0 && (
        <div className="text-center py-12 border-2 border-dashed border-border">
          <p className="text-muted-foreground">
            {query ? 'No drafts found matching your search' : 'No drafts yet'}
          </p>
        </div>
      )}
      
      {/* Grid */}
      {!isLoading && draftsIndex.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {draftsIndex.map((draft) => (
            <DraftCard key={draft.id} draft={draft} onUpdate={loadDrafts} />
          ))}
        </div>
      )}
    </div>
  );
};
