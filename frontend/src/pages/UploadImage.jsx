import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { imageService } from '../services/api';
import styled from 'styled-components';
import { toast } from 'react-toastify';

const UploadContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const UploadHeader = styled.div`
  margin-bottom: 2rem;
`;

const UploadTitle = styled.h1`
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
`;

const UploadSubtitle = styled.p`
  color: var(--text-light);
  font-size: 0.875rem;
`;

const DropzoneContainer = styled.div`
  margin-bottom: 2rem;
`;

const Dropzone = styled.div`
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-lg);
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s;
  background-color: ${props => props.isDragActive ? 'rgba(59, 130, 246, 0.05)' : 'transparent'};
  border-color: ${props => props.isDragActive ? 'var(--primary-color)' : 'var(--border-color)'};
  
  &:hover {
    border-color: var(--primary-color);
    background-color: rgba(59, 130, 246, 0.05);
  }
`;

const DropzoneIcon = styled.div`
  font-size: 2rem;
  margin-bottom: 1rem;
  color: var(--text-light);
`;

const DropzoneText = styled.div`
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
`;

const DropzoneSubtext = styled.div`
  font-size: 0.875rem;
  color: var(--text-light);
`;

const PreviewContainer = styled.div`
  margin-top: 2rem;
`;

const PreviewImage = styled.div`
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  
  img {
    width: 100%;
    max-height: 400px;
    object-fit: contain;
  }
`;

const PreviewInfo = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
`;

const PreviewInfoItem = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-color);
  
  &:last-child {
    border-bottom: none;
  }
`;

const PreviewLabel = styled.span`
  font-weight: 500;
  color: var(--text-color);
`;

const PreviewValue = styled.span`
  color: var(--text-light);
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
`;

const Button = styled.button`
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

const CancelButton = styled(Button)`
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  
  &:hover:not(:disabled) {
    background-color: var(--background-color);
  }
`;

const UploadButton = styled(Button)`
  background-color: var(--primary-color);
  border: none;
  color: white;
  
  &:hover:not(:disabled) {
    background-color: var(--primary-hover);
  }
`;

const ErrorMessage = styled.div`
  color: var(--error-color);
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
`;

const UploadImage = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  
  const navigate = useNavigate();
  
  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles.length === 0) return;
    
    const selectedFile = acceptedFiles[0];
    
    // Check file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('File type not supported. Please upload a JPG, PNG, GIF, or WebP image.');
      return;
    }
    
    // Check file size (10MB max)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (selectedFile.size > maxSize) {
      setError('File is too large. Maximum size is 10MB.');
      return;
    }
    
    setFile(selectedFile);
    setError(null);
    
    // Create preview
    const objectUrl = URL.createObjectURL(selectedFile);
    setPreview(objectUrl);
    
    // Clean up preview URL when component unmounts
    return () => URL.revokeObjectURL(objectUrl);
  }, []);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/gif': ['.gif'],
      'image/webp': ['.webp']
    },
    maxFiles: 1
  });
  
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };
  
  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    setError(null);
    
    try {
      const result = await imageService.uploadImage(file);
      toast.success('Image uploaded successfully!');
      navigate(`/images/${result.id}`);
    } catch (err) {
      console.error('Upload failed:', err);
      setError('Failed to upload image. Please try again.');
      toast.error('Upload failed');
    } finally {
      setUploading(false);
    }
  };
  
  const handleCancel = () => {
    navigate('/');
  };
  
  return (
    <UploadContainer>
      <UploadHeader>
        <UploadTitle>Upload Image</UploadTitle>
        <UploadSubtitle>Upload an image to process with our cloud image API</UploadSubtitle>
      </UploadHeader>
      
      <DropzoneContainer>
        <Dropzone {...getRootProps()} isDragActive={isDragActive}>
          <input {...getInputProps()} />
          <DropzoneIcon>📁</DropzoneIcon>
          <DropzoneText>
            {isDragActive ? 'Drop the image here' : 'Drag & drop an image here, or click to select'}
          </DropzoneText>
          <DropzoneSubtext>
            Supports JPG, PNG, GIF, WebP (max 10MB)
          </DropzoneSubtext>
        </Dropzone>
      </DropzoneContainer>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      {file && preview && (
        <PreviewContainer>
          <PreviewImage>
            <img src={preview} alt="Preview" />
          </PreviewImage>
          
          <PreviewInfo>
            <PreviewInfoItem>
              <PreviewLabel>File Name</PreviewLabel>
              <PreviewValue>{file.name}</PreviewValue>
            </PreviewInfoItem>
            <PreviewInfoItem>
              <PreviewLabel>File Type</PreviewLabel>
              <PreviewValue>{file.type}</PreviewValue>
            </PreviewInfoItem>
            <PreviewInfoItem>
              <PreviewLabel>File Size</PreviewLabel>
              <PreviewValue>{formatFileSize(file.size)}</PreviewValue>
            </PreviewInfoItem>
          </PreviewInfo>
          
          <ButtonContainer>
            <CancelButton onClick={handleCancel} disabled={uploading}>
              Cancel
            </CancelButton>
            <UploadButton onClick={handleUpload} disabled={uploading}>
              {uploading ? 'Uploading...' : 'Upload Image'}
            </UploadButton>
          </ButtonContainer>
        </PreviewContainer>
      )}
    </UploadContainer>
  );
};

export default UploadImage;
