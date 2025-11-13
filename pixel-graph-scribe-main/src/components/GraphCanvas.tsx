import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Download, Copy, Maximize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { useStore } from '@/lib/store';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#00ff7f',
    primaryTextColor: '#0b0f0c',
    primaryBorderColor: '#00e676',
    lineColor: '#00ff7f',
    secondaryColor: '#00e676',
    tertiaryColor: '#1a201c',
    background: '#0b0f0c',
    mainBkg: '#0b0f0c',
    textColor: '#e6ffe6',
  },
});

export const GraphCanvas = () => {
  const { currentGraph } = useStore();
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    if (!currentGraph?.mermaid || !containerRef.current) return;
    
    const renderDiagram = async () => {
      try {
        setError(null);
        const id = `mermaid-${Date.now()}`;
        const { svg } = await mermaid.render(id, currentGraph.mermaid);
        
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (err) {
        console.error('Mermaid render error:', err);
        setError('Failed to render diagram. Please check the syntax.');
      }
    };
    
    renderDiagram();
  }, [currentGraph?.mermaid]);
  
  const handleCopyMermaid = () => {
    if (currentGraph?.mermaid) {
      navigator.clipboard.writeText(currentGraph.mermaid);
      toast.success('Mermaid code copied to clipboard');
    }
  };
  
  const handleExportSVG = () => {
    if (!containerRef.current) return;
    
    const svg = containerRef.current.querySelector('svg');
    if (!svg) return;
    
    const svgData = new XMLSerializer().serializeToString(svg);
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'diagram.svg';
    a.click();
    
    URL.revokeObjectURL(url);
    toast.success('Diagram exported as SVG');
  };
  
  const handleExportPNG = async () => {
    if (!containerRef.current) return;
    
    const svg = containerRef.current.querySelector('svg');
    if (!svg) return;
    
    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx?.drawImage(img, 0, 0);
      
      canvas.toBlob((blob) => {
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'diagram.png';
        a.click();
        URL.revokeObjectURL(url);
        toast.success('Diagram exported as PNG');
      });
    };
    
    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
  };
  
  if (!currentGraph) {
    return (
      <div className="h-full flex items-center justify-center bg-card border-2 border-border">
        <div className="text-center space-y-6 max-w-md p-8 animate-fade-in">
          <div className="w-20 h-20 mx-auto bg-muted border-2 border-border flex items-center justify-center pixel-corners animate-scale-in">
            <Maximize2 className="w-10 h-10 text-muted-foreground animate-pulse" />
          </div>
          <div className="space-y-3">
            <h3 className="font-bold text-xl text-primary">Diagram Canvas</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Generate a diagram through chat or upload a text document to visualize it here
            </p>
          </div>
          <div className="p-4 bg-primary/5 border-2 border-primary/30 space-y-2">
            <p className="text-xs font-bold text-primary">✨ Features:</p>
            <ul className="text-xs text-muted-foreground space-y-1 text-left">
              <li>→ Export as SVG or PNG</li>
              <li>→ Copy Mermaid source code</li>
              <li>→ Generate variants with different layouts</li>
              <li>→ Built from text descriptions only</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex flex-col bg-card border-2 border-border h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-2 border-b-2 border-border bg-muted">
        <span className="text-xs font-bold px-2">DIAGRAM CANVAS</span>
        <div className="flex gap-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={handleCopyMermaid}
            className="h-8 px-2 hover:bg-card"
            title="Copy Mermaid code"
          >
            <Copy className="w-4 h-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={handleExportSVG}
            className="h-8 px-2 hover:bg-card"
            title="Export as SVG"
          >
            <Download className="w-4 h-4" />
            <span className="ml-1 text-xs hidden sm:inline">SVG</span>
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={handleExportPNG}
            className="h-8 px-2 hover:bg-card"
            title="Export as PNG"
          >
            <Download className="w-4 h-4" />
            <span className="ml-1 text-xs hidden sm:inline">PNG</span>
          </Button>
        </div>
      </div>
      
      {/* Canvas */}
      <div className="overflow-auto p-8 grid-pattern">
        {error ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="bg-destructive/10 border-2 border-destructive p-4 max-w-md">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          </div>
        ) : (
          <div 
            ref={containerRef}
            className="flex items-center justify-center w-full"
          />
        )}
      </div>
    </div>
  );
};
