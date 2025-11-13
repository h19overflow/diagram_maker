import { useState } from 'react';
import { Wand2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { toast } from 'sonner';

export const VariantPanel = () => {
  const { currentGraph, setCurrentGraph } = useStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [targetType, setTargetType] = useState<string>('flowchart');
  const [style, setStyle] = useState<string>('compact');
  const [complexity, setComplexity] = useState<string>('med');
  
  const handleGenerate = async () => {
    if (!currentGraph?.mermaid) {
      toast.error('No diagram to generate variants from');
      return;
    }
    
    setIsGenerating(true);
    
    try {
      const response = await api.variant({
        mermaid: currentGraph.mermaid,
        target_type: targetType as any,
        style: style as any,
        complexity: complexity as any,
      });
      
      setCurrentGraph({ mermaid: response.mermaid });
      toast.success('Variant generated successfully');
    } catch (error) {
      toast.error('Failed to generate variant');
      console.error('Variant generation error:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  if (!currentGraph) {
    return null;
  }
  
  return (
    <div className="p-4 bg-card border-2 border-border space-y-4">
      <div className="flex items-center gap-2">
        <Wand2 className="w-5 h-5 text-primary" />
        <h3 className="font-bold">Generate Variant</h3>
      </div>
      
      <div className="space-y-3">
        <div className="space-y-2">
          <Label htmlFor="type" className="text-xs">Diagram Type</Label>
          <Select value={targetType} onValueChange={setTargetType}>
            <SelectTrigger id="type" className="border-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="flowchart">Flowchart</SelectItem>
              <SelectItem value="sequence">Sequence</SelectItem>
              <SelectItem value="concept">Concept Map</SelectItem>
              <SelectItem value="erd">ERD</SelectItem>
              <SelectItem value="timeline">Timeline</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="style" className="text-xs">Layout Style</Label>
          <Select value={style} onValueChange={setStyle}>
            <SelectTrigger id="style" className="border-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="compact">Compact</SelectItem>
              <SelectItem value="spacious">Spacious</SelectItem>
              <SelectItem value="orthogonal">Orthogonal</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="complexity" className="text-xs">Complexity</Label>
          <Select value={complexity} onValueChange={setComplexity}>
            <SelectTrigger id="complexity" className="border-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="low">Low</SelectItem>
              <SelectItem value="med">Medium</SelectItem>
              <SelectItem value="high">High</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <Button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="w-full bg-primary hover:bg-primary/90 border-2 border-primary pixel-shadow"
        >
          {isGenerating ? (
            <span className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
              Generating...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Wand2 className="w-4 h-4" />
              Generate
            </span>
          )}
        </Button>
      </div>
    </div>
  );
};
