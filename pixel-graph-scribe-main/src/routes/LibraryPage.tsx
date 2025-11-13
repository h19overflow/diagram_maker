import { TopNav } from '@/components/TopNav';
import { DraftList } from '@/components/DraftList';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LibraryPage = () => {
  const navigate = useNavigate();
  
  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />
      
      <div className="flex-1 overflow-auto">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold mb-2">Draft Library</h1>
              <p className="text-muted-foreground">
                Manage and explore your saved diagrams
              </p>
            </div>
            
            <Button
              onClick={() => navigate('/app')}
              className="bg-primary hover:bg-primary/90 border-2 border-primary pixel-shadow"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Draft
            </Button>
          </div>
          
          <DraftList />
        </div>
      </div>
    </div>
  );
};

export default LibraryPage;
