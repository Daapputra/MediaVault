import axios from 'axios';

const API_URL = '/api';

const api = axios.create({
  baseURL: API_URL,
});

// Helper for multipart/form-data requests with progress tracking
const uploadRequest = async (endpoint, formData, onProgress) => {
  try {
    const response = await api.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || 'Server error occurred');
    }
    throw new Error('Network error. Please make sure backend is running.');
  }
};

export const compressImage = (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  return uploadRequest('/compress/image', formData, onProgress);
};

export const decompressImage = (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  return uploadRequest('/decompress/image', formData, onProgress);
};

export const embedImageMessage = (file, message, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('message', message);
  return uploadRequest('/stego/image/embed', formData, onProgress);
};

export const extractImageMessage = (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  return uploadRequest('/stego/image/extract', formData, onProgress);
};

// Generate download URL
export const getDownloadUrl = (path) => {
  if (!path) return null;
  return `${API_URL.replace('/api', '')}${path}`;
};
