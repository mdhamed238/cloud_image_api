import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { imageService } from '../services/api';
import styled from 'styled-components';
import { toast } from 'react-toastify';

const DashboardContainer = styled.div`
  padding: 1rem 0;
`;

const DashboardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
`;

const DashboardTitle = styled.h1`
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
`;

const UploadButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  background-color: var(--primary-color);
  color: white;
  border-radius: var(--radius-md);
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: var(--primary-hover);
    text-decoration: none;
  }
`;

const ImagesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
`;

const ImageCard = styled.div`
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-md);
  }
`;

const ImagePreview = styled.div`
  width: 100%;
  height: 200px;
  overflow: hidden;
  position: relative;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
  }
  
  &:hover img {
    transform: scale(1.05);
  }
`;

const ImageInfo = styled.div`
  padding: 1rem;
`;

const ImageName = styled.h3`
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ImageMeta = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-light);
`;

const NoImages = styled.div`
  text-align: center;
  padding: 3rem 0;
  color: var(--text-light);
`;

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  margin-top: 2rem;
  gap: 0.5rem;
`;

const PageButton = styled.button`
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  background-color: ${props => props.active ? 'var(--primary-color)' : 'white'};
  color: ${props => props.active ? 'white' : 'var(--text-color)'};
  border-radius: var(--radius-md);
  cursor: pointer;
  
  &:hover {
    background-color: ${props => props.active ? 'var(--primary-hover)' : 'var(--background-color)'};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem 0;
  color: var(--text-light);
`;

const Dashboard = () => {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [limit] = useState(12);
  
  useEffect(() => {
    const fetchImages = async () => {
      setLoading(true);
      try {
        const data = await imageService.getImages(page, limit);
        setImages(data.items);
        setTotalPages(Math.ceil(data.total / limit));
      } catch (err) {
        console.error('Failed to fetch images:', err);
        setError('Failed to load images. Please try again later.');
        toast.error('Failed to load images');
      } finally {
        setLoading(false);
      }
    };
    
    fetchImages();
  }, [page, limit]);
  
  const handlePageChange = (newPage) => {
    setPage(newPage);
    window.scrollTo(0, 0);
  };
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };
  
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };
  
  if (loading && page === 1) {
    return <LoadingSpinner>Loading images...</LoadingSpinner>;
  }
  
  return (
    <DashboardContainer>
      <DashboardHeader>
        <DashboardTitle>Your Images</DashboardTitle>
        <UploadButton to="/upload">Upload New Image</UploadButton>
      </DashboardHeader>
      
      {error && <div className="error-message">{error}</div>}
      
      {!loading && images.length === 0 ? (
        <NoImages>
          <p>You haven't uploaded any images yet.</p>
          <Link to="/upload" className="button button-primary mt-4">Upload your first image</Link>
        </NoImages>
      ) : (
        <>
          <ImagesGrid>
            {images.map((image) => (
              <ImageCard key={image.id}>
                <Link to={`/images/${image.id}`}>
                  <ImagePreview>
                    <img src={image.original_url} alt={image.filename} />
                  </ImagePreview>
                  <ImageInfo>
                    <ImageName>{image.filename}</ImageName>
                    <ImageMeta>
                      <span>{formatDate(image.created_at)}</span>
                      <span>{formatFileSize(image.size)}</span>
                    </ImageMeta>
                  </ImageInfo>
                </Link>
              </ImageCard>
            ))}
          </ImagesGrid>
          
          {totalPages > 1 && (
            <Pagination>
              <PageButton 
                onClick={() => handlePageChange(page - 1)} 
                disabled={page === 1}
              >
                Previous
              </PageButton>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(p => p === 1 || p === totalPages || (p >= page - 1 && p <= page + 1))
                .map((p, i, arr) => (
                  <React.Fragment key={p}>
                    {i > 0 && arr[i - 1] !== p - 1 && (
                      <span>...</span>
                    )}
                    <PageButton 
                      active={p === page}
                      onClick={() => handlePageChange(p)}
                    >
                      {p}
                    </PageButton>
                  </React.Fragment>
                ))
              }
              
              <PageButton 
                onClick={() => handlePageChange(page + 1)} 
                disabled={page === totalPages}
              >
                Next
              </PageButton>
            </Pagination>
          )}
        </>
      )}
    </DashboardContainer>
  );
};

export default Dashboard;
