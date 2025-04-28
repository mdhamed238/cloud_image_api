import axios from 'axios';

// Create an axios instance with base URL
export const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000, // 30 seconds
});

// Add a request interceptor to include the token in headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Image service functions
export const imageService = {
  // Get all images (with pagination)
  getImages: async (page = 1, limit = 10) => {
    try {
      const response = await api.get(`/images?page=${page}&limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching images:', error);
      throw error;
    }
  },

  // Get a single image by ID
  getImage: async (imageId) => {
    try {
      const response = await api.get(`/images/${imageId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching image ${imageId}:`, error);
      throw error;
    }
  },

  // Upload a new image
  uploadImage: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/images/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading image:', error);
      throw error;
    }
  },

  // Transform an image
  transformImage: async (imageId, operations) => {
    try {
      // Ensure operations are in the correct format expected by the backend
      const formattedOperations = operations.map(op => {
        // Make sure each operation has a params object
        if (!op.params) {
          op.params = {};
        }
        return op;
      });

      const response = await api.post(`/images/${imageId}/transform`, {
        operations: formattedOperations,
      });
      return response.data;
    } catch (error) {
      console.error(`Error transforming image ${imageId}:`, error);
      throw error;
    }
  },

  // Delete an image
  deleteImage: async (imageId) => {
    try {
      const response = await api.delete(`/images/${imageId}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting image ${imageId}:`, error);
      throw error;
    }
  },

  // Delete a transformation
  deleteTransformation: async (transformationId) => {
    try {
      const response = await api.delete(`/transformations/${transformationId}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting transformation ${transformationId}:`, error);
      throw error;
    }
  },
};
