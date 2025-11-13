import { Paintbrush } from 'lucide-react';
import { useStore } from '@/lib/store';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

export const ArtistToggle = () => {
  const { artistMode, setArtistMode } = useStore();
  
  return (
    <div className="flex items-center justify-between p-4 bg-card border-2 border-border pixel-shadow">
      <div className="flex items-center gap-2">
        <Paintbrush className="w-5 h-5 text-primary" />
        <Label htmlFor="artist-mode" className="font-bold cursor-pointer">
          Artist Mode
        </Label>
      </div>
      
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div>
              <Switch
                id="artist-mode"
                checked={artistMode}
                onCheckedChange={setArtistMode}
              />
            </div>
          </TooltipTrigger>
          <TooltipContent className="max-w-xs border-2 border-border bg-popover">
            <p className="text-sm">
              When enabled, the assistant will generate visual diagrams alongside text responses.
              Perfect for understanding complex concepts!
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  );
};
