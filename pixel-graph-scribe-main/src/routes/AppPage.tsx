import { TopNav } from '@/components/TopNav';
import { ChatPanel } from '@/components/ChatPanel';
import { ArtistToggle } from '@/components/ArtistToggle';
import { GraphCanvas } from '@/components/GraphCanvas';
import { VariantPanel } from '@/components/VariantPanel';
import { UploadPanel } from '@/components/UploadPanel';
import { DraftMetaForm } from '@/components/DraftMetaForm';

const AppPage = () => {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <TopNav />
      
      <div className="flex-1">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4">
          {/* Left Column - Chat */}
          <div className="flex flex-col gap-4 min-h-[calc(100vh-80px)]">
            <ArtistToggle />
            <div className="flex-1">
              <ChatPanel />
            </div>
          </div>
          
          {/* Right Column - Graph & Controls */}
          <div className="flex flex-col gap-4">
            <div className="min-h-[500px] lg:min-h-[600px]">
              <GraphCanvas />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-4">
                <VariantPanel />
              </div>
              
              <div className="space-y-4">
                <UploadPanel />
                <DraftMetaForm />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppPage;
