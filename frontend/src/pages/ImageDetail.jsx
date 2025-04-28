import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { imageService } from '../services/api';
import styled from 'styled-components';
import { toast } from 'react-toastify';

const DetailContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
`;

const BackButton = styled.button`
  display: inline-flex;
  align-items: center;
  background: none;
  border: none;
  color: var(--text-light);
  font-size: 0.875rem;
  cursor: pointer;
  margin-bottom: 1rem;
  
  &:hover {
    color: var(--primary-color);
  }
`;

const DetailHeader = styled.div`
  margin-bottom: 2rem;
`;

const DetailTitle = styled.h1`
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
`;

const DetailMeta = styled.div`
  display: flex;
  gap: 1rem;
  color: var(--text-light);
  font-size: 0.875rem;
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ImageContainer = styled.div`
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  background-color: white;
`;

const ImageWrapper = styled.div`
  width: 100%;
  position: relative;
  
  img {
    width: 100%;
    display: block;
    image-orientation: from-image;
    transform: rotate(0deg);
  }
`;

const TransformationsPanel = styled.div`
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1.5rem;
`;

const PanelTitle = styled.h2`
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-color);
`;

const TransformationForm = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const TransformationSection = styled.div`
  border-top: 1px solid var(--border-color);
  padding-top: 1rem;
`;

const SectionTitle = styled.h3`
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-color);
`;

const FormGroup = styled.div`
  margin-bottom: 0.75rem;
`;

const Label = styled.label`
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: var(--text-light);
`;

const Input = styled.input`
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  background-color: white;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const Checkbox = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  input {
    width: auto;
  }
  
  label {
    margin-bottom: 0;
    font-size: 0.875rem;
  }
`;

const TransformButton = styled.button`
  width: 100%;
  padding: 0.75rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover:not(:disabled) {
    background-color: var(--primary-hover);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

const ResetButton = styled.button`
  width: 100%;
  padding: 0.75rem;
  background-color: transparent;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  margin-top: 0.75rem;
  
  &:hover {
    background-color: var(--background-color);
  }
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background-color: ${props => props.primary ? 'var(--primary-color)' : props.danger ? 'var(--error-color)' : 'white'};
  color: ${props => (props.primary || props.danger) ? 'white' : 'var(--text-color)'};
  border: 1px solid ${props => props.primary ? 'var(--primary-color)' : props.danger ? 'var(--error-color)' : 'var(--border-color)'};
  
  &:hover {
    background-color: ${props => props.primary ? 'var(--primary-hover)' : props.danger ? '#d32f2f' : 'var(--background-color)'};
  }
`;

const DeleteButton = styled.button`
  background: none;
  border: none;
  color: var(--error-color);
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  
  &:hover {
    background-color: rgba(239, 68, 68, 0.1);
  }
`;

const TransformationHistory = styled.div`
  margin-top: 2rem;
`;

const HistoryTitle = styled.h3`
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-color);
`;

const TransformationList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
`;

const TransformationItem = styled.div`
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  background-color: white;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
  }
`;

