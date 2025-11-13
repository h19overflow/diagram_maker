import { useRef, useState } from 'react';
import { Upload, FileText, X, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import { toast } from 'sonner';

export const UploadPanel = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const { uploadQueue, addUpload, updateUpload, removeUpload, setCurrentGraph } = useStore();
  
  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;
    
    Array.from(files).forEach(async (file) => {
      // Validate file type
      if (!file.type.includes('pdf') && !file.type.includes('markdown') && !file.name.endsWith('.md')) {
        toast.error(`${file.name}: Only PDF and Markdown files are supported`);
        return;
      }
      
      // Validate file size (max 20MB)
      if (file.size > 20 * 1024 * 1024) {
        toast.error(`${file.name}: File size exceeds 20MB`);
        return;
      }
      
      const uploadId = addUpload(file);
      
      try {
        // Get presigned URL
        updateUpload(uploadId, { status: 'uploading', progress: 10 });
        const presignResponse = await api.presign({
          filename: file.name,
          mime: file.type,
        });
        
        // Upload file
        updateUpload(uploadId, { progress: 30 });
        await fetch(presignResponse.url, {
          method: presignResponse.method,
          headers: presignResponse.headers || {},
          body: file,
        });
        
        updateUpload(uploadId, { 
          status: 'processing',
          progress: 70,
          key: presignResponse.key 
        });
        
        // We'll generate draft on user action, not automatically
        updateUpload(uploadId, { status: 'complete', progress: 100 });
        toast.success(`${file.name} uploaded successfully`);
        
      } catch (error) {
        console.error('Upload error:', error);
        updateUpload(uploadId, { status: 'error' });
        toast.error(`Failed to upload ${file.name}`);
      }
    });
  };
  
  const handleGenerateDraft = async (uploadId: string) => {
    const upload = uploadQueue.find(u => u.id === uploadId);
    if (!upload?.key) return;
    
    updateUpload(uploadId, { status: 'processing', progress: 80 });
    
    try {
      const response = await api.generateDraft({
        doc_key: upload.key,
        views: ['flowchart', 'concept'],
      });
      
      setCurrentGraph({ mermaid: response.mermaid });
      toast.success('Walkthrough generated!');
      removeUpload(uploadId);
    } catch (error) {
      console.error('Generate draft error:', error);
      updateUpload(uploadId, { status: 'error' });
      toast.error('Failed to generate walkthrough');
    }
  };
  
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(false);
  };
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };
  
  return (
    <div className="p-4 bg-card border-2 border-border space-y-4 animate-fade-in">
      <div className="flex items-center gap-2">
        <Upload className="w-5 h-5 text-primary" />
        <h3 className="font-bold">Upload Document</h3>
      </div>
      
      <div className="p-3 bg-primary/5 border border-primary/30 space-y-1">
        <p className="text-xs font-bold text-primary">📝 Text Content Only</p>
        <p className="text-xs text-muted-foreground">
          Only text will be extracted and converted to diagrams. Images in documents are ignored.
        </p>
      </div>
      
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed p-6 text-center transition-all duration-300 cursor-pointer
          ${isDragging ? 'border-primary bg-primary/10 scale-105' : 'border-border hover:border-primary hover:bg-primary/5'}
        `}
        onClick={() => fileInputRef.current?.click()}
      >
        <FileText className={`w-8 h-8 mx-auto mb-2 transition-transform ${isDragging ? 'scale-110 text-primary' : 'text-muted-foreground'}`} />
        <p className="text-sm mb-1 font-medium">Drop files here or click to browse</p>
        <p className="text-xs text-muted-foreground">PDF or Markdown (max 20MB)</p>
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.md,.markdown"
          multiple
          className="hidden"
          onChange={(e) => handleFileSelect(e.target.files)}
        />
      </div>
      
      {uploadQueue.length > 0 && (
        <div className="space-y-2">
          {uploadQueue.map((upload) => (
            <div
              key={upload.id}
              className="p-3 bg-muted border border-border space-y-2"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{upload.file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(upload.file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
                
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => removeUpload(upload.id)}
                  className="h-6 w-6 p-0"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              
              {upload.status !== 'error' && upload.status !== 'complete' && (
                <div className="space-y-1">
                  <div className="h-1 bg-background overflow-hidden">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{ width: `${upload.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground capitalize">
                    {upload.status}... {upload.progress}%
                  </p>
                </div>
              )}
              
              {upload.status === 'complete' && (
                <Button
                  size="sm"
                  onClick={() => handleGenerateDraft(upload.id)}
                  className="w-full bg-primary hover:bg-primary/90 border-2 border-primary pixel-shadow h-8"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Generate Walkthrough
                </Button>
              )}
              
              {upload.status === 'error' && (
                <p className="text-xs text-destructive">Upload failed</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
