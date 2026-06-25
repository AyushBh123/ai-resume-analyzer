/**
 * File Upload Component
 * 
 * Drag-and-drop file upload with validation
 * Supports PDF and DOCX files
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, AlertCircle } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isUploading?: boolean;
  error?: string | null;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  isUploading = false,
  error = null,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setSelectedFile(file);
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled: isUploading,
  });

  const clearFile = () => {
    setSelectedFile(null);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="w-full">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
          ${selectedFile ? 'bg-green-50 border-green-500' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-4">
          {isUploading ? (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
              <p className="text-gray-600">Uploading...</p>
            </>
          ) : selectedFile ? (
            <>
              <File className="w-12 h-12 text-green-500" />
              <div>
                <p className="text-lg font-semibold text-gray-800">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  clearFile();
                }}
                className="mt-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center gap-2"
              >
                <X className="w-4 h-4" />
                Remove
              </button>
            </>
          ) : (
            <>
              <Upload className="w-12 h-12 text-gray-400" />
              <div>
                <p className="text-lg font-semibold text-gray-700">
                  {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or click to browse
                </p>
              </div>
              <div className="text-xs text-gray-400 mt-2">
                Supports PDF and DOCX files (max 10MB)
              </div>
            </>
          )}
        </div>
      </div>

      {/* File Rejection Errors */}
      {fileRejections.length > 0 && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-800">File rejected:</p>
              <ul className="mt-1 text-sm text-red-600 list-disc list-inside">
                {fileRejections[0].errors.map((error, index) => (
                  <li key={index}>
                    {error.code === 'file-too-large'
                      ? 'File is too large (max 10MB)'
                      : error.code === 'file-invalid-type'
                      ? 'Invalid file type (only PDF and DOCX allowed)'
                      : error.message}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* API Error */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-800">Upload Error:</p>
              <p className="mt-1 text-sm text-red-600">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;

// Made with Bob