const TransformationImage = styled.div`
  width: 100%;
  height: 150px;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

const TransformationInfo = styled.div`
  padding: 0.75rem;
  font-size: 0.75rem;
  color: var(--text-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const DownloadButton = styled.button`
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  
  &:hover {
    background-color: rgba(59, 130, 246, 0.1);
  }
`;

const ImageActions = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem 0;
  color: var(--text-light);
`;

const ErrorMessage = styled.div`
  color: var(--error-color);
  padding: 1rem;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background-color: white;
  border-radius: var(--radius-lg);
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  box-shadow: var(--shadow-lg);
`;

const ModalHeader = styled.div`
  margin-bottom: 1.5rem;
`;

const ModalTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
`;

const ModalBody = styled.div`
  margin-bottom: 1.5rem;
  color: var(--text-light);
`;

const ModalFooter = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
`;

const ImageDetail = () => {
  const { imageId } = useParams();
  const navigate = useNavigate();
  
  const [image, setImage] = useState(null);
  const [transformations, setTransformations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [transforming, setTransforming] = useState(false);
  const [error, setError] = useState(null);
  const [currentImageUrl, setCurrentImageUrl] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteTransformModalOpen, setDeleteTransformModalOpen] = useState(false);
  const [transformToDelete, setTransformToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  
  // Transformation options
  const [resize, setResize] = useState({ width: '', height: '', maintain_ratio: true });
  const [crop, setCrop] = useState({ width: '', height: '', x: '', y: '' });
  const [rotate, setRotate] = useState({ angle: '' });
  const [format, setFormat] = useState({ output_format: 'jpeg', quality: '85' });
  const [filter, setFilter] = useState({ type: 'none' });
  
  useEffect(() => {
    const fetchImageDetails = async () => {
      setLoading(true);
      try {
        const imageData = await imageService.getImage(imageId);
        setImage(imageData);
        setCurrentImageUrl(imageData.original_url);
        setDownloadUrl(imageData.original_url);
        
        // Set transformations if available
        if (imageData.transformations && imageData.transformations.length > 0) {
          setTransformations(imageData.transformations);
        }
      } catch (err) {
        console.error('Failed to fetch image details:', err);
        setError('Failed to load image details. Please try again later.');
        toast.error('Failed to load image details');
      } finally {
        setLoading(false);
      }
    };
    
    fetchImageDetails();
  }, [imageId]);
  
  const handleTransform = async () => {
    // Build operations array based on form inputs
    const operations = [];
    
    if (resize.width || resize.height) {
      operations.push({
        type: 'resize',
        params: {
          width: resize.width ? parseInt(resize.width) : null,
          height: resize.height ? parseInt(resize.height) : null,
          maintain_ratio: resize.maintain_ratio
        }
      });
    }
    
    if (crop.width && crop.height) {
      operations.push({
        type: 'crop',
        params: {
          width: parseInt(crop.width),
          height: parseInt(crop.height),
          x: crop.x ? parseInt(crop.x) : 0,
          y: crop.y ? parseInt(crop.y) : 0
        }
      });
    }
    
    if (rotate.angle) {
      operations.push({
        type: 'rotate',
        params: {
          angle: parseInt(rotate.angle)
        }
      });
    }
    
    if (format.output_format && format.output_format !== 'none') {
      operations.push({
        type: 'format',
        params: {
          output_format: format.output_format,
          quality: parseInt(format.quality)
        }
      });
    }
    
    if (filter.type && filter.type !== 'none') {
      operations.push({
        type: 'filter',
        params: {
          filter_type: filter.type
        }
      });
    }
    
    if (operations.length === 0) {
      toast.warning('Please select at least one transformation operation');
      return;
    }
    
    // Ensure all operations have a params object
    operations.forEach(operation => {
      if (!operation.params) {
        operation.params = {};
      }
    });
    
    setTransforming(true);
    setError(null);
    
    try {
      const result = await imageService.transformImage(imageId, operations);
      
      // Add the new transformation to the list
      setTransformations(prev => [result, ...prev]);
      
      // Update current image to show the transformed version
      setCurrentImageUrl(result.url);
      setDownloadUrl(result.url);
      
      toast.success('Image transformed successfully!');
    } catch (err) {
      console.error('Transformation failed:', err);
      setError('Failed to transform image. Please try again.');
      toast.error('Transformation failed');
    } finally {
      setTransforming(false);
    }
  };
  
  const resetForm = () => {
    setResize({ width: '', height: '', maintain_ratio: true });
    setCrop({ width: '', height: '', x: '', y: '' });
    setRotate({ angle: '' });
    setFormat({ output_format: 'jpeg', quality: '85' });
    setFilter({ type: 'none' });
  };
  
  const handleTransformationClick = (transformation) => {
    setCurrentImageUrl(transformation.url);
    setDownloadUrl(transformation.url);
  };
  
  const handleDownload = () => {
    if (!downloadUrl) return;
    
    // Create a temporary anchor element
    const link = document.createElement('a');
    link.href = downloadUrl;
    
    // Extract filename from URL or use a default name
    const filename = downloadUrl.split('/').pop() || `transformed-image-${Date.now()}.jpg`;
    link.download = filename;
    
    // Append to body, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };
  
  const handleDeleteImage = async () => {
    setDeleting(true);
    try {
      await imageService.deleteImage(imageId);
      toast.success('Image deleted successfully');
      navigate('/');
    } catch (err) {
      console.error('Failed to delete image:', err);
      toast.error('Failed to delete image');
      setDeleting(false);
      setDeleteModalOpen(false);
    }
  };

  const handleDeleteTransformation = async () => {
    if (!transformToDelete) return;
    
    setDeleting(true);
    try {
      await imageService.deleteTransformation(transformToDelete.id);
      
      // Remove from local state
      setTransformations(prev => prev.filter(t => t.id !== transformToDelete.id));
      
      // If currently viewing the deleted transformation, switch to original
      if (currentImageUrl === transformToDelete.url) {
        setCurrentImageUrl(image.original_url);
        setDownloadUrl(image.original_url);
      }
      
      toast.success('Transformation deleted successfully');
      setDeleteTransformModalOpen(false);
      setTransformToDelete(null);
    } catch (err) {
      console.error('Failed to delete transformation:', err);
      toast.error('Failed to delete transformation');
    } finally {
      setDeleting(false);
    }
  };
  
  if (loading) {
    return <LoadingSpinner>Loading image details...</LoadingSpinner>;
  }
  
  if (!image) {
    return <div>Image not found</div>;
  }
  
  return (
    <DetailContainer>
      <BackButton onClick={() => navigate('/')}>
        ← Back to Dashboard
      </BackButton>
      
      <DetailHeader>
        <DetailTitle>{image.filename}</DetailTitle>
        <DetailMeta>
          <span>Uploaded on {formatDate(image.created_at)}</span>
          <span>•</span>
          <span>{image.width}x{image.height}</span>
        </DetailMeta>
      </DetailHeader>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <ContentGrid>
        <ImageContainer>
          <ImageWrapper>
            <img src={currentImageUrl} alt={image.filename} />
          </ImageWrapper>
          <ImageActions>
            <ActionButton onClick={handleDownload} primary>
              <span>Download Image</span>
            </ActionButton>
            <ActionButton onClick={() => {
              setCurrentImageUrl(image.original_url);
              setDownloadUrl(image.original_url);
            }}>
              <span>View Original</span>
            </ActionButton>
            <ActionButton 
              danger 
              onClick={() => setDeleteModalOpen(true)}
            >
              <span>Delete Image</span>
            </ActionButton>
          </ImageActions>
        </ImageContainer>
        
        <TransformationsPanel>
          <PanelTitle>Transform Image</PanelTitle>
          
          <TransformationForm>
            <TransformationSection>
              <SectionTitle>Resize</SectionTitle>
              <FormGroup>
                <Label htmlFor="resize-width">Width (px)</Label>
                <Input
                  id="resize-width"
                  type="number"
                  value={resize.width}
                  onChange={(e) => setResize({ ...resize, width: e.target.value })}
                  placeholder="Width in pixels"
                />
              </FormGroup>
              <FormGroup>
                <Label htmlFor="resize-height">Height (px)</Label>
                <Input
                  id="resize-height"
                  type="number"
                  value={resize.height}
                  onChange={(e) => setResize({ ...resize, height: e.target.value })}
                  placeholder="Height in pixels"
                />
              </FormGroup>
              <Checkbox>
                <input
                  id="maintain-ratio"
                  type="checkbox"
                  checked={resize.maintain_ratio}
                  onChange={(e) => setResize({ ...resize, maintain_ratio: e.target.checked })}
                />
                <label htmlFor="maintain-ratio">Maintain aspect ratio</label>
              </Checkbox>
            </TransformationSection>
            
            <TransformationSection>
              <SectionTitle>Crop</SectionTitle>
              <FormGroup>
                <Label htmlFor="crop-width">Width (px)</Label>
                <Input
                  id="crop-width"
                  type="number"
                  value={crop.width}
                  onChange={(e) => setCrop({ ...crop, width: e.target.value })}
                  placeholder="Width in pixels"
                />
              </FormGroup>
              <FormGroup>
                <Label htmlFor="crop-height">Height (px)</Label>
                <Input
                  id="crop-height"
                  type="number"
                  value={crop.height}
                  onChange={(e) => setCrop({ ...crop, height: e.target.value })}
                  placeholder="Height in pixels"
                />
              </FormGroup>
              <FormGroup>
                <Label htmlFor="crop-x">X Position (px)</Label>
                <Input
                  id="crop-x"
                  type="number"
                  value={crop.x}
                  onChange={(e) => setCrop({ ...crop, x: e.target.value })}
                  placeholder="X coordinate (default: 0)"
                />
              </FormGroup>
              <FormGroup>
                <Label htmlFor="crop-y">Y Position (px)</Label>
                <Input
                  id="crop-y"
                  type="number"
                  value={crop.y}
                  onChange={(e) => setCrop({ ...crop, y: e.target.value })}
                  placeholder="Y coordinate (default: 0)"
                />
              </FormGroup>
            </TransformationSection>
            
            <TransformationSection>
              <SectionTitle>Rotate</SectionTitle>
              <FormGroup>
                <Label htmlFor="rotate-angle">Angle (degrees)</Label>
                <Input
                  id="rotate-angle"
                  type="number"
                  value={rotate.angle}
                  onChange={(e) => setRotate({ angle: e.target.value })}
                  placeholder="Rotation angle in degrees"
                />
              </FormGroup>
            </TransformationSection>
            
            <TransformationSection>
              <SectionTitle>Format</SectionTitle>
              <FormGroup>
                <Label htmlFor="output-format">Output Format</Label>
                <Select
                  id="output-format"
                  value={format.output_format}
                  onChange={(e) => setFormat({ ...format, output_format: e.target.value })}
                >
                  <option value="none">Original format</option>
                  <option value="jpeg">JPEG</option>
                  <option value="png">PNG</option>
                  <option value="webp">WebP</option>
                  <option value="gif">GIF</option>
                </Select>
              </FormGroup>
              <FormGroup>
                <Label htmlFor="quality">Quality (1-100)</Label>
                <Input
                  id="quality"
                  type="number"
                  min="1"
                  max="100"
                  value={format.quality}
                  onChange={(e) => setFormat({ ...format, quality: e.target.value })}
                  placeholder="Quality (1-100)"
                />
              </FormGroup>
            </TransformationSection>
            
            <TransformationSection>
              <SectionTitle>Filter</SectionTitle>
              <FormGroup>
                <Label htmlFor="filter-type">Filter Type</Label>
                <Select
                  id="filter-type"
                  value={filter.type}
                  onChange={(e) => setFilter({ type: e.target.value })}
                >
                  <option value="none">None</option>
                  <option value="blur">Blur</option>
                  <option value="sharpen">Sharpen</option>
                  <option value="grayscale">Grayscale</option>
                  <option value="sepia">Sepia</option>
                  <option value="invert">Invert</option>
                </Select>
              </FormGroup>
            </TransformationSection>
            
            <TransformButton 
              onClick={handleTransform} 
              disabled={transforming}
            >
              {transforming ? 'Transforming...' : 'Apply Transformations'}
            </TransformButton>
            
            <ResetButton onClick={resetForm}>
              Reset Form
            </ResetButton>
          </TransformationForm>
        </TransformationsPanel>
      </ContentGrid>
      
      {transformations.length > 0 && (
        <TransformationHistory>
          <HistoryTitle>Transformation History</HistoryTitle>
          <TransformationList>
            {transformations.map((transformation, index) => (
              <TransformationItem 
                key={index}
                onClick={() => handleTransformationClick(transformation)}
              >
                <TransformationImage>
                  <img src={transformation.url} alt={`Transformation ${index + 1}`} />
                </TransformationImage>
                <TransformationInfo>
                  <span>{formatDate(transformation.created_at)}</span>
                  <div className="flex gap-2">
                    <DownloadButton 
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent triggering the parent onClick
                        const link = document.createElement('a');
                        link.href = transformation.url;
                        link.download = `transformed-${image.filename}`;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                      }}
                    >
                      Download
                    </DownloadButton>
                    <DeleteButton
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent triggering the parent onClick
                        setTransformToDelete(transformation);
                        setDeleteTransformModalOpen(true);
                      }}
                    >
                      Delete
                    </DeleteButton>
                  </div>
                </TransformationInfo>
              </TransformationItem>
            ))}
          </TransformationList>
        </TransformationHistory>
      )}
      
      {deleteModalOpen && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Delete Image</ModalTitle>
            </ModalHeader>
            <ModalBody>
              <p>Are you sure you want to delete this image? This action cannot be undone and will also delete all associated transformations.</p>
            </ModalBody>
            <ModalFooter>
              <ActionButton 
                onClick={() => setDeleteModalOpen(false)}
                disabled={deleting}
              >
                Cancel
              </ActionButton>
              <ActionButton 
                danger 
                onClick={handleDeleteImage}
                disabled={deleting}
              >
                {deleting ? 'Deleting...' : 'Delete'}
              </ActionButton>
            </ModalFooter>
          </ModalContent>
        </Modal>
      )}

      {deleteTransformModalOpen && transformToDelete && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Delete Transformation</ModalTitle>
            </ModalHeader>
            <ModalBody>
              <p>Are you sure you want to delete this transformation? This action cannot be undone.</p>
            </ModalBody>
            <ModalFooter>
              <ActionButton 
                onClick={() => {
                  setDeleteTransformModalOpen(false);
                  setTransformToDelete(null);
                }}
                disabled={deleting}
              >
                Cancel
              </ActionButton>
              <ActionButton 
                danger 
                onClick={handleDeleteTransformation}
                disabled={deleting}
              >
                {deleting ? 'Deleting...' : 'Delete'}
              </ActionButton>
            </ModalFooter>
          </ModalContent>
        </Modal>
      )}
    </DetailContainer>
  );
};

export default ImageDetail;
